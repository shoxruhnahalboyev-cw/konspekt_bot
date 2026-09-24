import os
from threading import Thread
from flask import Flask

app = Flask('')


@app.route('/')
def home():
  return 'Bot is alive!'


def run():
  app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))


def keep_alive():
  t = Thread(target=run)
  t.start()


import io
import os
import re
import sqlite3
import textwrap
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

# Render uchun Flask server
app = Flask('')


@app.route('/')
def home():
  return 'Bot is alive!'


def run():
  app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))


def keep_alive():
  t = Thread(target=run)
  t.start()


keep_alive()

TOKEN = '8851697720:AAHk1WNfp63cLBthfDXqQnlsJqGbIrX3S58'
CHANNEL_USERNAME = '@shoxrux_code'

# ⚠️ O'ZINGIZNING TELEGRAM ID-INGIZNI YOZING
ADMIN_ID = 7439126820


# --- MA'LUMOTLAR BAZASI (SQLite) ---
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
  conn = sqlite3.connect('bot_users.db')
  cursor = conn.cursor()
  cursor.execute(
      '''
        INSERT OR IGNORE INTO users (user_id, full_name, username) 
        VALUES (?, ?, ?)
    ''',
      (user_id, full_name, username),
  )
  conn.commit()
  conn.close()


def get_users_count() -> int:
  conn = sqlite3.connect('bot_users.db')
  cursor = conn.cursor()
  cursor.execute('SELECT COUNT(*) FROM users')
  count = cursor.fetchone()[0]
  conn.close()
  return count


init_db()

# Shriftlar konfiguratsiyasi (Baza o'lchamlari)
FONTS = {
    'font1': {
        'name': '✍️ 1. Caveat (Talaba qo\'lyozmasi)',
        'file': 'font1.ttf',
        'base_size': 26,
        'base_spacing': 8,
        'wrap_width': 70,
    },
    'font2': {
        'name': '🖋️ 2. Marck Script',
        'file': 'font2.ttf',
        'base_size': 26,
        'base_spacing': 9,
        'wrap_width': 68,
    },
    'font3': {
        'name': '👨‍🎓 3. Bad Script',
        'file': 'font3.ttf',
        'base_size': 24,
        'base_spacing': 7,
        'wrap_width': 72,
    },
    'font4': {
        'name': '⚡ 4. Permanent Marker',
        'file': 'font4.ttf',
        'base_size': 25,
        'base_spacing': 9,
        'wrap_width': 65,
    },
    'font5': {
        'name': '🖊️ 5. Kalam (Oddiy Ruchka)',
        'file': 'font5.ttf',
        'base_size': 26,
        'base_spacing': 8,
        'wrap_width': 70,
    },
    'font6': {
        'name': '✏️ 6. Kalam (Ingichka Ruchka)',
        'file': 'font6.ttf',
        'base_size': 24,
        'base_spacing': 7,
        'wrap_width': 72,
    },
    'font7': {
        'name': '✒️ 7. Kalam (Qalin Ruchka)',
        'file': 'font7.ttf',
        'base_size': 26,
        'base_spacing': 9,
        'wrap_width': 68,
    },
}

user_data_store = {}


async def check_subscription(
    user_id: int, context: ContextTypes.DEFAULT_TYPE
) -> bool:
  try:
    member = await context.bot.get_chat_member(
        chat_id=CHANNEL_USERNAME, user_id=user_id
    )
    return member.status in ['creator', 'administrator', 'member']
  except Exception:
    return False


def sub_keyboard():
  clean_username = CHANNEL_USERNAME.replace('@', '')
  keyboard = [
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
  ]
  return InlineKeyboardMarkup(keyboard)


