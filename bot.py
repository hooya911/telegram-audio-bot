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


async def transcribe_with_chirp(mp3_path: str) -> str:
    """Transcribe audio using Google Cloud Speech-to-Text Chirp 3 model"""
    import json
    from google.cloud.speech_v2 import SpeechClient
    from google.cloud.speech_v2.types import cloud_speech
    from google.api_core.client_options import ClientOptions
    from google.oauth2 import service_account

    credentials_json = os.getenv('GOOGLE_CLOUD_CREDENTIALS')
    if not credentials_json:
        raise ValueError("GOOGLE_CLOUD_CREDENTIALS environment variable is not set")

    credentials_info = json.loads(credentials_json)
    project_id = credentials_info.get('project_id')
    if not project_id:
        raise ValueError("project_id not found in GOOGLE_CLOUD_CREDENTIALS")

    credentials = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    with open(mp3_path, 'rb') as f:
        audio_bytes = f.read()

    loop = asyncio.get_event_loop()

    def do_transcribe():
        client_options = ClientOptions(api_endpoint="us-speech.googleapis.com")
        client = SpeechClient(
            credentials=credentials,
            client_options=client_options
        )

        config = cloud_speech.RecognitionConfig(
            auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
            model="chirp_3",
            language_codes=["fa-IR", "en-US"],
            features=cloud_speech.RecognitionFeatures(
                enable_automatic_punctuation=True,
                enable_word_time_offsets=True,
            ),
        )

        recognizer_path = f"projects/{project_id}/locations/us/recognizers/_"
        request = cloud_speech.RecognizeRequest(
            recognizer=recognizer_path,
            config=config,
            content=audio_bytes
        )

        logger.info("Sending audio to Chirp 3 (Google Cloud Speech-to-Text)...")
        return client.recognize(request=request)

    response = await loop.run_in_executor(None, do_transcribe)

    # Assemble transcription with timestamps every ~2 minutes
    lines = []
    last_timestamp_seconds = -120  # Force first timestamp at [0:00]

    for result in response.results:
        if not result.alternatives:
            continue
        best = result.alternatives[0]
        text = best.transcript.strip()
        if not text:
            continue

        # Insert timestamp every ~2 minutes using word timing
        if best.words:
            try:
                offset = best.words[0].start_offset
                if hasattr(offset, 'total_seconds'):
                    start_secs = int(offset.total_seconds())
                else:
                    start_secs = int(offset.seconds + offset.nanos / 1e9)
                if start_secs - last_timestamp_seconds >= 120:
                    mins = start_secs // 60
                    secs = start_secs % 60
                    lines.append(f"[{mins}:{secs:02d}]")
                    last_timestamp_seconds = start_secs
            except Exception:
                pass

        lines.append(text)

    return "\n".join(lines) if lines else "No speech detected in audio"


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
            if mp3_sent and final_mp3_path and os.getenv('GOOGLE_CLOUD_CREDENTIALS'):
                transcription_status = await message.reply_text(
                    "🎙️ Transcribing with Chirp 3 (Google Cloud)...\n"
                    "⏳ Please wait — this takes 1–3 minutes for longer files"
                )
                try:
                    transcription = await transcribe_with_chirp(final_mp3_path)
                    await transcription_status.delete()
                    await send_transcription(message, transcription, duration_mins)

                except Exception as trans_error:
                    await transcription_status.edit_text(
                        f"❌ Transcription failed: {str(trans_error)}\n\n"
                        f"✅ MP3 was still sent above"
                    )
                    logger.error(f"Transcription error: {trans_error}", exc_info=True)

            elif mp3_sent and not os.getenv('GOOGLE_CLOUD_CREDENTIALS'):
                logger.warning("GOOGLE_CLOUD_CREDENTIALS not set — skipping transcription")

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

    has_chirp = bool(os.getenv('GOOGLE_CLOUD_CREDENTIALS'))

    application = Application.builder().token(token).build()
    application.add_handler(MessageHandler(
        filters.VOICE | filters.AUDIO | filters.Document.AUDIO,
        handle_audio
    ))

    logger.info("🤖 Bot starting...")
    logger.info("✅ MP3 conversion: Ready")
    logger.info(f"{'✅' if has_chirp else '⚠️ '} Chirp 3 transcription: {'Ready' if has_chirp else 'GOOGLE_CLOUD_CREDENTIALS not set — transcription disabled'}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
