import json
import telebot
from telebot import types


bot = telebot.TeleBot('6013566509:AAFbarNxSocCg__ga225XCYj_fPiaHaIYc8')
chat_id = "-1001770638270"
information = ''
bot_api = "6013566509:AAFbarNxSocCg__ga225XCYj_fPiaHaIYc8"
name = ''
university = ''
subject = ''
purpose = 'None'
object_message = ''
customer_id = 0
text_message_confirmed = 0
user_language = ''
filepath = 'languages.json'


def get_translation(language, key, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        translations = json.load(file)
    return translations.get(language, {}).get(key, f"No translation found for language '{language}' and key '{key}'")



@bot.message_handler(content_types=['text', 'photo'])
def get_text_messages(message):
    if message.text == "/start":
        bot.send_message(message.from_user.id, "Starting...")

        keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
        key_en = types.InlineKeyboardButton(text='English', callback_data='en')  # кнопка «Да»
        keyboard.add(key_en)  # добавляем кнопку в клавиатуру
        key_ru = types.InlineKeyboardButton(text='Russian', callback_data='ru')
        keyboard.add(key_ru)
        key_ru = types.InlineKeyboardButton(text='Czech', callback_data='cs')
        keyboard.add(key_ru)
        key_ru = types.InlineKeyboardButton(text='Italian', callback_data='it')
        keyboard.add(key_ru)
        bot.send_message(message.from_user.id, 'Choose a language', reply_markup=keyboard)
        bot.register_next_step_handler(message, step1)

@bot.callback_query_handler(func=lambda call: call.data == 'en' or call.data=='ru' or call.data=='cs'
                                              or call.data == 'it')
def callback_function1(callback_obj: telebot.types.CallbackQuery):
    global user_language
    user_language = callback_obj.data
    bot.delete_message(callback_obj.from_user.id, callback_obj.message.id)
    bot.send_message(callback_obj.from_user.id, get_translation(user_language, 'start', filepath))

@bot.callback_query_handler(func=lambda message: message == True)
# _______________________________________________________________________
def step1(message):  # Name Parse
    global name
    global object_message
    object_message = message
    name = message.text
    bot.send_message(message.from_user.id, get_translation(user_language, 'university', filepath))
    bot.register_next_step_handler(message, step2)

# ________________________________________________________________________


@bot.callback_query_handler(func=lambda message: message == True)
def step2(message):  # Name Parse
    global university
    university = message.text
    bot.send_message(message.from_user.id, get_translation(user_language, 'subject', filepath))
    bot.register_next_step_handler(message, step3)


@bot.callback_query_handler(func=lambda message: message == True)
def step3(message):  # Name Parse
    global subject
    subject = message.text
    bot.send_message(message.from_user.id, get_translation(user_language, 'purpose', filepath))
    bot.register_next_step_handler(message, step4)


@bot.callback_query_handler(func=lambda message: message == True)
def step4(message):
    global purpose
    global information
    global text_message_confirmed
    global question
    purpose = message.text


    keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
    key_yes = types.InlineKeyboardButton(text='\U00002705', callback_data='yes')  # кнопка «Да»
    keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
    key_no = types.InlineKeyboardButton(text='\U0000274C', callback_data='no')
    keyboard.add(key_no)
    question = get_translation(user_language, 'information_template', filepath).format(
                         name=name,
                         subject=subject,
                         university=university,
                         purpose=purpose
                     )
    bot.send_message(message.from_user.id,
                     text=get_translation(user_language, 'confirm_message_to_user', filepath).format(
                         name=name,
                         subject=subject,
                         university=university,
                         purpose=purpose
                     ),
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'yes')
def callback_function1(callback_obj: telebot.types.CallbackQuery):
    global text_message_confirmed
    bot.send_message(callback_obj.from_user.id, text=get_translation(user_language, 'confirm', filepath))
    global customer_id
    customer_id = callback_obj.from_user.id
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='\U00002705', callback_data='confirm')
    keyboard.add(key_yes)
    bot.send_message(chat_id, text=question, reply_markup=keyboard)
    text_message_confirmed = callback_obj.message.id


@bot.callback_query_handler(func=lambda call: call.data == 'no')
def callback_function1(callback_obj: telebot.types.CallbackQuery):
    bot.send_message(callback_obj.from_user.id, "Запустите бота снова./start")


@bot.callback_query_handler(func=lambda call: call.data == 'confirm')
def callback_function1(callback_obj: telebot.types.CallbackQuery):
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text=get_translation(user_language, 'new_order', filepath),
                                         callback_data='create_old_new')
    keyboard.add(key_yes)
    bot.send_message(customer_id,
                     text=f"{question}\n{get_translation(user_language, 'contact_teacher', filepath).format(teacher_id=callback_obj.from_user.username)}", # noqa
                     reply_markup=keyboard)

    bot.send_message(chat_id, text=f"{callback_obj.message.html_text}\n{ get_translation(user_language, 'booked_order', filepath).format(teacher_id=callback_obj.from_user.username) }")  # noqa
    bot.delete_message(chat_id, callback_obj.message.id)


@bot.callback_query_handler(func=lambda call: call.data == 'create_old_new')
def callback_function1(callback_obj: telebot.types.CallbackQuery):
    bot.send_message(callback_obj.from_user.id, text='Click /start')


bot.polling(none_stop=True, interval=0)
