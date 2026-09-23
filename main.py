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

# 7 ta shrift ro'yxati
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

user_texts = {}


def main_menu_keyboard():
  keyboard = [
      [KeyboardButton('✍️ Yangi konspekt yozish')],
      [KeyboardButton('ℹ️ Bot haqida'), KeyboardButton('❓ Yordam')],
  ]
  return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


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
        '📌 **Qanday foydalaniladi?**\n1. Botga istalgan matningizni yuboring.\n2.'
        ' Chiqqan tugmalardan o\'zingizga yoqqan shriftni tanlang.\n3. Bot'
        ' tayyor konspekt rasmini sizga yuboradi!\n\nSavollar bo\'lsa:'
        ' @my_student_konspekt_bot'
    )
    await update.message.reply_text(
        help_text, parse_mode='Markdown', reply_markup=main_menu_keyboard()
    )
    return

  user_texts[user_id] = text
  await update.message.reply_text(
      'Matn qabul qilindi! Endi o\'zingizga yoqqan shriftni (yozuv usulini)'
      ' tanlang:',
      reply_markup=fonts_inline_keyboard(),
  )


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  if not query:
    return

  await query.answer()
  user_id = query.from_user.id
  data = query.data

  if data == 'change_font':
    if user_id in user_texts:
      await query.message.reply_text(
          'Boshqa shriftni tanlang:', reply_markup=fonts_inline_keyboard()
      )
    else:
      await query.message.reply_text(
          'Iltimos, avval yangi matn yuboring.',
          reply_markup=main_menu_keyboard(),
      )
    return

  if user_id not in user_texts:
    await query.message.reply_text(
        'Matn topilmadi. Qaytadan matn yuboring.',
        reply_markup=main_menu_keyboard(),
    )
    return

  font_key = data
  font_info = FONTS[font_key]

  await query.edit_message_text(
      text=f"⏳ Rasm tayyorlanmoqda ({font_info['name']})..."
  )

  try:
    image = Image.open('paper.jpg')
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_info['file'], size=font_info['size'])

    # Shrift qo'llab-quvvatlamaydigan emojilarni olib tashlash
    clean_text = re.sub(
        r'[^\w\s\d.,!?\'"\-–—:;()№%@\'"’‘«»QWERTZUIPASDFGHJKLZXCVBNMqwertzuiopasdfghjklyxcvbnmА-Яа-яЎўҚқҒғҲҳ]',
        '',
        user_texts[user_id],
    )

    # Paragraflar (Enter) bo'yicha ajratish
    paragraphs = clean_text.split('\n')

    x_start = 100  # Chap tomondan xoshiya
    x_indent = 150  # Xat boshi (abzats) uchun o'ngroqdan boshlash
    y = 100  # Tepadan boshlanish masofasi
    line_height = font_info['size'] + 14

    for paragraph in paragraphs:
      paragraph = paragraph.strip()
      if not paragraph:
        y += line_height // 2
        continue

      # O'ng tomondan joy qolishi uchun enini 36 harfga chegaralaymiz
      wrapped_lines = textwrap.wrap(paragraph, width=36)

      for i, line in enumerate(wrapped_lines):
        # Paragrafning birinchi qatori xat boshi bilan boshlanadi
        current_x = x_indent if i == 0 else x_start

        draw.text((current_x, y), line, fill=(20, 30, 130), font=font)
        y += line_height

      y += 8  # Paragraflar orasida biroz bo'shliq

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