import logging
import random
import os
from io import BytesIO
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image, ImageDraw, ImageFont

# ==================== CONFIG ====================
BOT_TOKEN = "8811695172:AAElOR2kWDC3cnXI5uyS2Ko5jpiVRleFyjs"
TEMPLATE_IMAGE = "C:\\Users\\zrean\\OneDrive\\Desktop\\template.jpg.jpg"
# ================================================

logging.basicConfig(level=logging.INFO)

active_users = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("بەخێربێیت 😄 بنووسە: Kapl")

def create_final_image(user1_bytes, user2_bytes):
    try:
        bg = Image.open(TEMPLATE_IMAGE).convert("RGBA")
    except:
        bg = Image.new("RGBA", (1920, 1080), (200, 20, 60, 255))

    def create_circle_avatar(img_bytes, size=500):
        if not img_bytes:
            return None
        try:
            img = Image.open(BytesIO(img_bytes)).convert("RGBA")
            img = img.resize((size, size))
            mask = Image.new("L", (size, size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size, size), fill=255)
            output = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            output.paste(img, (0, 0), mask)
            return output
        except:
            return None

    # ===== گۆڕانکاری لە شوێنی بازنەکان (بۆ ئەم وێنەیە) =====
    left_x, left_y = 345, 422
    right_x, right_y = 980, 422
    # =======================================================

    def create_broken_heart(size=500):
        heart = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw_heart = ImageDraw.Draw(heart)
        try:
            font = ImageFont.truetype("arial.ttf", 280)
        except:
            font = ImageFont.load_default()
        draw_heart.text((size//2, size//2), "💔", fill=(255, 100, 150, 255), anchor="mm", font=font)
        return heart

    avatar1 = create_circle_avatar(user1_bytes)
    avatar2 = create_circle_avatar(user2_bytes)

    if avatar1:
        bg.paste(avatar1, (left_x - 250, left_y - 250), avatar1)
    else:
        bg.paste(create_broken_heart(), (left_x - 250, left_y - 250), create_broken_heart())

    if avatar2:
        bg.paste(avatar2, (right_x - 250, right_y - 250), avatar2)
    else:
        bg.paste(create_broken_heart(), (right_x - 250, right_y - 250), create_broken_heart())

    out = BytesIO()
    bg.save(out, format="PNG")
    out.seek(0)
    return out

async def track_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user = update.effective_user
    chat = update.effective_chat
    text = update.message.text.lower().strip()
    chat_id = chat.id

    if chat_id not in active_users:
        active_users[chat_id] = set()

    active_users[chat_id].add(user.id)

    if text != "kapl":
        return

    try:
        await update.message.delete()
    except:
        pass

    if len(active_users[chat_id]) < 2:
        await context.bot.send_message(chat_id, "پێویستە لانی کەم ٢ کەس پەیام بنێرن 😅")
        return

    u1_id, u2_id = random.sample(list(active_users[chat_id]), 2)

    u1 = (await context.bot.get_chat_member(chat_id, u1_id)).user
    u2 = (await context.bot.get_chat_member(chat_id, u2_id)).user

    photos1 = await context.bot.get_user_profile_photos(u1_id, limit=1)
    photos2 = await context.bot.get_user_profile_photos(u2_id, limit=1)

    img1_bytes = None
    img2_bytes = None

    if photos1.total_count > 0:
        file1 = await context.bot.get_file(photos1.photos[0][0].file_id)
        img1_bytes = await file1.download_as_bytearray()

    if photos2.total_count > 0:
        file2 = await context.bot.get_file(photos2.photos[0][0].file_id)
        img2_bytes = await file2.download_as_bytearray()

    final_img = create_final_image(img1_bytes, img2_bytes)

    if not final_img:
        await context.bot.send_message(chat_id, "هەڵە لە دروستکردنی وێنە!")
        return

    caption_text = (
        "💘 دوو کەس دیاری کراون ❤️\n"
        "━━━━━━━━━━━━━━\n"
        f"🔥 {u1.mention_html()}\n"
        f"🔥 {u2.mention_html()}\n"
        "━━━━━━━━━━━━━━\n"
        "😂 پیرۆزە!"
    )

    await context.bot.send_photo(
        chat_id=chat_id,
        photo=final_img,
        caption=caption_text,
        parse_mode="HTML"
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_users))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()