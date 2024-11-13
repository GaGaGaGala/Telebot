import telebot
from PIL import Image, ImageOps
import io
from telebot import types
from list_jokes import Jokes


TOKEN = '<token goes here>'
bot = telebot.TeleBot(TOKEN)

user_states = {}  # тут будем хранить информацию о действиях пользователя

# набор символов из которых составляем изображение
ASCII_CHARS = '@%#*+=-:. '
jokes = Jokes() # объект класса Jokes

def resize_image(image, new_width=100):
    """ Изменяет размер изображения с сохранением пропорций."""
    width, height = image.size
    ratio = height / width
    new_height = int(new_width * ratio)
    return image.resize((new_width, new_height))


def grayify(image):
    """Преобразует цветное изображение в оттенки серого."""
    return image.convert("L")


def image_to_ascii(image_stream, new_width=40):
    """ Основная функция для преобразования изображения в ASCII-арт. Изменяет размер, преобразует в градации
    серого и затем в строку ASCII-символов."""
    # Переводим в оттенки серого
    image = Image.open(image_stream).convert('L')

    # меняем размер сохраняя отношение сторон
    width, height = image.size
    aspect_ratio = height / float(width)
    new_height = int(
        aspect_ratio * new_width * 0.55)  # 0,55 так как буквы выше чем шире
    img_resized = image.resize((new_width, new_height))

    img_str = pixels_to_ascii(img_resized)
    img_width = img_resized.width

    max_characters = 4000 - (new_width + 1)
    max_rows = max_characters // (new_width + 1)

    ascii_art = ""
    for i in range(0, min(max_rows * img_width, len(img_str)), img_width):
        ascii_art += img_str[i:i + img_width] + "\n"

    return ascii_art


