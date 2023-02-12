import telebot
from telebot import types


bot = telebot.TeleBot('6013566509:AAFbarNxSocCg__ga225XCYj_fPiaHaIYc8')
name = ''
university = ''
subject = ''
purpose = 'None'

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/start":
        bot.send_message(message.from_user.id, "Начинаем...")
        bot.send_message(message.from_user.id, 'Как тебя зовут?')
        bot.register_next_step_handler(message, step1)


# _______________________________________________________________________
def step1(message): # Name Parse
    global name
    name = message.text
    bot.send_message(message.from_user.id, 'В каком вузе учишься?') #todo Варианты
    bot.register_next_step_handler(message, step2)
# ________________________________________________________________________


def step2(message): # Name Parse
    global university
    university = message.text
    bot.send_message(message.from_user.id, 'С каким предметом тебе нужна помощь?')
    bot.register_next_step_handler(message, step3)

def step3(message): # Name Parse
    global subject
    subject = message.text
    bot.send_message(message.from_user.id, 'Сформулируйте свой вопрос.')
    bot.register_next_step_handler(message, step4)

def step4(message):
    global purpose

    while purpose == 'None' :  # проверяем что возраст изменился
        try:
            purpose = message.text
            bot.send_message(message.from_user.id, "Ваш запрос создан, Проверьте информаци еще раз.")
        except Exception:
            bot.send_message(message.from_user.id, 'Введите данные корректно')
        keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
        key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')  # кнопка «Да»
        keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
        key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
        keyboard.add(key_no)
        question = 'Тебя зовут '+name+' ты из ' + university + '.' + ' Твой вопрос '+purpose+' По '+subject+'?'
        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes":  # call.data это callback_data, которую мы указали при объявлении кнопки
        bot.send_message(call.message.chat.id, 'Ваш запрос принят, ожидайте ответа.')
    elif call.data == "no":
         ...




bot.polling(none_stop=True, interval=0)
