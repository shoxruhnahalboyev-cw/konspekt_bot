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

# ⚠️ BU YERGA O'ZINGIZNING KANALINGIZ USERNAMENI YOZING (masalan: '@my_channel')
CHANNEL_USERNAME = '@A_ToolsX'

FONTS = {
    'font1': {
        'name': '✍️ 1. Caveat (14pt, 1.0)',
        'file': 'font1.ttf',
        'size': 32,
        'line_spacing': 10,
        'wrap_width': 58,
    },
    'font2': {
        'name': '🖋️ 2. Marck Script (14pt, 1.5)',
        'file': 'font2.ttf',
        'size': 32,
        'line_spacing': 22,
        'wrap_width': 58,
    },
    'font3': {
        'name': '👨‍🎓 3. Bad Script (12pt, 1.0)',
        'file': 'font3.ttf',
        'size': 27,
        'line_spacing': 8,
        'wrap_width': 68,
    },
    'font4': {
        'name': '⚡ 4. Permanent Marker',
        'file': 'font4.ttf',
        'size': 30,
        'line_spacing': 12,
        'wrap_width': 55,
    },
    'font5': {
        'name': '🖊️ 5. Kalam (Oddiy Ruchka)',
        'file': 'font5.ttf',
        'size': 32,
        'line_spacing': 10,
        'wrap_width': 58,
    },
    'font6': {
        'name': '✏️ 6. Kalam (Ingichka Ruchka)',
        'file': 'font6.ttf',
        'size': 27,
        'line_spacing': 8,
        'wrap_width': 68,
    },
    'font7': {
        'name': '✒️ 7. Kalam (Qalin Ruchka)',
        'file': 'font7.ttf',
        'size': 32,
        'line_spacing': 22,
        'wrap_width': 58,
    },
}

user_data_store = {}


async def check_subscription(
    user_id: int, context: ContextTypes.DEFAULT_TYPE
) -> bool:
  """Foydalanuvchi kanalda bor-yo'qligini tekshirish"""
  try:
    member = await context.bot.get_chat_member(
        chat_id=CHANNEL_USERNAME, user_id=user_id
    )
    if member.status in ['creator', 'administrator', 'member']:
      return True
    return False
  except Exception:
    return False


def sub_keyboard():
  """Kanalga a'zo bo'lish tugmasi"""
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
  user_id = update.message.from_user.id

  if not await check_subscription(user_id, context):
    await update.message.reply_text(
        "⚠️ **Botdan foydalanish uchun avval kanalimizga a'zo bo'ling!**\n\nA'zo"
        " bo'lgach, 'Tekshirish' tugmasini bosing.",
        parse_mode='Markdown',
        reply_markup=sub_keyboard(),
    )
    return

  welcome_text = (
      "Salom! Men matnlaringizni A4 varaqli qo'lyozma konspektga aylantirib"
      " beruvchi botman. 📝\n\nKatta matn bo'lsa ham bot avtomatik sahifalarga"
      " bo'lib beradi. Matningizni yuboring!"
  )
  await update.message.reply_text(
      welcome_text, reply_markup=main_menu_keyboard()
  )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if not update.message or not update.message.text:
    return

  user_id = update.message.from_user.id

  # Kanal a'zoligini tekshiramiz
  if not await check_subscription(user_id, context):
    await update.message.reply_text(
        "⚠️ **Botdan foydalanish uchun avval kanalimizga a'zo bo'ling!**",
        parse_mode='Markdown',
        reply_markup=sub_keyboard(),
    )
    return

  text = update.message.text

  if text == '✍️ Yangi konspekt yozish':
    await update.message.reply_text(
        'Konspekt qilmoqchi bo\'lgan matningizni yuboring:',
        reply_markup=main_menu_keyboard(),
    )
    return
  elif text == 'ℹ️ Bot haqida':
    about_text = (
        '🤖 **Konspekt Bot** — Matnlarni A4 formatdagi qo\'lyozma konspekt'
        ' rasmlariga aylantirib beradi.'
    )
    await update.message.reply_text(
        about_text, parse_mode='Markdown', reply_markup=main_menu_keyboard()
    )
    return
  elif text == '❓ Yordam':
    help_text = (
        '📌 **Qanday foydalaniladi?**\n1. Matn yuboring (1000+ so\'z bo\'lsa'
        " ham bo'laveradi).\n2. Uslubni tanlang.\n3. Shriftni tanlang va tayyor"
        ' A4 sahifalarni oling!'
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

  # Tekshirish tugmasi bosilganda
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
          ' a\'zo bo\'ling.',
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

    if mode == 'poem':
      x_start = 160
      x_indent = 160
      wrap_width = 32
    else:
      x_start = 70
      x_indent = 110
      wrap_width = font_info['wrap_width']

    paragraphs = clean_text.split('\n')
    all_lines = []

    for paragraph in paragraphs:
      paragraph = paragraph.strip()
      if not paragraph:
        continue
      wrapped = textwrap.wrap(paragraph, width=wrap_width)
      for i, line in enumerate(wrapped):
        is_indent = i == 0 and mode == 'text'
        all_lines.append((line, is_indent))

    y_start = 80
    max_y = 1150
    line_height = font_info['size'] + font_info['line_spacing']

    pages = []
    current_image = Image.open('paper.jpg')
    current_draw = ImageDraw.Draw(current_image)
    font = ImageFont.truetype(font_info['file'], size=font_info['size'])
    y = y_start

    for line, is_indent in all_lines:
      if y + line_height > max_y:
        pages.append(current_image)
        current_image = Image.open('paper.jpg')
        current_draw = ImageDraw.Draw(current_image)
        y = y_start

      current_x = x_indent if is_indent else x_start
      current_draw.text((current_x, y), line, fill=(20, 30, 130), font=font)
      y += line_height

    pages.append(current_image)

    media_group = []
    bio_list = []

    for idx, page_img in enumerate(pages):
      bio = io.BytesIO()
      bio.name = f'page_{idx+1}.jpg'
      page_img.save(bio, 'JPEG')
      bio.seek(0)
      bio_list.append(bio)

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
        f"✅ Jami {len(pages)} ta A4 sahifa tayyorlandi!",
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