#!/usr/bin/env python3
"""
Telegram Audio Converter Bot with Google Cloud Speech-to-Text
Converts audio to MP3 and transcribes using Google Cloud Speech-to-Text API
Uses Google Cloud Storage for large files (no size limits!)
"""

import os
import logging
import json
import tempfile
import uuid
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from pydub import AudioSegment
from google.cloud import speech
from google.cloud import storage
from google.oauth2 import service_account

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Google Cloud clients
speech_client = None
storage_client = None
project_id = None
bucket_name = None

try:
    # Get credentials from environment variable
    credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    if credentials_json:
        credentials_dict = json.loads(credentials_json)
        credentials = service_account.Credentials.from_service_account_info(credentials_dict)
        
        # Initialize Speech client
        speech_client = speech.SpeechClient(credentials=credentials)
        
        # Initialize Storage client
        storage_client = storage.Client(credentials=credentials, project=credentials_dict['project_id'])
        
        # Get project info
        project_id = credentials_dict['project_id']
        bucket_name = f"{project_id}-telegram-bot-temp"
        
        logger.info("✅ Google Cloud Speech-to-Text enabled for transcription")
        logger.info(f"✅ Google Cloud Storage enabled - bucket: {bucket_name}")
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
            
            # Transcribe with Google Cloud Speech-to-Text
            if speech_client and storage_client:
                try:
                    # For files larger than 10MB, use async API with Cloud Storage
                    if file_size_mb > 9:
                        await message.reply_text(
                            f"🎙️ Transcribing large file ({file_size_mb:.1f} MB) with Google Cloud...\n"
                            f"Uploading to Cloud Storage for async processing..."
                        )
                        
                        # Ensure bucket exists with lifecycle rule for automatic cleanup
                        try:
                            bucket = storage_client.bucket(bucket_name)
                            if not bucket.exists():
                                logger.info(f"Creating bucket: {bucket_name}")
                                bucket = storage_client.create_bucket(bucket_name, location="us")
                                
                                # Add lifecycle rule: auto-delete files older than 10 minutes
                                bucket.add_lifecycle_delete_rule(age=0, number_of_newer_versions=0)
                                bucket.lifecycle_rules = [
                                    {
                                        "action": {"type": "Delete"},
                                        "condition": {
                                            "age": 1,  # Delete after 1 day (backup safety)
                                            "matchesPrefix": ["audio_"]
                                        }
                                    }
                                ]
                                bucket.patch()
                                logger.info(f"✅ Bucket created with auto-cleanup: {bucket_name}")
                            else:
                                logger.info(f"Using existing bucket: {bucket_name}")
                        except Exception as e:
                            logger.error(f"Bucket error: {e}")
                            await message.reply_text(f"⚠️ Storage setup failed: {str(e)}")
                            return
                        
                        # Upload file to Cloud Storage
                        blob_name = f"audio_{uuid.uuid4()}.mp3"
                        blob = bucket.blob(blob_name)
                        
                        logger.info(f"Uploading {blob_name} to Cloud Storage...")
                        blob.upload_from_filename(output_path)
                        logger.info(f"✅ Upload complete")
                        
                        # Get GCS URI
                        gcs_uri = f"gs://{bucket_name}/{blob_name}"
                        
                        await message.reply_text(
                            "☁️ File uploaded! Starting transcription...\n"
                            "This may take a few minutes for long audio."
                        )
                        
                        # Configure for async recognition
                        audio = speech.RecognitionAudio(uri=gcs_uri)
                        config = speech.RecognitionConfig(
                            encoding=speech.RecognitionConfig.AudioEncoding.MP3,
                            sample_rate_hertz=44100,
                            language_code="fa-IR",
                            alternative_language_codes=["en-US", "tr-TR", "ar-SA"],
                            enable_automatic_punctuation=True,
                            model="default",
                        )
                        
                        # Start long-running operation
                        logger.info("Starting async transcription...")
                        operation = speech_client.long_running_recognize(config=config, audio=audio)
                        
                        # Wait for completion (with 10 minute timeout to match file retention)
                        logger.info("Waiting for transcription to complete...")
                        response = operation.result(timeout=600)  # 10 minute timeout
                        
                        # Clean up - delete file from Cloud Storage after successful transcription
                        try:
                            blob.delete()
                            logger.info(f"✅ Deleted {blob_name} from Cloud Storage after transcription")
                        except Exception as cleanup_error:
                            logger.warning(f"Cleanup warning: {cleanup_error}")
                            # Don't fail the whole operation if cleanup fails
                            pass
                        
                        # Get transcript
                        transcript_parts = [result.alternatives[0].transcript 
                                          for result in response.results]
                        full_transcript = " ".join(transcript_parts)
                        
                        if full_transcript and len(full_transcript.strip()) > 0:
                            # Split long transcripts for Telegram
                            max_length = 4000
                            if len(full_transcript) <= max_length:
                                await message.reply_text(
                                    f"📝 **Complete Transcription:**\n\n{full_transcript}",
                                    parse_mode="Markdown"
                                )
                            else:
                                parts = [full_transcript[i:i+max_length] 
                                        for i in range(0, len(full_transcript), max_length)]
                                for i, part in enumerate(parts):
                                    await message.reply_text(
                                        f"📝 **Transcription (Part {i+1}/{len(parts)}):**\n\n{part}",
                                        parse_mode="Markdown"
                                    )
                            logger.info(f"✅ Async transcription completed: {len(full_transcript)} chars")
                        else:
                            await message.reply_text("⚠️ No speech detected in audio")
                    
                    else:
                        # File is small - use direct sync API
                        await message.reply_text("🎙️ Transcribing with Google Cloud Speech-to-Text...")
                        
                        with open(output_path, 'rb') as audio_file:
                            audio_content = audio_file.read()
                        
                        audio = speech.RecognitionAudio(content=audio_content)
                        config = speech.RecognitionConfig(
                            encoding=speech.RecognitionConfig.AudioEncoding.MP3,
                            sample_rate_hertz=44100,
                            language_code="fa-IR",
                            alternative_language_codes=["en-US", "tr-TR", "ar-SA"],
                            enable_automatic_punctuation=True,
                            model="default",
                        )
                        
                        response = speech_client.recognize(config=config, audio=audio)
                        
                        transcript_parts = [result.alternatives[0].transcript 
                                          for result in response.results]
                        full_transcript = " ".join(transcript_parts)
                        
                        if full_transcript and len(full_transcript.strip()) > 0:
                            max_length = 4000
                            if len(full_transcript) <= max_length:
                                await message.reply_text(
                                    f"📝 **Transcription:**\n\n{full_transcript}",
                                    parse_mode="Markdown"
                                )
                            else:
                                chunks = [full_transcript[i:i+max_length] 
                                         for i in range(0, len(full_transcript), max_length)]
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
