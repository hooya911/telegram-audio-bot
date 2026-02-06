#!/usr/bin/env python3
"""
Telegram Audio Converter Bot with Google Gemini (Vertex AI)
Converts audio to MP3 and transcribes using Gemini via Vertex AI
"""

import os
import logging
import json
import tempfile
import uuid
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from pydub import AudioSegment
from google.cloud import storage
from google.oauth2 import service_account
import vertexai
from vertexai.generative_models import GenerativeModel, Part

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Google Cloud Storage and Vertex AI Gemini
storage_client = None
project_id = None
bucket_name = None
gemini_model = None

try:
    # Get credentials from environment variable
    credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    if credentials_json:
        credentials_dict = json.loads(credentials_json)
        credentials = service_account.Credentials.from_service_account_info(credentials_dict)
        
        # Initialize Storage client
        storage_client = storage.Client(credentials=credentials, project=credentials_dict['project_id'])
        project_id = credentials_dict['project_id']
        bucket_name = f"{project_id}-telegram-bot-temp"
        
        # Initialize Vertex AI (uses same credentials as Cloud Storage!)
        vertexai.init(project=project_id, location="us-central1", credentials=credentials)
        gemini_model = GenerativeModel("gemini-1.5-pro")
        
        logger.info("✅ Google Gemini (Vertex AI) enabled - Notebook LLM quality!")
        logger.info(f"✅ Using project: {project_id}")
    else:
        logger.warning("⚠️ GOOGLE_APPLICATION_CREDENTIALS_JSON not set - transcription disabled")
except Exception as e:
    logger.warning(f"⚠️ Initialization failed: {e}")

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
            
            # Transcribe with Vertex AI Gemini (same as Notebook LLM!)
            if gemini_model and storage_client:
                try:
                    await message.reply_text(
                        f"🎙️ Transcribing with Gemini (Notebook LLM quality)...\n"
                        f"File: {file_size_mb:.1f} MB | Duration: {duration_mins:.1f} min"
                    )
                    
                    # Upload to Cloud Storage for Vertex AI
                    try:
                        bucket = storage_client.bucket(bucket_name)
                        if not bucket.exists():
                            logger.info(f"Creating bucket: {bucket_name}")
                            bucket = storage_client.create_bucket(bucket_name, location="us")
                    except Exception as e:
                        logger.error(f"Bucket error: {e}")
                        await message.reply_text(f"⚠️ Storage setup failed")
                        return
                    
                    # Upload audio file
                    blob_name = f"audio_{uuid.uuid4()}.mp3"
                    blob = bucket.blob(blob_name)
                    logger.info(f"Uploading to Cloud Storage...")
                    blob.upload_from_filename(output_path)
                    
                    gcs_uri = f"gs://{bucket_name}/{blob_name}"
                    logger.info(f"File uploaded: {gcs_uri}")
                    
                    await message.reply_text("☁️ Processing audio with Gemini...")
                    
                    # Create audio part for Vertex AI
                    audio_part = Part.from_uri(gcs_uri, mime_type="audio/mpeg")
                    
                    # Comprehensive prompt for best transcription
                    prompt = """Transcribe this audio recording accurately and completely.

Instructions:
- Transcribe every word exactly as spoken
- Preserve the original language (do not translate)
- Include proper punctuation and capitalization
- If multiple speakers, note speaker changes
- Maintain natural flow and phrasing
- Do NOT summarize - provide word-for-word transcription

Provide only the complete transcription."""
                    
                    # Generate transcription
                    logger.info("Generating transcription with Vertex AI Gemini...")
                    response = gemini_model.generate_content([prompt, audio_part])
                    
                    # Clean up
                    try:
                        blob.delete()
                        logger.info("✅ Cleaned up Cloud Storage")
                    except:
                        pass
                    
                    # Get transcript
                    full_transcript = response.text.strip()
                    
                    if full_transcript and len(full_transcript) > 0:
                        # Split for Telegram's message limit
                        max_length = 4000
                        if len(full_transcript) <= max_length:
                            await message.reply_text(
                                f"📝 **Transcription:**\n\n{full_transcript}",
                                parse_mode="Markdown"
                            )
                        else:
                            parts = [full_transcript[i:i+max_length] 
                                    for i in range(0, len(full_transcript), max_length)]
                            for i, part in enumerate(parts):
                                await message.reply_text(
                                    f"📝 **Part {i+1}/{len(parts)}:**\n\n{part}",
                                    parse_mode="Markdown"
                                )
                        logger.info(f"✅ Transcription completed: {len(full_transcript)} chars")
                    else:
                        await message.reply_text("⚠️ No transcription generated")
                        
                except Exception as e:
                    logger.error(f"Transcription error: {e}", exc_info=True)
                    await message.reply_text(f"⚠️ Transcription failed: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
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
