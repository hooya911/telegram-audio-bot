#!/usr/bin/env python3
"""
Telegram Audio Converter Bot
- Converts any audio format to MP3
- Transcribes audio using Google Cloud Speech-to-Text Chirp 3 (Farsi + English)
- Generates AI summary using Gemini
"""

import os
import math
import logging
import tempfile
import asyncio
import subprocess
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


def _get_audio_duration_secs(path: str) -> float:
    """Return audio duration in seconds using ffprobe (no file load into RAM)."""
    import json

    # Try stream-level duration first
    probe = subprocess.run(
        ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', path],
        capture_output=True, text=True
    )
    try:
        for stream in json.loads(probe.stdout).get('streams', []):
            if 'duration' in stream:
                return float(stream['duration'])
    except Exception:
        pass

    # Fallback: format-level duration
    probe2 = subprocess.run(
        ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', path],
        capture_output=True, text=True
    )
    try:
        return float(json.loads(probe2.stdout).get('format', {}).get('duration', 0))
    except Exception:
        return 0


async def transcribe_with_chirp(mp3_path: str) -> str:
    """Transcribe audio using Google Cloud Speech-to-Text Chirp 3.

    Each 55-second chunk is extracted via ffmpeg directly from disk — the full
    audio file is never loaded into RAM, so there is no memory limit and no
    truncation regardless of recording length.
    """
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

    client_options = ClientOptions(api_endpoint="us-speech.googleapis.com")
    client = SpeechClient(credentials=credentials, client_options=client_options)

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

    # Determine total duration without loading the file into memory
    duration_secs = _get_audio_duration_secs(mp3_path)
    CHUNK_SECS = 55
    num_chunks = max(1, math.ceil(duration_secs / CHUNK_SECS))
    logger.info(f"Audio: {duration_secs:.1f}s — {num_chunks} chunk(s) for Chirp 3")

    loop = asyncio.get_running_loop()
    all_lines = []
    last_timestamp_seconds = -120  # force first timestamp at [0:00]

    for idx in range(num_chunks):
        chunk_offset_secs = idx * CHUNK_SECS

        # Extract this 55-second window with ffmpeg — reads only that slice,
        # never the whole file, keeping RAM usage constant regardless of length
        tmp = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        tmp.close()
        try:
            result = subprocess.run(
                [
                    'ffmpeg', '-y',
                    '-ss', str(chunk_offset_secs),   # fast seek (before -i)
                    '-t', str(CHUNK_SECS),
                    '-i', mp3_path,
                    '-ar', '16000', '-ac', '1', '-b:a', '16k',
                    '-f', 'mp3', tmp.name
                ],
                capture_output=True
            )
            if result.returncode != 0 or os.path.getsize(tmp.name) < 500:
                logger.info(f"Chunk {idx + 1}/{num_chunks}: empty or ffmpeg error — skipping")
                continue

            with open(tmp.name, 'rb') as f:
                chunk_bytes = f.read()
        finally:
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)

        request = cloud_speech.RecognizeRequest(
            recognizer=recognizer_path,
            config=config,
            content=chunk_bytes,
        )

        try:
            response = await loop.run_in_executor(
                None, lambda r=request: client.recognize(request=r)
            )
        except Exception as chunk_err:
            logger.error(f"Chunk {idx + 1}/{num_chunks} failed: {chunk_err}")
            all_lines.append(f"[chunk {idx + 1} error: {chunk_err}]")
            continue

        for res in response.results:
            if not res.alternatives:
                continue
            best = res.alternatives[0]
            text = best.transcript.strip()
            if not text:
                continue

            # Timestamp every ~2 minutes (absolute position = chunk offset + word offset)
            if best.words:
                try:
                    offset = best.words[0].start_offset
                    if hasattr(offset, 'total_seconds'):
                        word_secs = int(offset.total_seconds())
                    else:
                        word_secs = int(offset.seconds + offset.nanos / 1e9)
                    start_secs = chunk_offset_secs + word_secs
                    if start_secs - last_timestamp_seconds >= 120:
                        mins = start_secs // 60
                        secs = start_secs % 60
                        all_lines.append(f"[{mins}:{secs:02d}]")
                        last_timestamp_seconds = start_secs
                except Exception:
                    pass

            all_lines.append(text)

        logger.info(f"Chunk {idx + 1}/{num_chunks} done")

    return "\n".join(all_lines) if all_lines else "No speech detected in audio"


