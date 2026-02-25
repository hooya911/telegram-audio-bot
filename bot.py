#!/usr/bin/env python3
"""
Telegram Audio Converter Bot
- Converts any audio format to MP3
- Transcribes audio using Gemini AI (Farsi + English)
"""

import os
import logging
import tempfile
import asyncio
from functools import partial
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from pydub import AudioSegment

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Supported audio formats (sent as documents)
SUPPORTED_FORMATS = ['.m4a', '.ogg', '.opus', '.wav', '.aac', '.flac', '.wma', '.mp3']


async def transcribe_with_gemini(mp3_path: str) -> str:
    """Upload MP3 to Gemini and transcribe Farsi+English audio"""
    import google.generativeai as genai
    import time

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")

    genai.configure(api_key=api_key)
    loop = asyncio.get_event_loop()

    # Step 1: Upload file to Gemini Files API
    logger.info("Uploading file to Gemini Files API...")

    def upload_file():
        return genai.upload_file(mp3_path, mime_type="audio/mpeg")

    audio_file = await loop.run_in_executor(None, upload_file)
    logger.info(f"File uploaded: {audio_file.name}, state: {audio_file.state.name}")

    # Step 2: Wait for Gemini to process the file
    def wait_for_processing(f):
        attempts = 0
        while f.state.name == "PROCESSING" and attempts < 30:
            time.sleep(3)
            f = genai.get_file(f.name)
            attempts += 1
            logger.info(f"File state: {f.state.name} (attempt {attempts})")
        return f

    audio_file = await loop.run_in_executor(None, partial(wait_for_processing, audio_file))

    if audio_file.state.name == "FAILED":
        raise Exception("Gemini failed to process the audio file")

    # Step 3: Transcribe
    logger.info("Sending to Gemini for transcription...")

    model = genai.GenerativeModel('gemini-1.5-pro')

    prompt = """Please transcribe this audio file exactly as spoken.

Important instructions:
- The audio contains a mix of Farsi (Persian) and English
- Write Farsi words in Persian script (فارسی) — do NOT romanize
- Write English words in English
- Do NOT translate anything — transcribe exactly what is said
- Keep the original language of each word/sentence
- Add a timestamp every ~2 minutes like [0:00], [2:00], [4:00] etc.
- If there are multiple speakers, indicate with Speaker 1:, Speaker 2: etc. if noticeable

Transcribe now:"""

    def do_transcribe():
        response = model.generate_content(
            [prompt, audio_file],
            request_options={"timeout": 300}  # 5 min timeout
        )
        return response.text

    transcription = await loop.run_in_executor(None, do_transcribe)

    # Step 4: Cleanup — delete uploaded file from Gemini
    def cleanup():
        try:
            genai.delete_file(audio_file.name)
            logger.info(f"Deleted Gemini file: {audio_file.name}")
        except Exception as e:
            logger.warning(f"Could not delete Gemini file: {e}")

    await loop.run_in_executor(None, cleanup)

    return transcription


