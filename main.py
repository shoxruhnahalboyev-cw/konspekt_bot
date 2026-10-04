import asyncio
import io
import os
import re
import sqlite3
from threading import Thread

from flask import Flask
from PIL import Image, ImageDraw, ImageFont
from telegram import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Render uchun web server
app = Flask(__name__)


@app.route('/')
def home():
    return 'Bot is alive!'


def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)


def keep_alive():
    t = Thread(target=run_flask, daemon=True)
    t.start()


TOKEN = '8851697720:AAHiTdWO3PoDnSFLk2xdVbTR3TPrl8nazJQ'
CHANNEL_USERNAME = '@shoxrux_code'
ADMIN_ID = 7439126820


def init_db():
    conn = sqlite3.connect('bot_users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            username TEXT,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def add_user(user_id: int, full_name: str, username: str):
    try:
        conn = sqlite3.connect('bot_users.db')
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT OR IGNORE INTO users (user_id, full_name, username) 
            VALUES (?, ?, ?)
        ''',
            (user_id, full_name or '', username or ''),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f'DB error: {e}')


def get_users_count() -> int:
    try:
        conn = sqlite3.connect('bot_users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0


FONTS = {
    'font1': {
        'name': "✍️ 1. Caveat (Talaba qo'lyozmasi)",
        'file': 'font1.ttf',
        'default_size': 38,
    },
    'font2': {'name': '🖋️ 2. Marck Script', 'file': 'font2.ttf', 'default_size': 36},
    'font3': {'name': '👨‍🎓 3. Bad Script', 'file': 'font3.ttf', 'default_size': 34},
    'font4': {
        'name': '⚡ 4. Permanent Marker',
        'file': 'font4.ttf',
        'default_size': 32,
    },
    'font5': {
        'name': '🖊️ 5. Kalam (Oddiy Ruchka)',
        'file': 'font5.ttf',
        'default_size': 36,
    },
    'font6': {
        'name': '✏️ 6. Kalam (Ingichka Ruchka)',
        'file': 'font6.ttf',
        'default_size': 32,
    },
    'font7': {
        'name': '✒️ 7. Kalam (Qalin Ruchka)',
        'file': 'font7.ttf',
        'default_size': 36,
    },
}

user_data_store = {}


def wrap_text_by_pixels(text, font, max_width, draw):
    paragraphs = text.split('\n')
    lines = []

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            lines.append('')
            continue

        words = paragraph.split()
        if not words:
            continue

        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]

            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

    return lines


async def check_subscription(
    user_id: int, context: ContextTypes.DEFAULT_TYPE
) -> bool:
    try:
        member = await context.bot.get_chat_member(
            chat_id=CHANNEL_USERNAME, user_id=user_id
        )
        return member.status in ['creator', 'administrator', 'member']
    except Exception as e:
        print(f'Obuna tekshirishda xatolik: {e}')
        return False


def sub_keyboard():
    clean_username = CHANNEL_USERNAME.replace('@', '')
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📢 Kanalimizga a'zo bo'lish",
                url=f'https://t.me/{clean_username}',
            )
        ],
        [
            InlineKeyboardButton(
                "✅ A'zo bo'ldim / Tekshirish", callback_data='check_sub'
            )
        ],
    ])


def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton('✍️ Yangi matn yuborish')],
            [KeyboardButton('ℹ️ Bot haqida'), KeyboardButton('❓ Yordam')],
        ],
        resize_keyboard=True,
    )


def mode_inline_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(
            '📄 Standart Matn (A4)', callback_data='mode_text'
        ),
        InlineKeyboardButton("📜 She'r / Sheriy uslub", callback_data='mode_poem'),
    ]])


def fonts_inline_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                FONTS['font1']['name'], callback_data='font1'
            ),
            InlineKeyboardButton(
                FONTS['font2']['name'], callback_data='font2'
            ),
        ],
        [
            InlineKeyboardButton(
                FONTS['font3']['name'], callback_data='font3'
            ),
            InlineKeyboardButton(
                FONTS['font4']['name'], callback_data='font4'
            ),
        ],
        [
            InlineKeyboardButton(
                FONTS['font5']['name'], callback_data='font5'
            ),
            InlineKeyboardButton(
                FONTS['font6']['name'], callback_data='font6'
            ),
        ],
        [
            InlineKeyboardButton(
                FONTS['font7']['name'], callback_data='font7'
            )
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def generate_pdf_pages(clean_text, mode, font_info):
    base_img = Image.open('paper.jpg')
    img_w, img_h = base_img.size
    draw_dummy = ImageDraw.Draw(base_img)

    margin_left = 90 if mode == 'text' else 150
    margin_right = 80
    margin_top = 80
    margin_bottom = 80

    usable_width = img_w - margin_left - margin_right
    usable_height = img_h - margin_top - margin_bottom

    font_size = font_info['default_size']
    font = ImageFont.truetype(font_info['file'], size=font_size)

    lines = wrap_text_by_pixels(clean_text, font, usable_width, draw_dummy)
    line_spacing = int(font_size * 0.25)
    line_height = font_size + line_spacing

    max_lines_per_page = max(1, usable_height // line_height)
    pages_lines = [
        lines[i : i + max_lines_per_page]
        for i in range(0, len(lines), max_lines_per_page)
    ]

    pages_bytes = []
    for p_lines in pages_lines:
        page_img = Image.open('paper.jpg')
        draw = ImageDraw.Draw(page_img)
        y = margin_top

        for line in p_lines:
            draw.text((margin_left, y), line, fill=(20, 35, 110), font=font)
            y += line_height

        bio = io.BytesIO()
        page_img.save(bio, 'JPEG')
        bio.seek(0)
        pages_bytes.append(bio)

    return pages_bytes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    user = update.message.from_user
    add_user(user.id, user.full_name, user.username)

    if not await check_subscription(user.id, context):
        await update.message.reply_text(
            f"⚠️ **Botdan foydalanish uchun {CHANNEL_USERNAME} kanalimizga a'zo bo'ling!**",
            parse_mode='Markdown',
            reply_markup=sub_keyboard(),
        )
        return

    user_data_store[user.id] = {}

    await update.message.reply_text(
        "Salom! Konspekt yaratish uchun **matningizni yuboring**:",
        reply_markup=main_menu_keyboard(),
    )


async def stat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        total_users = get_users_count()
        await update.message.reply_text(
            f'📊 **Bot Statistikasi:**\n\n👤 Jami foydalanuvchilar: **{total_users} ta**',
            parse_mode='Markdown',
        )
    else:
        await update.message.reply_text(
            '❌ Siz bot admini emassiz!', reply_markup=main_menu_keyboard()
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user = update.message.from_user
    add_user(user.id, user.full_name, user.username)

    if not await check_subscription(user.id, context):
        await update.message.reply_text(
            f"⚠️ **Botdan foydalanish uchun {CHANNEL_USERNAME} kanalimizga a'zo bo'ling!**",
            parse_mode='Markdown',
            reply_markup=sub_keyboard(),
        )
        return

    text = update.message.text.strip()

    if text in ['✍️ Yangi matn yuborish', 'Yangi matn yuborish']:
        user_data_store[user.id] = {}
        await update.message.reply_text(
            '📥 **Konspekt qilish uchun yangi matningizni yuboring:**',
            parse_mode='Markdown',
            reply_markup=main_menu_keyboard(),
        )
        return
    elif text == 'ℹ️ Bot haqida':
        await update.message.reply_text(
            "🤖 **Talaba Konspekt Bot** — Matnlaringizni xuddi talaba daftardagidek chiroyli qo'lyozma A4 konspektga aylantirib beradi.",
            parse_mode='Markdown',
            reply_markup=main_menu_keyboard(),
        )
        return
    elif text == '❓ Yordam':
        await update.message.reply_text(
            '📌 Konspekt qilish uchun shunchaki matn yuboring va shriftni tanlang.',
            reply_markup=main_menu_keyboard(),
        )
        return

    user_data_store[user.id] = {'text': text}

    await update.message.reply_text(
        '✅ Matn qabul qilindi!\n\nEndi yozuv uslubini tanlang:',
        reply_markup=mode_inline_keyboard(),
    )


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return

    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == 'check_sub':
        if await check_subscription(user_id, context):
            try:
                await query.message.delete()
            except Exception:
                pass
            await query.message.reply_text(
                '✅ Rahmat! Obuna tasdiqlandi. Endi matn yuborishingiz mumkin.',
                reply_markup=main_menu_keyboard(),
            )
        else:
            await query.message.reply_text(
                "❌ Siz hali kanalga a'zo bo'lmadingiz! Kanalga kirib **A'zo bo'lish** tugmasini bosing.",
                reply_markup=sub_keyboard(),
            )
        return

    user_info = user_data_store.get(user_id, {})
    if 'text' not in user_info or not user_info['text']:
        await query.message.reply_text(
            '⚠️ Matn topilmadi! Iltimos, avval matn yuboring.',
            reply_markup=main_menu_keyboard(),
        )
        return

    if data.startswith('mode_'):
        user_data_store[user_id]['mode'] = (
            'poem' if data == 'mode_poem' else 'text'
        )
        await query.edit_message_text(
            text="Ajoyib! Endi o'zingizga yoqqan shriftni tanlang:",
            reply_markup=fonts_inline_keyboard(),
        )
        return

    if data == 'change_font':
        await query.message.reply_text(
            'Boshqa shriftni tanlang:', reply_markup=fonts_inline_keyboard()
        )
        return

    font_key = data
    if font_key not in FONTS:
        return

    font_info = FONTS[font_key]
    await query.edit_message_text(
        text=f"✍️ A4 sahifa yaratilmoqda ({font_info['name']})..."
    )

    try:
        raw_text = user_info['text']
        clean_text = re.sub(
            r'[^a-zA-Z0-9\s.,!?\"\'\-\—:;()№%@«»а-яА-ЯёЁo‘O‘g‘G‘o’O’g’G’]',
            '',
            raw_text,
        )
        mode = user_info.get('mode', 'text')

        # Rasmlarni asinxron fonda generatsiya qilish (bot qotib qolmasligi uchun)
        pages_bytes = await asyncio.to_thread(
            generate_pdf_pages, clean_text, mode, font_info
        )

        media_group = []
        for idx, bio in enumerate(pages_bytes):
            bio.name = f'page_{idx+1}.jpg'
            caption = (
                f'📝 **A4 Konspekt -- {idx+1}/{len(pages_bytes)}-sahifa**'
                if idx == 0
                else ''
            )
            media_group.append(InputMediaPhoto(media=bio, caption=caption))

        re_select_keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                "🎨 Boshqa shriftda ko'rish", callback_data='change_font'
            )
        ]])

        await query.message.reply_media_group(media=media_group)
        await query.message.reply_text(
            f'✅ Jami {len(pages_bytes)} ta A4 sahifa tayyorlandi!',
            reply_markup=re_select_keyboard,
        )

    except Exception as e:
        await query.message.reply_text(f'❌ Xatolik yuz berdi: {e}')


async def setup_bot_commands(app_obj: Application):
    commands = [
        BotCommand('start', 'Botni ishga tushirish'),
        BotCommand('help', 'Yordam'),
        BotCommand('stat', 'Statistika (Admin)'),
    ]
    await app_obj.bot.set_my_commands(commands)


def main():
    init_db()
    
    # 1. Flask serverni alohida thread'da ishga tushirish
    keep_alive()

    # 2. Asyncio Event Loop'ni qo'lda yaratish (Render Thread crash'ini oldini oladi)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # 3. Botni sozlash va ishga tushirish
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', start))
    application.add_handler(CommandHandler('stat', stat_command))
    application.add_handler(MessageHandler(filters.ALL, handle_message))
    application.add_handler(CallbackQueryHandler(button_click))

    # Polling'ni xavfsiz ishga tushirish
    application.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
    main()