async def summarize_with_gemini(transcription: str, duration_mins: float) -> str:
    """Send transcription to Gemini and return a detailed summary."""
    import google.generativeai as genai

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set")

    genai.configure(api_key=api_key)

    prompt = f"""You are summarizing a {duration_mins:.1f}-minute audio recording that was transcribed from mixed Farsi and English speech.

TRANSCRIPTION:
{transcription}

Write a detailed summary of everything discussed. Follow these rules:
- Summarize in the same language(s) as the speaker used — Farsi parts in Persian script (فارسی), English parts in English
- Use clear sections/bullet points to organize the key topics
- Cover all main points, decisions, and important details — do not skip anything significant
- Keep it concise but comprehensive (not a word-for-word repeat)
- If the audio is mostly Farsi, write the summary mostly in Farsi; if mostly English, mostly English"""

    # Try models in order of preference — fall back if one is unavailable
    candidate_models = [
        "gemini-2.0-flash-lite",
        "gemini-2.0-flash-001",
        "gemini-2.5-flash",
        "gemini-2.5-pro",
    ]

    loop = asyncio.get_running_loop()
    last_error = None
    for model_name in candidate_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = await loop.run_in_executor(
                None, lambda m=model: m.generate_content(prompt)
            )
            logger.info(f"Summary generated using model: {model_name}")
            return response.text.strip()
        except Exception as e:
            logger.warning(f"Model {model_name} failed: {e}")
            last_error = e
            continue

    raise RuntimeError(f"All summary models failed. Last error: {last_error}")


async def send_long_text(message, header: str, body: str, parse_mode: str = 'Markdown'):
    """Send text to Telegram, splitting into multiple messages if needed."""
    LIMIT = 4000
    full = header + body
    if len(full) <= LIMIT:
        await message.reply_text(full, parse_mode=parse_mode)
        return

    await message.reply_text(header, parse_mode=parse_mode)
    remaining = body
    part = 1
    while remaining:
        chunk = remaining[:LIMIT]
        remaining = remaining[LIMIT:]
        suffix = f"\n\n_(part {part})_" if remaining else ""
        await message.reply_text(chunk + suffix)
        part += 1


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

            # transcription_mp3_path always points to the FULL audio file
            # (may differ from what was sent to Telegram if split)
            transcription_mp3_path = None
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
                transcription_mp3_path = output_path
                mp3_sent = True
                logger.info(f"✅ Sent 128k MP3: {output_filename}")

            except Exception as hq_error:
                logger.info(f"128k failed: {hq_error} — trying 64k...")
                await status_message.edit_text("🔄 File large, compressing to 64k...")

                # Try 64k mono compressed
                compressed_path = os.path.join(temp_dir, f"{base_name}_compressed.mp3")
                try:
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
                    transcription_mp3_path = compressed_path  # Full file
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

                    # Use compressed file for transcription if export succeeded
                    # (it exists but was too large for Telegram — Chirp reads it chunk-by-chunk)
                    if os.path.exists(compressed_path):
                        transcription_mp3_path = compressed_path
                    else:
                        transcription_mp3_path = part1_path
                    mp3_sent = True
                    logger.info(f"✅ Sent in 2 parts: {output_filename}")

            # ── Transcribe (Chirp 3) ──────────────────────────────────────
            if mp3_sent and transcription_mp3_path and os.getenv('GOOGLE_CLOUD_CREDENTIALS'):
                transcription_status = await message.reply_text(
                    "🎙️ Transcribing with Chirp 3 (Google Cloud)...\n"
                    "⏳ Please wait — this takes 1–3 minutes for longer files"
                )
                try:
                    transcription = await transcribe_with_chirp(transcription_mp3_path)
                    await transcription_status.delete()

                    header = f"📝 *Transcription* — ⏱ {duration_mins:.1f} min\n{'━' * 28}\n\n"
                    await send_long_text(message, header, transcription)

                    # ── Summary (optional, only if GEMINI_API_KEY is set) ──
                    if os.getenv('GEMINI_API_KEY'):
                        summary_status = await message.reply_text(
                            "🤖 Generating AI summary with Gemini..."
                        )
                        try:
                            summary = await summarize_with_gemini(transcription, duration_mins)
                            await summary_status.delete()
                            header = f"📋 *Summary* — ⏱ {duration_mins:.1f} min\n{'━' * 28}\n\n"
                            await send_long_text(message, header, summary)
                            logger.info("✅ Summary sent")
                        except Exception as sum_error:
                            await summary_status.edit_text(
                                f"⚠️ Summary failed: {str(sum_error)}\n"
                                f"✅ Transcription was still sent above"
                            )
                            logger.error(f"Summary error: {sum_error}", exc_info=True)

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
    has_gemini = bool(os.getenv('GEMINI_API_KEY'))

    application = Application.builder().token(token).build()
    application.add_handler(MessageHandler(
        filters.VOICE | filters.AUDIO | filters.Document.AUDIO,
        handle_audio
    ))

    logger.info("🤖 Bot starting...")
    logger.info("✅ MP3 conversion: Ready")
    logger.info(f"{'✅' if has_chirp else '⚠️ '} Chirp 3 transcription: {'Ready (ffmpeg chunking — no memory limit)' if has_chirp else 'GOOGLE_CLOUD_CREDENTIALS not set'}")
    logger.info(f"{'✅' if has_gemini else '⚠️ '} Gemini summary: {'Ready' if has_gemini else 'GEMINI_API_KEY not set — summary disabled'}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
