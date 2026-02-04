#!/usr/bin/env python3
"""
Telegram Audio Converter Bot with Google Cloud Speech-to-Text
Converts audio to MP3 and transcribes using Google Cloud Speech-to-Text API
"""

import os
import logging
import json
import tempfile
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from pydub import AudioSegment
from google.cloud import speech
from google.oauth2 import service_account

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Google Cloud Speech client
speech_client = None
try:
    # Get credentials from environment variable
    credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    if credentials_json:
        credentials_dict = json.loads(credentials_json)
        credentials = service_account.Credentials.from_service_account_info(credentials_dict)
        speech_client = speech.SpeechClient(credentials=credentials)
        logger.info("✅ Google Cloud Speech-to-Text enabled for transcription")
    else:
        logger.warning("⚠️ GOOGLE_APPLICATION_CREDENTIALS_JSON not set - transcription disabled")
except Exception as e:
    logger.warning(f"⚠️ Google Cloud initialization failed: {e}")

# Supported audio formats
SUPPORTED_FORMATS = ['.m4a', '.ogg', '.opus', '.wav', '.aac', '.flac', '.wma']

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming audio/voice messages and convert them to MP3"""
    message = update.message
    
    # Get the audio file
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
    
    # Send processing message
    status_message = await message.reply_text("🎵 Converting to MP3...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download file
            file = await audio_file.get_file()
            input_path = os.path.join(temp_dir, "input_audio")
            await file.download_to_drive(input_path)
            
            # Convert to MP3
            base_name = os.path.splitext(original_filename)[0]
            output_filename = f"{base_name}.mp3"
            output_path = os.path.join(temp_dir, output_filename)
            
            audio = AudioSegment.from_file(input_path)
            audio.export(
                output_path,
                format="mp3",
                bitrate="128k",
                parameters=["-ar", "44100"]
            )
            
            # Get file info
            file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            duration_mins = len(audio) / 60000
            
            # Send converted MP3
            with open(output_path, 'rb') as mp3_file:
                await message.reply_document(
                    document=mp3_file,
                    filename=output_filename,
                    caption=f"✅ Converted to MP3\n📁 {file_size_mb:.2f} MB | ⏱ {duration_mins:.1f} min"
                )
            
            await status_message.delete()
            logger.info(f"Successfully converted: {output_filename}")
            
            # Transcribe with Google Cloud Speech-to-Text if available
            if speech_client and file_size_mb <= 10:  # Google Cloud limit for synchronous: 10MB
                try:
                    await message.reply_text("🎙️ Transcribing with Google Cloud Speech-to-Text...")
                    
                    # Read the audio file
                    with open(output_path, 'rb') as audio_file:
                        audio_content = audio_file.read()
                    
                    # Configure audio and recognition settings
                    audio = speech.RecognitionAudio(content=audio_content)
                    config = speech.RecognitionConfig(
                        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
                        sample_rate_hertz=44100,
                        language_code="fa-IR",  # Farsi - auto-detection would be "auto"
                        alternative_language_codes=["en-US", "tr-TR", "ar-SA"],  # English, Turkish, Arabic
                        enable_automatic_punctuation=True,
                        model="default",
                    )
                    
                    # Perform transcription
                    response = speech_client.recognize(config=config, audio=audio)
                    
                    # Combine all transcripts
                    transcript_parts = []
                    for result in response.results:
                        transcript_parts.append(result.alternatives[0].transcript)
                    
                    full_transcript = " ".join(transcript_parts)
                    
                    # Send transcription
                    if full_transcript and len(full_transcript.strip()) > 0:
                        # Split long transcripts
                        max_length = 4000
                        if len(full_transcript) <= max_length:
                            await message.reply_text(
                                f"📝 **Transcription:**\n\n{full_transcript}",
                                parse_mode="Markdown"
                            )
                        else:
                            # Split into chunks
                            chunks = [full_transcript[i:i+max_length] for i in range(0, len(full_transcript), max_length)]
                            for i, chunk in enumerate(chunks):
                                await message.reply_text(
                                    f"📝 **Transcription (Part {i+1}/{len(chunks)}):**\n\n{chunk}",
                                    parse_mode="Markdown"
                                )
                        logger.info(f"Transcription completed: {len(full_transcript)} chars")
                    else:
                        await message.reply_text("⚠️ No speech detected in audio")
                        
                except Exception as e:
                    logger.error(f"Transcription error: {e}", exc_info=True)
                    await message.reply_text(f"⚠️ Transcription failed: {str(e)}")
            elif speech_client and file_size_mb > 10:
                # For larger files, use async long-running operation
                try:
                    await message.reply_text("🎙️ Transcribing large file with Google Cloud (this may take a few minutes)...")
                    
                    # Read audio file
                    with open(output_path, 'rb') as audio_file:
                        audio_content = audio_file.read()
                    
                    # Configure for long audio
                    audio = speech.RecognitionAudio(content=audio_content)
                    config = speech.RecognitionConfig(
                        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
                        sample_rate_hertz=44100,
                        language_code="fa-IR",
                        alternative_language_codes=["en-US", "tr-TR", "ar-SA"],
                        enable_automatic_punctuation=True,
                        model="default",
                    )
                    
                    # Start long-running operation
                    operation = speech_client.long_running_recognize(config=config, audio=audio)
                    logger.info("Waiting for long-running operation to complete...")
                    
                    response = operation.result(timeout=300)  # 5 minute timeout
                    
                    # Combine transcripts
                    transcript_parts = []
                    for result in response.results:
                        transcript_parts.append(result.alternatives[0].transcript)
                    
                    full_transcript = " ".join(transcript_parts)
                    
                    if full_transcript and len(full_transcript.strip()) > 0:
                        # Split and send
                        max_length = 4000
                        if len(full_transcript) <= max_length:
                            await message.reply_text(
                                f"📝 **Transcription:**\n\n{full_transcript}",
                                parse_mode="Markdown"
                            )
                        else:
                            chunks = [full_transcript[i:i+max_length] for i in range(0, len(full_transcript), max_length)]
                            for i, chunk in enumerate(chunks):
                                await message.reply_text(
                                    f"📝 **Transcription (Part {i+1}/{len(chunks)}):**\n\n{chunk}",
                                    parse_mode="Markdown"
                                )
                        logger.info(f"Long transcription completed: {len(full_transcript)} chars")
                    else:
                        await message.reply_text("⚠️ No speech detected in audio")
                        
                except Exception as e:
                    logger.error(f"Long transcription error: {e}", exc_info=True)
                    await message.reply_text(f"⚠️ Long transcription failed: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error converting audio: {e}", exc_info=True)
        await status_message.edit_text(f"❌ Error: {str(e)}")

def main():
    """Start the bot"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("ERROR: TELEGRAM_BOT_TOKEN not set!")
        return
    
    application = Application.builder().token(token).build()
    
    application.add_handler(MessageHandler(
        filters.VOICE | filters.AUDIO | filters.Document.AUDIO,
        handle_audio
    ))
    
    logger.info("🤖 Bot starting...")
    logger.info("✅ Ready to convert audio files to MP3!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
