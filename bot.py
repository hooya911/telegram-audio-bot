#!/usr/bin/env python3
"""
Telegram Audio Converter Bot - Railway Optimized Version
Automatically converts audio files to MP3 format
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from pydub import AudioSegment
import tempfile

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

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
            
            # Send converted file
            with open(output_path, 'rb') as mp3_file:
                await message.reply_document(
                    document=mp3_file,
                    filename=output_filename,
                    caption=f"✅ Converted to MP3\n📁 {file_size_mb:.2f} MB | ⏱ {duration_mins:.1f} min"
                )
            
            await status_message.delete()
            logger.info(f"Successfully converted: {output_filename}")
            
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
