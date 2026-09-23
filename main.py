from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from PIL import Image, ImageDraw, ImageFont
import textwrap
import io

TOKEN = "8851697720:AAFkUX76UGMIXRxTftQBpqjKyPh76woEvpo"

# 7 ta shrift ro'yxati
FONTS = {
    "font1": {"name": "✍️ 1. Caveat", "file": "font1.ttf", "size": 36},
    "font2": {"name": "🖋️ 2. Marck Script", "file": "font2.ttf", "size": 34},
    "font3": {"name": "👨‍🎓 3. Bad Script", "file": "font3.ttf", "size": 35},
    "font4": {"name": "⚡ 4. Permanent Marker", "file": "font4.ttf", "size": 32},
    "font5": {"name": "🖊️ 5. Kalam (Oddiy Ruchka)", "file": "font5.ttf", "size": 34},
    "font6": {"name": "✏️ 6. Kalam (Ingichka Ruchka)", "file": "font6.ttf", "size": 34},
    "font7": {"name": "✒️ 7. Kalam (Qalin Ruchka)", "file": "font7.ttf", "size": 34},
}

user_texts = {}

# Asosiy doimiy menyu (Reply Keyboard)
def main_menu_keyboard():
    keyboard = [
        [KeyboardButton("✍️ Yangi konspekt yozish")],
        [KeyboardButton("ℹ️ Bot haqida"), KeyboardButton("❓ Yordam")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Shriftlarni tanlash tugmalari (Inline Keyboard)
def fonts_inline_keyboard():
    keyboard = [
        [InlineKeyboardButton(FONTS["font1"]["name"], callback_data="font1"), InlineKeyboardButton(FONTS["font2"]["name"], callback_data="font2")],
        [InlineKeyboardButton(FONTS["font3"]["name"], callback_data="font3"), InlineKeyboardButton(FONTS["font4"]["name"], callback_data="font4")],
        [InlineKeyboardButton(FONTS["font5"]["name"], callback_data="font5"), InlineKeyboardButton(FONTS["font6"]["name"], callback_data="font6")],
        [InlineKeyboardButton(FONTS["font7"]["name"], callback_data="font7")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "Salom! Men matnlaringizni qo'lyozma konspektga aylantirib beruvchi botman. 📝\n\n"
        "Menga konspekt qilmoqchi bo'lgan matningizni shunchaki yuboring!"
    )
    await update.message.reply_text(welcome_text, reply_markup=main_menu_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id

    # Doimiy menyu tugmalari bosilganda
    if text == "✍️ Yangi konspekt yozish":
        await update.message.reply_text("Konspekt qilmoqchi bo'lgan matningizni yuboring:", reply_markup=main_menu_keyboard())
        return
    elif text == "ℹ️ Bot haqida":
        about_text = (
            "🤖 **Konspekt Bot** — talabalar va o'quvchilar uchun eng yaxshi yordamchi!\n\n"
            "Ushbu bot matnlarni haqiqiy daftardagidek qo'lyozma rasmga aylantirib beradi."
        )
        await update.message.reply_text(about_text, parse_mode="Markdown", reply_markup=main_menu_keyboard())
        return
    elif text == "❓ Yordam":
        help_text = (
            "📌 **Qanday foydalaniladi?**\n"
            "1. Botga istalgan matningizni yuboring.\n"
            "2. Chiqqan tugmalardan o'zingizga yoqqan shriftni tanlang.\n"
            "3. Bot tayyor konspekt rasmini sizga yuboradi!\n\n"
            "Savollar bo'lsa: @my_student_konspekt_bot"
        )
        await update.message.reply_text(help_text, parse_mode="Markdown", reply_markup=main_menu_keyboard())
        return

    # Agar foydalanuvchi oddiy matn yuborsa
    user_texts[user_id] = text
    await update.message.reply_text(
        "Matn qabul qilindi! Endi o'zingizga yoqqan shriftni (yozuv usulini) tanlang:",
        reply_markup=fonts_inline_keyboard()
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data

    if data == "change_font":
        if user_id in user_texts:
            await query.message.reply_text("Boshqa shriftni tanlang:", reply_markup=fonts_inline_keyboard())
        else:
            await query.message.reply_text("Iltimos, avval yangi matn yuboring.", reply_markup=main_menu_keyboard())
        return

    if user_id not in user_texts:
        await query.message.reply_text("Matn topilmadi. Qaytadan matn yuboring.", reply_markup=main_menu_keyboard())
        return
        
    font_key = data
    font_info = FONTS[font_key]
    
    await query.edit_message_text(text=f"⏳ Rasm tayyorlanmoqda ({font_info['name']})...")
    
    try:
        image = Image.open("paper.jpg")
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(font_info["file"], size=font_info["size"])
        
        lines = textwrap.wrap(user_texts[user_id], width=42)
        
        x, y = 80, 100
        line_height = font_info["size"] + 12
        
        for line in lines:
            draw.text((x, y), line, fill=(20, 30, 140), font=font)
            y += line_height
        
        bio = io.BytesIO()
        bio.name = 'konspekt.jpg'
        image.save(bio, 'JPEG')
        bio.seek(0)
        
        # Rasm ostiga qayta shrift almashtirish tugmasi
        re_select_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Boshqa shriftda ko'rish", callback_data="change_font")]
        ])

        await query.message.reply_photo(
            photo=bio,
            caption=f"✅ **Konspekt tayyor!**\nUsul: {font_info['name']}",
            parse_mode="Markdown",
            reply_markup=re_select_keyboard
        )
    except Exception as e:
        await query.message.reply_text(f"❌ Xatolik! `{font_info['file']}` fayli papkada borligini tekshiring.\nXato: {e}")

async def setup_bot_commands(app: Application):
    # Telegram'dagi rasmiy "Menu" tugmasiga buyruqlarni o'rnatish
    commands = [
        BotCommand("start", "Botni qayta ishga tushirish"),
        BotCommand("help", "Yordam va ko'rsatma"),
    ]
    await app.bot.set_my_commands(commands)

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_click))
    
    print("Bot menyu va 7 ta shrift bilan ishga tushdi...")
    
    # Telegram menyusini sozlash
    app.post_init = setup_bot_commands
    app.run_polling()

if __name__ == '__main__':
    main()