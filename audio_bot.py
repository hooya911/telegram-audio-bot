#!/usr/bin/env python3
"""
Telegram Audio Converter Bot
Automatically converts audio files (m4a, ogg, etc.) to MP3 format
Perfect for preparing voice memos for Google Notebook LLM transcription
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
    """
    Handle incoming audio/voice messages and convert them to MP3
    """
    message = update.message
    
    # Get the audio file (could be voice message or audio file)
    audio_file = None
    original_filename = "voice_memo"
    
    if message.voice:
        audio_file = message.voice
        original_filename = f"voice_{message.voice.file_unique_id}"
        logger.info(f"Received voice message: {original_filename}")
    elif message.audio:
        audio_file = message.audio
        original_filename = message.audio.file_name or f"audio_{message.audio.file_unique_id}"
        logger.info(f"Received audio file: {original_filename}")
    elif message.document:
        # Check if document is an audio file
        file_ext = os.path.splitext(message.document.file_name)[1].lower()
        if file_ext in SUPPORTED_FORMATS:
            audio_file = message.document
            original_filename = message.document.file_name
            logger.info(f"Received audio document: {original_filename}")
    
    if not audio_file:
        return
    
    # Send processing message
    status_message = await message.reply_text("🎵 Converting to MP3... Please wait.")
    
    try:
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download the file
            file = await audio_file.get_file()
            input_path = os.path.join(temp_dir, "input_audio")
            await file.download_to_drive(input_path)
            
            logger.info(f"Downloaded file to {input_path}")
            
            # Determine output filename
            base_name = os.path.splitext(original_filename)[0]
            output_filename = f"{base_name}.mp3"
            output_path = os.path.join(temp_dir, output_filename)
            
            # Convert to MP3
            logger.info(f"Converting to MP3...")
            audio = AudioSegment.from_file(input_path)
            
            # Export as MP3 with good quality settings
            audio.export(
                output_path,
                format="mp3",
                bitrate="128k",  # Good quality for voice
                parameters=["-ar", "44100"]  # Standard sample rate
            )
            
            logger.info(f"Conversion complete: {output_filename}")
            
            # Get file size for info
            file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            duration_mins = len(audio) / 60000  # milliseconds to minutes
            
            # Send the converted MP3 back
            with open(output_path, 'rb') as mp3_file:
                await message.reply_document(
                    document=mp3_file,
                    filename=output_filename,
                    caption=f"✅ Converted to MP3\n"
                            f"📁 Size: {file_size_mb:.2f} MB\n"
                            f"⏱ Duration: {duration_mins:.1f} minutes\n\n"
                            f"Ready for Google Notebook LLM! 🎯"
                )
            
            # Delete status message
            await status_message.delete()
            
            logger.info(f"Successfully sent MP3: {output_filename}")
            
    except Exception as e:
        logger.error(f"Error converting audio: {e}", exc_info=True)
        await status_message.edit_text(
            f"❌ Error converting audio: {str(e)}\n\n"
            f"Please make sure the file is a valid audio format."
        )

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "👋 Welcome to Audio Converter Bot!\n\n"
        "🎵 I convert audio files to MP3 format, perfect for Google Notebook LLM.\n\n"
        "📤 Just send me:\n"
        "• Voice messages\n"
        "• Audio files (m4a, ogg, wav, etc.)\n"
        "• Any audio document\n\n"
        "⚡️ I'll automatically convert them to MP3 and send them back!\n\n"
        "💡 Tip: Create a private channel, add me as admin, and forward all your "
        "voice memos there. I'll convert them automatically!"
    )

def main():
    """Start the bot"""
    # Get token from environment variable
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("ERROR: TELEGRAM_BOT_TOKEN environment variable not set!")
        logger.error("Please set it with: export TELEGRAM_BOT_TOKEN='your-token-here'")
        return
    
    # Create the Application
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(MessageHandler(
        filters.VOICE | filters.AUDIO | filters.Document.AUDIO,
        handle_audio
    ))
    
    # Start command (optional, for testing)
    from telegram.ext import CommandHandler
    application.add_handler(CommandHandler("start", handle_start))
    
    # Start the bot
    logger.info("🤖 Bot is starting...")
    logger.info("✅ Ready to convert audio files to MP3!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
