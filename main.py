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
from threading import Thread

from flask import Flask
from googletrans import Translator
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

# Render server uchun Flask
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

TOKEN = '8851697720:AAE9w9hfGVA582w9vwumKUds9xw1DZ0ND_A'
CHANNEL_USERNAME = '@shoxrux_code'
ADMIN_ID = 7439126828

translator = Translator()


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
    return True


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


def action_inline_keyboard():
  return InlineKeyboardMarkup([
      [InlineKeyboardButton('📝 Konspekt Yaratish', callback_data='act_konspekt')],
      [InlineKeyboardButton('🌐 Tarjima Qilish', callback_data='act_translate')],
  ])


def translate_inline_keyboard():
  return InlineKeyboardMarkup([
      [
          InlineKeyboardButton('🇺🇿 UZB ➡️ 🇷🇺 RUS', callback_data='tr_uz_ru'),
          InlineKeyboardButton('🇷🇺 RUS ➡️ 🇺🇿 UZB', callback_data='tr_ru_uz'),
      ],
      [
          InlineKeyboardButton('🇺🇿 UZB ➡️ 🇬🇧 ENG', callback_data='tr_uz_en'),
          InlineKeyboardButton('🇬🇧 ENG ➡️ 🇺🇿 UZB', callback_data='tr_en_uz'),
      ],
      [
          InlineKeyboardButton('🇷🇺 RUS ➡️ 🇬🇧 ENG', callback_data='tr_ru_en'),
          InlineKeyboardButton('🇬🇧 ENG ➡️ 🇷🇺 RUS', callback_data='tr_en_ru'),
      ],
  ])


