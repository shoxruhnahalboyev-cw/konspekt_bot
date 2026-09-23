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
from threading import Thread
import textwrap

from flask import Flask
from PIL import Image, ImageDraw, ImageFont
from telegram import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
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

TOKEN = '8851697720:AAFkUX76UGMIXRxTftQBpqjKyPh76woEvpo'

FONTS = {
    'font1': {'name': '✍️ 1. Caveat', 'file': 'font1.ttf', 'size': 36},
    'font2': {'name': '🖋️ 2. Marck Script', 'file': 'font2.ttf', 'size': 34},
    'font3': {'name': '👨‍🎓 3. Bad Script', 'file': 'font3.ttf', 'size': 35},
    'font4': {'name': '⚡ 4. Permanent Marker', 'file': 'font4.ttf', 'size': 32},
    'font5': {
        'name': '🖊️ 5. Kalam (Oddiy Ruchka)',
        'file': 'font5.ttf',
        'size': 34,
    },
    'font6': {
        'name': '✏️ 6. Kalam (Ingichka Ruchka)',
        'file': 'font6.ttf',
        'size': 34,
    },
    'font7': {
        'name': '✒️ 7. Kalam (Qalin Ruchka)',
        'file': 'font7.ttf',
        'size': 34,
    },
}

user_data_store = {}


def main_menu_keyboard():
  keyboard = [
      [KeyboardButton('✍️ Yangi konspekt yozish')],
      [KeyboardButton('ℹ️ Bot haqida'), KeyboardButton('❓ Yordam')],
  ]
  return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def mode_inline_keyboard():
  keyboard = [[
      InlineKeyboardButton(
          '📄 Oddiy Matn (Printer/Konspekt)', callback_data='mode_text'
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
  welcome_text = (
      "Salom! Men matnlaringizni qo'lyozma konspektga aylantirib beruvchi"
      ' botman. 📝\n\nMenga konspekt qilmoqchi bo\'lgan matningizni shunchaki'
      ' yuboring!'
  )
  await update.message.reply_text(
      welcome_text, reply_markup=main_menu_keyboard()
  )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if not update.message or not update.message.text:
    if update.message:
      await update.message.reply_text(
          "Iltimos, faqat matnli xabar yuboring! 📝",
          reply_markup=main_menu_keyboard(),
      )
    return

  text = update.message.text
  user_id = update.message.from_user.id

  if text == '✍️ Yangi konspekt yozish':
    await update.message.reply_text(
        'Konspekt qilmoqchi bo\'lgan matningizni yuboring:',
        reply_markup=main_menu_keyboard(),
    )
    return
  elif text == 'ℹ️ Bot haqida':
    about_text = (
        '🤖 **Konspekt Bot** — talabalar va o\'quvchilar uchun eng yaxshi'
        ' yordamchi!\n\nUshbu bot matnlarni haqiqiy daftardagidek qo\'lyozma'
        ' rasmga aylantirib beradi.'
    )
    await update.message.reply_text(
        about_text, parse_mode='Markdown', reply_markup=main_menu_keyboard()
    )
    return
  elif text == '❓ Yordam':
    help_text = (
        '📌 **Qanday foydalaniladi?**\n1. Botga matn yuboring.\n2. Matn'
        " uslubini tanlang (Oddiy matn yoki She'r).\n3. Shriftni tanlang va"
        ' tayyor rasmni oling!'
    )
    await update.message.reply_text(
        help_text, parse_mode='Markdown', reply_markup=main_menu_keyboard()
    )
    return

  user_data_store[user_id] = {'text': text, 'mode': 'text'}
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
        text='Ajoyib! Endi o\'zingizga yoqqan shriftni tanlang:',
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
      text=f"⏳ Rasm tayyorlanmoqda ({font_info['name']})..."
  )

  try:
    image = Image.open('paper.jpg')
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_info['file'], size=font_info['size'])

    raw_text = user_data_store[user_id]['text']
    clean_text = re.sub(
        r'[^\w\s\d.,!?\'"\-–—:;()№%@\'"’‘«»QWERTZUIPASDFGHJKLZXCVBNMqwertzuiopasdfghjklyxcvbnmА-Яа-яЎўҚқҒғҲҳ]',
        '',
        raw_text,
    )

    mode = user_data_store[user_id].get('mode', 'text')

    if mode == 'poem':
      x_start = 160
      x_indent = 160
      wrap_width = 32
    else:
      x_start = 70
      x_indent = 110
      wrap_width = 58  # O'ng tarafgacha to'liq yetib borishi uchun

    y = 80
    line_height = font_info['size'] + 10

    paragraphs = clean_text.split('\n')

    for paragraph in paragraphs:
      paragraph = paragraph.strip()
      if not paragraph:
        continue  # Bo'sh qatorlar va ortqcha masofalar o'chirib tashlanadi

      wrapped_lines = textwrap.wrap(paragraph, width=wrap_width)

      for i, line in enumerate(wrapped_lines):
        current_x = (
            x_indent if (i == 0 and mode == 'text') else x_start
        )
        draw.text((current_x, y), line, fill=(20, 30, 130), font=font)
        y += line_height

    bio = io.BytesIO()
    bio.name = 'konspekt.jpg'
    image.save(bio, 'JPEG')
    bio.seek(0)

    re_select_keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "🔄 Boshqa shriftda ko'rish", callback_data='change_font'
        )
    ]])

    await query.message.reply_photo(
        photo=bio,
        caption=f"✅ **Konspekt tayyor!**\nUsul: {font_info['name']}",
        parse_mode='Markdown',
        reply_markup=re_select_keyboard,
    )
  except Exception as e:
    await query.message.reply_text(f'❌ Xatolik: {e}')


async def setup_bot_commands(app: Application):
  commands = [
      BotCommand('start', 'Botni qayta ishga tushirish'),
      BotCommand('help', 'Yordam va ko\'rsatma'),
  ]
  await app.bot.set_my_commands(commands)


def main():
  app = Application.builder().token(TOKEN).build()

  app.add_handler(CommandHandler('start', start))
  app.add_handler(CommandHandler('help', start))
  app.add_handler(MessageHandler(filters.ALL, handle_message))
  app.add_handler(CallbackQueryHandler(button_click))

  print('Bot ishga tushdi...')

  app.post_init = setup_bot_commands
  app.run_polling()


if __name__ == '__main__':
  main()