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


@bot.message_handler(content_types=['text'])

def get_text_messages(message):
    if message.text == "/start":
        bot.send_message(message.from_user.id, "Начинаем...")
        bot.send_message(message.from_user.id, 'Как тебя зовут?')
        bot.register_next_step_handler(message, step1)


@bot.callback_query_handler(func=lambda message: message == True)
# _______________________________________________________________________
def step1(message):  # Name Parse
    global name
    global object_message
    object_message = message
    name = message.text
    bot.send_message(message.from_user.id, 'В каком вузе учишься?')  # todo Варианты
    bot.register_next_step_handler(message, step2)

# ________________________________________________________________________

@bot.callback_query_handler(func=lambda message: message == True)
def step2(message):  # Name Parse
    global university
    university = message.text
    bot.send_message(message.from_user.id, 'С каким предметом тебе нужна помощь?')
    bot.register_next_step_handler(message, step3)

@bot.callback_query_handler(func=lambda message: message == True)
def step3(message):  # Name Parse
    global subject
    subject = message.text
    bot.send_message(message.from_user.id, 'Сформулируйте свой вопрос.')
    bot.register_next_step_handler(message, step4)

@bot.callback_query_handler(func=lambda message: message == True)
def step4(message):
    global purpose
    global information
    global text_message_confirmed
    purpose = message.text
    bot.send_message(message.from_user.id, "Ваш запрос создан, Проверьте информацию еще раз.")

    keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
    key_yes = types.InlineKeyboardButton(text='\U00002705', callback_data='yes')  # кнопка «Да»
    keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
    key_no = types.InlineKeyboardButton(text='\U0000274C', callback_data='no')
    keyboard.add(key_no)
    question = 'Тебя зовут '+name+' ты из ' + university + '.' + ' Твой вопрос '+purpose+' По '+subject+'?'
    information = f"Имя:{name}\nУниверситет:{university}\nПредмет:{subject}\nВопрос:{purpose}"
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'yes')
def callback_function1(callback_obj: telebot.types.CallbackQuery):
    global text_message_confirmed
    bot.send_message(callback_obj.from_user.id, f"Вы нажали на кнопку подтверждения\U0001F680. Ждите ответа от преподователя\U000023F3.")
    global customer_id
    customer_id = callback_obj.from_user.id
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='\U00002705', callback_data='confirm')
    keyboard.add(key_yes)
    bot.send_message(chat_id, text=information, reply_markup=keyboard)
    text_message_confirmed = callback_obj.message.id


@bot.callback_query_handler(func=lambda call: call.data == 'no')
def callback_function1(callback_obj: telebot.types.CallbackQuery):
    bot.send_message(callback_obj.from_user.id, "Запустите бота снова./start")


@bot.callback_query_handler(func=lambda call: call.data == 'confirm')
def callback_function1(callback_obj: telebot.types.CallbackQuery):
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Создать еще один запрос', callback_data='create_old_new')
    keyboard.add(key_yes)
    bot.send_message(customer_id,
                     f"{callback_obj.message.html_text}\nВаш заказ был взят нашим специалистом\U0001F973\nКонтакт специалиста"
                     f"\U0001F4F2 :@"
                     f"{callback_obj.from_user.username}",
                     reply_markup=keyboard)

    bot.send_message(chat_id, text=f"{callback_obj.message.html_text}\nДанный заказ был взят пользователем\U0001F60E\n @"
                                   f"{callback_obj.from_user.username}")
    bot.delete_message(chat_id, callback_obj.message.id)


@bot.callback_query_handler(func=lambda call: call.data == 'create_old_new')
def callback_function1(callback_obj: telebot.types.CallbackQuery):
    bot.send_message(callback_obj.from_user.id, "Для создания нового запроса \U0001F503, отправьте /start")



bot.polling(none_stop=True, interval=0)
