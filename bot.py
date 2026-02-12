#!/usr/bin/env python3
"""
Telegram Audio Converter Bot - MP3 Only
Converts any audio format to MP3
"""

import os
import logging
import tempfile
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from pydub import AudioSegment

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
            # Download file with retry logic
            try:
                file = await audio_file.get_file()
                input_path = os.path.join(temp_dir, "input_audio")
                await file.download_to_drive(input_path)
                logger.info(f"Downloaded file successfully")
            except Exception as download_error:
                error_msg = str(download_error)
                if "413" in error_msg or "too large" in error_msg.lower():
                    await status_message.edit_text(
                        f"⚠️ File too large for Telegram API (13+ MB)\n\n"
                        f"💡 Workaround:\n"
                        f"1. Save the voice message to Files\n"
                        f"2. Send it as a document (not voice message)\n"
                        f"3. Bot will convert it!"
                    )
                else:
                    await status_message.edit_text(f"❌ Download failed: {error_msg}")
                logger.error(f"Download error: {download_error}", exc_info=True)
                return
            
            # Convert to MP3
            base_name = os.path.splitext(original_filename)[0]
            output_filename = f"{base_name}.mp3"
            output_path = os.path.join(temp_dir, output_filename)
            
            audio = AudioSegment.from_file(input_path)
            duration_mins = len(audio) / 60000
            
            # Try high quality first (128k)
            try:
                logger.info("Attempting 128k high quality conversion...")
                audio.export(
                    output_path,
                    format="mp3",
                    bitrate="128k",
                    parameters=["-ar", "44100"]
                )
                
                file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                
                # Check if output is too large for Telegram (50 MB limit)
                if file_size_mb > 45:
                    logger.info(f"Output too large ({file_size_mb:.1f} MB), trying 64k...")
                    raise Exception("File too large, need compression")
                
                # Try to send high quality version
                with open(output_path, 'rb') as mp3_file:
                    await message.reply_document(
                        document=mp3_file,
                        filename=output_filename,
                        caption=f"✅ High Quality MP3 (128k)\n📁 {file_size_mb:.2f} MB | ⏱ {duration_mins:.1f} min"
                    )
                
                await status_message.delete()
                logger.info(f"✅ Sent high quality: {output_filename}")
                return
                
            except Exception as hq_error:
                logger.info(f"High quality failed, trying compressed... ({hq_error})")
                await status_message.edit_text("🔄 File large, compressing to 64k...")
                
                # Fallback: Try 64k compressed
                try:
                    output_path_compressed = os.path.join(temp_dir, f"{base_name}_compressed.mp3")
                    audio.export(
                        output_path_compressed,
                        format="mp3",
                        bitrate="64k",
                        parameters=["-ar", "44100", "-ac", "1"]  # Mono
                    )
                    
                    file_size_mb = os.path.getsize(output_path_compressed) / (1024 * 1024)
                    
                    # Try to send compressed version
                    with open(output_path_compressed, 'rb') as mp3_file:
                        await message.reply_document(
                            document=mp3_file,
                            filename=output_filename,
                            caption=f"✅ Compressed MP3 (64k mono)\n📁 {file_size_mb:.2f} MB | ⏱ {duration_mins:.1f} min\n💡 Quality optimized for voice transcription"
                        )
                    
                    await status_message.delete()
                    logger.info(f"✅ Sent compressed: {output_filename}")
                    return
                    
                except Exception as compressed_error:
                    logger.info(f"Compressed failed, splitting... ({compressed_error})")
                    await status_message.edit_text("🔄 Still too large, splitting into parts...")
                    
                    # Final fallback: Split into 2 parts
                    duration_ms = len(audio)
                    half_duration = duration_ms // 2
                    
                    # Split audio
                    part1 = audio[:half_duration]
                    part2 = audio[half_duration:]
                    
                    # Export both parts (64k for size)
                    part1_path = os.path.join(temp_dir, f"{base_name}_part1.mp3")
                    part2_path = os.path.join(temp_dir, f"{base_name}_part2.mp3")
                    
                    part1.export(part1_path, format="mp3", bitrate="64k", parameters=["-ar", "44100", "-ac", "1"])
                    part2.export(part2_path, format="mp3", bitrate="64k", parameters=["-ar", "44100", "-ac", "1"])
                    
                    part1_size = os.path.getsize(part1_path) / (1024 * 1024)
                    part2_size = os.path.getsize(part2_path) / (1024 * 1024)
                    
                    # Send both parts
                    with open(part1_path, 'rb') as mp3_file:
                        await message.reply_document(
                            document=mp3_file,
                            filename=f"{base_name}_part1.mp3",
                            caption=f"✅ Part 1/2\n📁 {part1_size:.2f} MB | ⏱ {duration_mins/2:.1f} min"
                        )
                    
                    with open(part2_path, 'rb') as mp3_file:
                        await message.reply_document(
                            document=mp3_file,
                            filename=f"{base_name}_part2.mp3",
                            caption=f"✅ Part 2/2\n📁 {part2_size:.2f} MB | ⏱ {duration_mins/2:.1f} min"
                        )
                    
                    await status_message.delete()
                    logger.info(f"✅ Sent in 2 parts: {output_filename}")
                    return
            
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