async def send_transcription(message, transcription: str, duration_mins: float):
    """Send transcription text to Telegram, splitting if needed (4096 char limit)"""
    TELEGRAM_LIMIT = 4000  # Leave some buffer below 4096

    header = f"📝 *Transcription* — ⏱ {duration_mins:.1f} min\n{'━' * 28}\n\n"
    full_text = header + transcription

    if len(full_text) <= TELEGRAM_LIMIT:
        await message.reply_text(full_text, parse_mode='Markdown')
    else:
        # Split into multiple messages
        chunks = []
        remaining = transcription
        while remaining:
            chunks.append(remaining[:TELEGRAM_LIMIT - 100])
            remaining = remaining[TELEGRAM_LIMIT - 100:]

        total = len(chunks)
        for i, chunk in enumerate(chunks, 1):
            part_header = f"📝 *Transcription {i}/{total}*\n{'━' * 28}\n\n"
            await message.reply_text(part_header + chunk, parse_mode='Markdown')

    logger.info(f"✅ Transcription sent ({len(transcription)} characters)")


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming audio/voice messages — convert to MP3 then transcribe"""
    message = update.message

    # Identify the audio file
    audio_file = None
    original_filename = "voice_memo"

    if message.voice:
        audio_file = message.voice
        original_filename = f"voice_{message.voice.file_unique_id}"
    elif message.audio:
        audio_file = message.audio
        original_filename = message.audio.file_name or f"audio_{message.audio.file_unique_id}"
    elif message.document:
        file_ext = os.path.splitext(message.document.file_name)[1].lower()
        if file_ext in SUPPORTED_FORMATS:
            audio_file = message.document
            original_filename = message.document.file_name

    if not audio_file:
        return

    status_message = await message.reply_text("🎵 Converting to MP3...")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:

            # ── Download ──────────────────────────────────────────────────
            try:
                file = await audio_file.get_file()
                input_path = os.path.join(temp_dir, "input_audio")
                await file.download_to_drive(input_path)
                logger.info("Downloaded file successfully")
            except Exception as download_error:
                error_msg = str(download_error)
                if "413" in error_msg or "too large" in error_msg.lower():
                    await status_message.edit_text(
                        "⚠️ File too large for Telegram API (13+ MB)\n\n"
                        "💡 Workaround:\n"
                        "1. Save the voice message to Files\n"
                        "2. Send it as a document (not voice message)\n"
                        "3. Bot will convert it!"
                    )
                else:
                    await status_message.edit_text(f"❌ Download failed: {error_msg}")
                logger.error(f"Download error: {download_error}", exc_info=True)
                return

            # ── Convert to MP3 ────────────────────────────────────────────
            base_name = os.path.splitext(original_filename)[0]
            output_filename = f"{base_name}.mp3"
            output_path = os.path.join(temp_dir, output_filename)

            audio = AudioSegment.from_file(input_path)
            duration_mins = len(audio) / 60000

            # Track which MP3 path to use for transcription
            final_mp3_path = None
            mp3_sent = False

            # Try 128k high quality first
            try:
                logger.info("Attempting 128k conversion...")
                audio.export(output_path, format="mp3", bitrate="128k", parameters=["-ar", "44100"])
                file_size_mb = os.path.getsize(output_path) / (1024 * 1024)

                if file_size_mb > 45:
                    raise Exception(f"Output too large ({file_size_mb:.1f} MB)")

                with open(output_path, 'rb') as f:
                    await message.reply_document(
                        document=f,
                        filename=output_filename,
                        caption=f"✅ High Quality MP3 (128k)\n📁 {file_size_mb:.2f} MB | ⏱ {duration_mins:.1f} min"
                    )
                await status_message.delete()
                final_mp3_path = output_path
                mp3_sent = True
                logger.info(f"✅ Sent 128k MP3: {output_filename}")

            except Exception as hq_error:
                logger.info(f"128k failed: {hq_error} — trying 64k...")
                await status_message.edit_text("🔄 File large, compressing to 64k...")

                # Try 64k mono compressed
                try:
                    compressed_path = os.path.join(temp_dir, f"{base_name}_compressed.mp3")
                    audio.export(compressed_path, format="mp3", bitrate="64k",
                                 parameters=["-ar", "44100", "-ac", "1"])
                    file_size_mb = os.path.getsize(compressed_path) / (1024 * 1024)

                    with open(compressed_path, 'rb') as f:
                        await message.reply_document(
                            document=f,
                            filename=output_filename,
                            caption=(f"✅ Compressed MP3 (64k mono)\n"
                                     f"📁 {file_size_mb:.2f} MB | ⏱ {duration_mins:.1f} min\n"
                                     f"💡 Optimized for voice")
                        )
                    await status_message.delete()
                    final_mp3_path = compressed_path
                    mp3_sent = True
                    logger.info(f"✅ Sent 64k MP3: {output_filename}")

                except Exception as compressed_error:
                    logger.info(f"64k failed: {compressed_error} — splitting into 2 parts...")
                    await status_message.edit_text("🔄 Still too large, splitting into 2 parts...")

                    duration_ms = len(audio)
                    half = duration_ms // 2

                    part1_path = os.path.join(temp_dir, f"{base_name}_part1.mp3")
                    part2_path = os.path.join(temp_dir, f"{base_name}_part2.mp3")

                    audio[:half].export(part1_path, format="mp3", bitrate="64k",
                                        parameters=["-ar", "44100", "-ac", "1"])
                    audio[half:].export(part2_path, format="mp3", bitrate="64k",
                                        parameters=["-ar", "44100", "-ac", "1"])

                    p1_mb = os.path.getsize(part1_path) / (1024 * 1024)
                    p2_mb = os.path.getsize(part2_path) / (1024 * 1024)

                    with open(part1_path, 'rb') as f:
                        await message.reply_document(
                            document=f,
                            filename=f"{base_name}_part1.mp3",
                            caption=f"✅ Part 1/2 | 📁 {p1_mb:.2f} MB | ⏱ {duration_mins/2:.1f} min"
                        )
                    with open(part2_path, 'rb') as f:
                        await message.reply_document(
                            document=f,
                            filename=f"{base_name}_part2.mp3",
                            caption=f"✅ Part 2/2 | 📁 {p2_mb:.2f} MB | ⏱ {duration_mins/2:.1f} min"
                        )
                    await status_message.delete()
                    final_mp3_path = part1_path  # Transcribe part 1 (largest coherent chunk)
                    mp3_sent = True
                    logger.info(f"✅ Sent in 2 parts: {output_filename}")

            # ── Transcribe ────────────────────────────────────────────────
            if mp3_sent and final_mp3_path and os.getenv('GEMINI_API_KEY'):
                transcription_status = await message.reply_text(
                    "🎙️ Transcribing with Gemini AI...\n"
                    "⏳ Please wait — this takes 1–3 minutes for longer files"
                )
                try:
                    transcription = await transcribe_with_gemini(final_mp3_path)
                    await transcription_status.delete()
                    await send_transcription(message, transcription, duration_mins)

                except Exception as trans_error:
                    await transcription_status.edit_text(
                        f"❌ Transcription failed: {str(trans_error)}\n\n"
                        f"✅ MP3 was still sent above"
                    )
                    logger.error(f"Transcription error: {trans_error}", exc_info=True)

            elif mp3_sent and not os.getenv('GEMINI_API_KEY'):
                logger.warning("GEMINI_API_KEY not set — skipping transcription")

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        try:
            await status_message.edit_text(f"❌ Error: {str(e)}")
        except Exception:
            pass


def main():
    """Start the bot"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("ERROR: TELEGRAM_BOT_TOKEN not set!")
        return

    has_gemini = bool(os.getenv('GEMINI_API_KEY'))

    application = Application.builder().token(token).build()
    application.add_handler(MessageHandler(
        filters.VOICE | filters.AUDIO | filters.Document.AUDIO,
        handle_audio
    ))

    logger.info("🤖 Bot starting...")
    logger.info("✅ MP3 conversion: Ready")
    logger.info(f"{'✅' if has_gemini else '⚠️ '} Gemini transcription: {'Ready' if has_gemini else 'GEMINI_API_KEY not set — transcription disabled'}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