def mode_inline_keyboard():
  return InlineKeyboardMarkup([[
      InlineKeyboardButton(
          '📄 Oddiy Matn (A4 Printer)', callback_data='mode_text'
      ),
      InlineKeyboardButton("📜 She'r / Qo'shiq uslubi", callback_data='mode_poem'),
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

  await update.message.reply_text(
      'Salom! Matningizni yuboring, uni konspekt qilishingiz yoki 3 xil tilda'
      ' tarjima qilishingiz mumkin. 📝🌐',
      reply_markup=main_menu_keyboard(),
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
        f"⚠️ **Botdan foydalanish mezonlari uchun {CHANNEL_USERNAME} kanalimizga a'zo bo'ling!**",
        parse_mode='Markdown',
        reply_markup=sub_keyboard(),
    )
    return

  text = update.message.text

  if text == '✍️ Yangi matn yuborish':
    await update.message.reply_text(
        "Matningizni yuboring:", reply_markup=main_menu_keyboard()
    )
    return
  elif text == 'ℹ️ Bot haqida':
    await update.message.reply_text(
        "🤖 **Konspekt & Tarjimon Bot** — A4 konspekt yaratish va tarjima qilish"
        ' xizmati.',
        parse_mode='Markdown',
        reply_markup=main_menu_keyboard(),
    )
    return
  elif text == '❓ Yordam':
    await update.message.reply_text(
        "📌 Matn yuboring va keragli amaliyotni (Konspekt yoki Tarjima) tanlang.",
        reply_markup=main_menu_keyboard(),
    )
    return

  user_data_store[user.id] = {'text': text, 'mode': 'text'}
  await update.message.reply_text(
      'Matn qabul qilindi! Nima qilamiz?', reply_markup=action_inline_keyboard()
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
          '✅ Rahmat! Obuna tasdiqlandi.', reply_markup=main_menu_keyboard()
      )
    else:
      await query.message.reply_text(
          "❌ Siz hali kanalga a'zo bo'lmadingiz!", reply_markup=sub_keyboard()
      )
    return

  if user_id not in user_data_store:
    await query.message.reply_text(
        'Matn topilmadi. Qaytadan yuboring.', reply_markup=main_menu_keyboard()
    )
    return

  # Amaliyot tanlovi
  if data == 'act_konspekt':
    await query.edit_message_text(
        text='Yozuv uslubini tanlang:', reply_markup=mode_inline_keyboard()
    )
    return
  elif data == 'act_translate':
    await query.edit_message_text(
        text='Tarjima yoʻnalishini tanlang:',
        reply_markup=translate_inline_keyboard(),
    )
    return

  # Tarjima jarayoni
  if data.startswith('tr_'):
    src, dest = data.split('_')[1], data.split('_')[2]
    raw_text = user_data_store[user_id]['text']

    await query.edit_message_text(text='⏳ Tarjima qilinmoqda...')
    try:
      translated = translator.translate(raw_text, src=src, dest=dest)
      user_data_store[user_id]['text'] = translated.text  # Tarjimani saqlaymiz

      re_konspekt_keyboard = InlineKeyboardMarkup([[
          InlineKeyboardButton(
              '📝 Ushbu tarjimani Konspektga aylantirish',
              callback_data='act_konspekt',
          )
      ]])

      await query.message.reply_text(
          f'🌐 **Tarjima natijasi:**\n\n{translated.text}',
          parse_mode='Markdown',
          reply_markup=re_konspekt_keyboard,
      )
    except Exception as e:
      await query.message.reply_text(f'❌ Tarjimada xatolik boʻldi: {e}')
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
      text=f"⏳ A4 sahifa yaratilmoqda ({font_info['name']})..."
  )

  try:
    raw_text = user_data_store[user_id]['text']
    clean_text = re.sub(
        r'[^\w\s\d.,!?\'"\-–—:;()№%@\'"’‘«»QWERTZUIPASDFGHJKLZXCVBNMqwertzuiopasdfghjklyxcvbnmА-Яа-яЎўҚқҒғҲҳ]',
        '',
        raw_text,
    )

    mode = user_data_store[user_id].get('mode', 'text')

    base_img = Image.open('paper.jpg')
    img_w, img_h = base_img.size
    draw_dummy = ImageDraw.Draw(base_img)

    margin_left = 110 if mode == 'text' else 180
    margin_right = 100
    margin_top = 100
    margin_bottom = 120

    usable_width = img_w - margin_left - margin_right
    usable_height = img_h - margin_top - margin_bottom

    font_size = font_info['default_size']
    font = ImageFont.truetype(font_info['file'], size=font_size)

    lines = wrap_text_by_pixels(clean_text, font, usable_width, draw_dummy)
    line_spacing = int(font_size * 0.35)
    line_height = font_size + line_spacing
    total_height = len(lines) * line_height

    if total_height > usable_height:
      while total_height > usable_height and font_size > 20:
        font_size -= 1
        font = ImageFont.truetype(font_info['file'], size=font_size)
        lines = wrap_text_by_pixels(clean_text, font, usable_width, draw_dummy)
        line_spacing = int(font_size * 0.35)
        line_height = font_size + line_spacing
        total_height = len(lines) * line_height

    max_lines_per_page = max(1, usable_height // line_height)
    pages_lines = [
        lines[i : i + max_lines_per_page]
        for i in range(0, len(lines), max_lines_per_page)
    ]

    pages = []
    for p_lines in pages_lines:
      page_img = Image.open('paper.jpg')
      draw = ImageDraw.Draw(page_img)
      y = margin_top

      for line in p_lines:
        draw.text((margin_left, y), line, fill=(20, 35, 110), font=font)
        y += line_height

      pages.append(page_img)

    media_group = []
    for idx, page_img in enumerate(pages):
      bio = io.BytesIO()
      bio.name = f'page_{idx+1}.jpg'
      page_img.save(bio, 'JPEG')
      bio.seek(0)

      caption = (
          f'📄 **A4 Konspekt — {idx+1}/{len(pages)}-sahifa**' if idx == 0 else ''
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
    await query.message.reply_text(f'❌ Xatolik yuz berdi: {e}')


async def setup_bot_commands(app: Application):
  commands = [
      BotCommand('start', 'Botni qayta ishga tushirish'),
      BotCommand('help', "Yordam va ko'rsatma"),
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

  app.post_init = setup_bot_commands
  app.run_polling()


if __name__ == '__main__':
  main()