def main_menu_keyboard():
  keyboard = [
      [KeyboardButton('✍️ Yangi konspekt yozish')],
      [KeyboardButton('ℹ️ Bot haqida'), KeyboardButton('❓ Yordam')],
  ]
  return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def mode_inline_keyboard():
  keyboard = [[
      InlineKeyboardButton(
          '📄 Oddiy Matn (A4 Printer)', callback_data='mode_text'
      ),
      InlineKeyboardButton('📜 She\'r / Qo\'shiq uslubi', callback_data='mode_poem'),
  ]]
  return InlineKeyboardMarkup(keyboard)


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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if not update.message:
    return
  user = update.message.from_user

  add_user(user.id, user.full_name, user.username)

  if not await check_subscription(user.id, context):
    await update.message.reply_text(
        "⚠️ **Botdan foydalanish uchun avval kanalimizga a'zo bo'ling!**\n\nA'zo"
        " bo'lgach, 'Tekshirish' tugmasini bosing.",
        parse_mode='Markdown',
        reply_markup=sub_keyboard(),
    )
    return

  welcome_text = (
      "Salom! Men matnlaringizni A4 varaqli qo'lyozma konspektga aylantirib"
      " beruvchi botman. 📝\n\nMatningizni yuboring va A4 shaklidagi haqiqiy"
      ' talaba konspektiga ega bo\'ling!'
  )
  await update.message.reply_text(
      welcome_text, reply_markup=main_menu_keyboard()
  )


