import telebot
from config import keys, TOKEN
from extensions import Converter, APIException, GetNoun
from telebot import types


bot = telebot.TeleBot(TOKEN)


# Клавиатура
def create_markup(base=None):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = []
    for i in keys.keys():
        if i != base:
            buttons.append(types.KeyboardButton(i.capitalize()))
    markup.add(*buttons)
    return markup


# склонение наименований валют
def get_decl(a, b, q):
    base_t = f"{GetNoun.get_noun(float(a.replace(',', '.')), keys[b][1], keys[b][2])} ({keys[b][0]})"
    quote_t = f"{keys[q][3]} ({keys[q][0]})"
    return base_t, quote_t


# Команды /start и /help
@bot.message_handler(commands=['start', 'help'])
def start(message: telebot.types.Message):
    user_name = message.from_user.full_name
    text = f"Привет, {user_name}!\n \
\nВведите запрос в следующем формате: \
\n<имя валюты> <в какую валюту перевести> <количество>, \
\nнапример:  доллар рубль 100 \
\nили воспользуйтесь командой:  /convert \
\nдля отображения кнопок.\n \
\nСписок доступных валют:  /values"
    bot.send_message(message.chat.id, text)


# Команда /values - список доступных валют
@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    text = "Доступные валюты:\n"
    for key in keys:
        text = '\n-  <b>'.join((text, key)) + '</b>     \n   <i>' + keys[key][0] + '  |  ' + keys[key][4] + '</i>'
    bot.send_message(message.chat.id, text, parse_mode='html')


# Команда /convert - конвертирование с помощью клавиатуры
@bot.message_handler(commands=['convert'])
def values(message: telebot.types.Message):
    text = "Выберите валюту, из которой нужно конвертировать:"
    bot.send_message(message.chat.id, text, reply_markup=create_markup())
    bot.register_next_step_handler(message, base_handler)


def base_handler(message: telebot.types.Message):
    base = message.text.strip().lower()
    text = "Выберите валюту, в которую нужно конвертировать:"
    bot.send_message(message.chat.id, text, reply_markup=create_markup(base))
    bot.register_next_step_handler(message, quote_handler, base)


def quote_handler(message: telebot.types.Message, base):
    quote = message.text.strip().lower()
    text = "Выберите количество конвертируемой валюты:"
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, amount_handler, base, quote)


def amount_handler(message: telebot.types.Message, base, quote):
    amount = message.text.strip()
    try:
        new_price = Converter.get_price(base, quote, amount)
    except APIException as e:
        bot.send_message(message.chat.id, f"Ошибка конвертации...\n{e}")
    else:
        quote_t = get_decl(amount, base, quote)[1]
        base_t = get_decl(amount, base, quote)[0]
        text = f"Цена {amount} {base_t} в {quote_t} = {round(new_price, 4)}"
        bot.send_message(message.chat.id, text)


# Обработка сообщений - запроса из 3-х параметров
@bot.message_handler(content_types=['text'])
def convert(message: telebot.types.Message):
    vals = message.text.lower().split()
    try:
        if len(vals) != 3:
            raise APIException("Количество параметров должно быть равно 3")
        b, q, a = map(str.lower, vals)
        total_base = Converter.get_price(*vals)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка ввода запроса...\n{e}")
    else:
        text = f"Цена {a} {get_decl(a, b, q)[0]} в {get_decl(a, b, q)[1]} = {round(total_base, 4)}"
        bot.send_message(message.chat.id, text)


bot.polling()