def pixels_to_ascii(image):
    """ Конвертирует пиксели изображения в градациях серого в строку ASCII-символов, используя
     предопределенную строку ASCII_CHARS."""
    pixels = image.getdata()
    characters = ""
    for pixel in pixels:
        characters += ASCII_CHARS[pixel * len(ASCII_CHARS) // 256]
    return characters


# Огрубляем изображение
def pixelate_image(image, pixel_size):
    """Принимает изображение и размер пикселя. Уменьшает изображение до размера, где один пиксель представляет большую
     область, затем увеличивает обратно, создавая пиксельный эффект."""
    image = image.resize(
        (image.size[0] // pixel_size, image.size[1] // pixel_size),
        Image.NEAREST
    )
    image = image.resize(
        (image.size[0] * pixel_size, image.size[1] * pixel_size),
        Image.NEAREST
    )
    return image


def invert_colors(image):
    """Функция меняет цвет изображения на противоположный."""
    return ImageOps.invert(image)


def mirror_image(image):
    """Создаёт зеркально-отражённое изображение по горизонтали."""
    return ImageOps.mirror(image)


def convert_to_heatmap(image):
    """Преобразует изображение в тепловую карту."""
    image = image.convert("L")
    return ImageOps.colorize(image, (0, 0, 255), (255, 0, 0))


def resize_for_sticker(image, new_width=60):
    """ Изменяет размер изображения для использования в качестве стикера в Telegram, ограничивая максимальный размер."""
    width, height = image.size
    ratio = height / width
    new_height = int(new_width * ratio)
    new_image = image.resize((new_width, new_height))
    new_image.show()
    return new_image


"""Обработчик сообщений реагирует на команды /start и /help, отправляя приветственное сообщение."""
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Send me an image, and I'll provide options for you!")


"""Обработчик, реагирует на изображения, отправляемые пользователем, и предлагает варианты обработки."""
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_states[message.chat.id] = {'level': 0}
    bot.send_message(message.chat.id, jokes.get_joke()) # вставляем шутку
    bot.reply_to(message, "I got your photo! Please choose what you'd like to do with it.",
                 reply_markup=get_options_keyboard())
    user_states[message.chat.id] = {'photo': message.photo[-1].file_id}


def get_options_keyboard():
    """Клавиатура для взаимодействия:"""
    keyboard = types.InlineKeyboardMarkup()
    pixelate_btn = types.InlineKeyboardButton("Pixelate", callback_data="pixelate")
    ascii_btn = types.InlineKeyboardButton("ASCII Art", callback_data="ascii")
    invert_btn = types.InlineKeyboardButton("Invert_colors", callback_data="invert")
    mirror_btn = types.InlineKeyboardButton("Mirror_image", callback_data="mirror")
    heatmap_btn = types.InlineKeyboardButton("Heatmap", callback_data="heatmap")
    resize_btn = types.InlineKeyboardButton("Resize_for_sticker", callback_data="resize")
    keyboard.add(pixelate_btn, ascii_btn, invert_btn, mirror_btn, heatmap_btn, resize_btn)
    return keyboard


"""Обработчик определяет действия в ответ на выбор пользователя. """
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "pixelate":
        user_states[chat_id]['level'] = 1
        bot.send_message(chat_id, jokes.get_joke())# шутка
        bot.answer_callback_query(call.id, "Pixelating your image...")
        pixelate_and_send(call.message)
    elif call.data == "invert":
        user_states[chat_id]['level'] = 2
        bot.send_message(chat_id, jokes.get_joke())#шутка
        bot.answer_callback_query(call.id, "Inversion your image...")
        pixelate_and_send(call.message)
    elif call.data == "mirror":
        user_states[chat_id]['level'] = 4
        bot.send_message(chat_id, jokes.get_joke())
        bot.answer_callback_query(call.id, "Mirroring your image...")
        pixelate_and_send(call.message)
    elif call.data == "heatmap":
        user_states[chat_id]['level'] = 5
        bot.send_message(chat_id, jokes.get_joke())# ещё шутка
        bot.answer_callback_query(call.id, "Conversion to a heat map your image...")
        pixelate_and_send(call.message)
    elif call.data == "resize":
        user_states[chat_id]['level'] = 6
        bot.send_message(chat_id, jokes.get_joke()) # ещё одна случайная шутка
        bot.answer_callback_query(call.id, "Changing the size your image...")
        pixelate_and_send(call.message)
    elif call.data == "ascii":
        user_states[chat_id]['level'] = 3
        bot.send_message(chat_id, jokes.get_joke()) # и опять шутка
        user_states[chat_id]['ascii'] = True
        bot.reply_to(call.message, "Enter char for converting your image to ASCII art...")


def pixelate_and_send(message):
    """Пикселизирует изображение и отправляет его обратно пользователю."""
    photo_id = user_states[message.chat.id]['photo']
    file_info = bot.get_file(photo_id)
    downloaded_file = bot.download_file(file_info.file_path)

    image_stream = io.BytesIO(downloaded_file)
    image = Image.open(image_stream)
    if user_states.get(message.chat.id) and user_states[message.chat.id]['level'] == 1:
        pixelated = pixelate_image(image, 20)
    elif user_states.get(message.chat.id) and user_states[message.chat.id]['level'] == 2:
        pixelated = invert_colors(image)
    elif user_states.get(message.chat.id) and user_states[message.chat.id]['level'] == 4:
        pixelated = mirror_image(image)
    elif user_states.get(message.chat.id) and user_states[message.chat.id]['level'] == 5:
        pixelated = convert_to_heatmap(image)
    elif user_states.get(message.chat.id) and user_states[message.chat.id]['level'] == 6:
        pixelated = resize_for_sticker(image)
    output_stream = io.BytesIO()
    pixelated.save(output_stream, format="JPEG")
    output_stream.seek(0)
    bot.send_photo(message.chat.id, output_stream)


def ascii_and_send(message):
    """Преобразует изображение в ASCII-арт и отправляет результат в виде текстового сообщения."""
    photo_id = user_states[message.chat.id]['photo']
    file_info = bot.get_file(photo_id)
    downloaded_file = bot.download_file(file_info.file_path)

    image_stream = io.BytesIO(downloaded_file)
    ascii_art = image_to_ascii(image_stream)
    if user_states.get(message.chat.id) and user_states[message.chat.id]['level'] == 3:
        bot.send_message(message.chat.id, f"```\n{ascii_art}\n```", parse_mode="MarkdownV2")


"""Обработка сообщений, вызов функции ascii_and_send."""
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if user_states.get(message.chat.id) and user_states[message.chat.id]['ascii']:
        global ASCII_CHARS
        ASCII_CHARS = message.text
        ascii_and_send(message)


"""Бесконечный цыкл бота"""
bot.polling(none_stop=True)