async def stat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_id = update.message.from_user.id
  if user_id == ADMIN_ID:
    total_users = get_users_count()
    await update.message.reply_text(
        f'📊 **Bot Statistikasi:**\n\n👤 Jami foydalanuvchilar: **{total_users}'
        ' ta**',
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
        "⚠️ **Botdan foydalanish uchun avval kanalimizga a'zo bo'ling!**",
        parse_mode='Markdown',
        reply_markup=sub_keyboard(),
    )
    return

  text = update.message.text

  if text == '✍️ Yangi konspekt yozish':
    await update.message.reply_text(
        "Konspekt qilmoqchi bo'lgan matningizni yuboring:",
        reply_markup=main_menu_keyboard(),
    )
    return
  elif text == 'ℹ️ Bot haqida':
    about_text = (
        "🤖 **Konspekt Bot** — Matnlarni A4 formatdagi qo'lyozma konspekt"
        ' rasmlariga aylantirib beradi.'
    )
    await update.message.reply_text(
        about_text, parse_mode='Markdown', reply_markup=main_menu_keyboard()
    )
    return
  elif text == '❓ Yordam':
    help_text = (
        "📌 **Qanday foydalaniladi?**\n1. Matn yuboring.\n2. Uslubni tanlang.\n3."
        ' Shriftni tanlang va A4 sahifani oling!'
    )
    await update.message.reply_text(
        help_text, parse_mode='Markdown', reply_markup=main_menu_keyboard()
    )
    return

  user_data_store[user.id] = {'text': text, 'mode': 'text'}
  await update.message.reply_text(
      'Matn qabul qilindi! Yozuv uslubini tanlang:',
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
      await query.message.delete()
      await query.message.reply_text(
          "✅ **Rahmat! Obuna tasdiqlandi.**\nEndi matningizni yuborishingiz"
          ' mumkin.',
          parse_mode='Markdown',
          reply_markup=main_menu_keyboard(),
      )
    else:
      await query.message.reply_text(
          "❌ **Siz hali kanalga a'zo bo'lmadingiz!**\nIltimos, avval kanalga"
          " a'zo bo'ling.",
          reply_markup=sub_keyboard(),
      )
    return

  if not await check_subscription(user_id, context):
    await query.message.reply_text(
        "⚠️ **Avval kanalga a'zo bo'ling!**", reply_markup=sub_keyboard()
    )
    return

  if user_id not in user_data_store:
    await query.message.reply_text(
        'Matn topilmadi. Qaytadan matn yuboring.',
        reply_markup=main_menu_keyboard(),
    )
    return

  if data.startswith('mode_'):
    mode = 'poem' if data == 'mode_poem' else 'text'
    user_data_store[user_id]['mode'] = mode
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
      text=f"⏳ A4 sahifalar tayyorlanmoqda ({font_info['name']})..."
  )

  try:
    raw_text = user_data_store[user_id]['text']
    clean_text = re.sub(
        r'[^\w\s\d.,!?\'"\-–—:;()№%@\'"’‘«»QWERTZUIPASDFGHJKLZXCVBNMqwertzuiopasdfghjklyxcvbnmА-Яа-яЎўҚқҒғҲҳ]',
        '',
        raw_text,
    )

    mode = user_data_store[user_id].get('mode', 'text')

    # MARGINLAR VA PLANETKA TARTIBI
    if mode == 'poem':
      x_start = 140
      x_indent = 140
      wrap_width = 45
    else:
      x_start = 75  # Chap margin ~1.8 sm
      x_indent = 110  # Paragraf o'ngroq xatboshi
      wrap_width = font_info['wrap_width']

    y_start = 75  # Tepadagi margin ~1.5 sm
    max_y = 1320  # Pastki marja ~1.5 sm bo'sh joygacha

    # --- DINAMIK FONT VA QATOR ORALIG'INI HISOBLASH ---
    words_count = len(clean_text.split())

    # Harf hajmi va spetsifikatsiyalarini matn uzunligiga moslash
    font_size = font_info['base_size']
    line_spacing = font_info['base_spacing']

    if words_count < 220:
      font_size += 3
      line_spacing += 3
    elif words_count > 380:
      font_size -= 2
      line_spacing -= 2

    line_height = font_size + line_spacing
    lines_per_page = (max_y - y_start) // line_height

    # --- GAPLARNI KESMASDAN SAHIFALARGA BO'LISH ---
    raw_paragraphs = clean_text.split('\n')
    pages_lines = []
    current_page_lines = []

    for paragraph in raw_paragraphs:
      paragraph = paragraph.strip()
      if not paragraph:
        continue

      # Gaplarni yakunlovchi belgilar orqali bo'lish (., !, ?)
      sentences = re.split(r'(?<=[.!?]) +', paragraph)

      for sentence in sentences:
        wrapped_sentence = textwrap.wrap(sentence, width=wrap_width)
        sentence_line_count = len(wrapped_sentence)

        # Agar gap joriy A4 betga sig'masa, gapni TO'LIQ yangi sahifaga o'tkazish
        if len(current_page_lines) + sentence_line_count > lines_per_page:
          if current_page_lines:
            pages_lines.append(current_page_lines)
            current_page_lines = []

        for idx, line in enumerate(wrapped_sentence):
          is_indent = idx == 0 and mode == 'text'
          current_page_lines.append((line, is_indent))

    if current_page_lines:
      pages_lines.append(current_page_lines)

    # --- RASMLARNI YARATISH ---
    pages = []
    font = ImageFont.truetype(font_info['file'], size=font_size)

    for page_lines in pages_lines:
      current_image = Image.open('paper.jpg')
      current_draw = ImageDraw.Draw(current_image)
      y = y_start

      for line, is_indent in page_lines:
        current_x = x_indent if is_indent else x_start
        # Tabiiy ko'k siyoh rangi (Dark Slate Blue / Navy)
        current_draw.text((current_x, y), line, fill=(25, 40, 115), font=font)
        y += line_height

      pages.append(current_image)

    media_group = []
    for idx, page_img in enumerate(pages):
      bio = io.BytesIO()
      bio.name = f'page_{idx+1}.jpg'
      page_img.save(bio, 'JPEG')
      bio.seek(0)

      caption = (
          f"📄 **A4 Konspekt — {idx+1}/{len(pages)}-sahifa**\nShrift:"
          f" {font_info['name']}"
          if idx == 0
          else ''
      )
      media_group.append(InputMediaPhoto(media=bio, caption=caption))

    re_select_keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "🔄 Boshqa shriftda ko'rish", callback_data='change_font'
        )
    ]])

    await query.message.reply_media_group(media=media_group)
    await query.message.reply_text(
        f'✅ Jami {len(pages)} ta A4 sahifa tayyorlandi!',
        reply_markup=re_select_keyboard,
    )

  except Exception as e:
    await query.message.reply_text(f'❌ Xatolik: {e}')


async def setup_bot_commands(app: Application):
  commands = [
      BotCommand('start', 'Botni qayta ishga tushirish'),
      BotCommand('help', 'Yordam va ko\'rsatma'),
      BotCommand('stat', 'Statistika (Admin)'),
  ]
  await app.bot.set_my_commands(commands)


def main():
  app = Application.builder().token(TOKEN).build()

  app.add_handler(CommandHandler('start', start))
  app.add_handler(CommandHandler('help', start))
  app.add_handler(CommandHandler('stat', stat_command))
  app.add_handler(MessageHandler(filters.ALL, handle_message))
  app.add_handler(CallbackQueryHandler(button_click))

  print('Bot ishga tushdi...')

  app.post_init = setup_bot_commands
  app.run_polling()


if __name__ == '__main__':
  main()