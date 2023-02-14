import telebot
from telebot import types
import requests


bot = telebot.TeleBot('6013566509:AAFbarNxSocCg__ga225XCYj_fPiaHaIYc8')
chat_id = "-1001770638270"
information = ''
bot_api = "6013566509:AAFbarNxSocCg__ga225XCYj_fPiaHaIYc8"
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
    global information

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
        information = f"Имя:{name}\nУниверситет:{university}\nПредмет:{subject}\nВопрос:{purpose}"
        user = message.from_user.username
        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_function1(callback_obj: telebot.types.CallbackQuery):
    if callback_obj.data == "yes":
        bot.send_message(callback_obj.from_user.id, "Вы нажали на кнопку подтверждения. Ждите ответа от преподователя.")
        keyboard = telebot.types.InlineKeyboardMarkup()
        key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
        keyboard.add(key_yes)
        bot.send_message(chat_id, text=information, reply_markup=keyboard)
    else:
        bot.send_message(callback_obj.from_user.id, "Перезапустите бота и попытайтесь снова")
    bot.answer_callback_query(callback_query_id=callback_obj.id)








bot.polling(none_stop=True, interval=0)
