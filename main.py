import json
import telebot
import sqlite3
from telebot import types



tmp = None
# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('bot_states.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bot_states (
        user_id INTEGER PRIMARY KEY,
        user_language TEXT,
        name TEXT,
        university TEXT,
        subject TEXT,
        purpose TEXT,
        text_message_confirmed INTEGER,
        filepath TEXT DEFAULT 'languages.json'
    )
    ''')
    conn.commit()
    conn.close()


init_db()


def get_user_state(user_id):
    conn = sqlite3.connect('bot_states.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bot_states WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return create_new_user_state(user_id)
    return row


def create_new_user_state(user_id):
    conn = sqlite3.connect('bot_states.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO bot_states (user_id, user_language, name, university, subject, purpose, text_message_confirmed)
    VALUES (?, '', '', '', '', '', 0)
    ''', (user_id,))
    conn.commit()
    conn.close()
    return get_user_state(user_id)


def update_user_state(user_id, **kwargs):
    conn = sqlite3.connect('bot_states.db')
    cursor = conn.cursor()
    update_columns = ', '.join(f'{k} = ?' for k in kwargs)
    cursor.execute(f'''
    UPDATE bot_states
    SET {update_columns}
    WHERE user_id = ?
    ''', (*kwargs.values(), user_id))
    conn.commit()
    conn.close()


def get_translation(language, key, filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            translations = json.load(file)
        return translations.get(language, {}).get(key,
                                                  f"No translation found for language '{language}' and key '{key}'")
    except FileNotFoundError:
        return "Translation file not found."


# ...

# Ваш токен и chat_id
bot_token = "6013566509:AAEnUPgalbDUStLkWk6KsUQPv0wDsMczZfY"
chat_id = '-1001770638270'
bot = telebot.TeleBot(bot_token)


@bot.message_handler(content_types=['text', 'photo'])
def get_text_messages(message):
    user_state = get_user_state(message.from_user.id)
    if message.text == "/start":
        bot.send_message(message.from_user.id, "Starting...")
        buttons = [('English', 'en'), ('Russian', 'ru'), ('Czech', 'cs'), ('Italian', 'it')]
        keyboard = create_keyboard(buttons)
        bot.send_message(message.from_user.id, 'Choose a language', reply_markup=keyboard)
        bot.register_next_step_handler(message, step1)


def create_keyboard(buttons):
    keyboard = types.InlineKeyboardMarkup()
    for text, callback_data in buttons:
        key = types.InlineKeyboardButton(text=text, callback_data=callback_data)
        keyboard.add(key)
    return keyboard


@bot.callback_query_handler(func=lambda call: call.data in ['en', 'ru', 'cs', 'it'])
def callback_function1(callback_obj: telebot.types.CallbackQuery):
    update_user_state(callback_obj.from_user.id, user_language=callback_obj.data)
    bot.delete_message(callback_obj.from_user.id, callback_obj.message.id)
    user_state = get_user_state(callback_obj.from_user.id)
    bot.send_message(callback_obj.from_user.id, get_translation(user_state[1], 'start', user_state[7]))


def step1(message):
    update_user_state(message.from_user.id, name=message.text)
    user_state = get_user_state(message.from_user.id)
    bot.send_message(message.from_user.id, get_translation(user_state[1], 'university', user_state[7]))
    bot.register_next_step_handler(message, step2)


def step2(message):
    update_user_state(message.from_user.id, university=message.text)
    user_state = get_user_state(message.from_user.id)
    bot.send_message(message.from_user.id, get_translation(user_state[1], 'subject', user_state[7]))
    bot.register_next_step_handler(message, step3)


def step3(message):
    update_user_state(message.from_user.id, subject=message.text)
    user_state = get_user_state(message.from_user.id)
    bot.send_message(message.from_user.id, get_translation(user_state[1], 'purpose', user_state[7]))
    bot.register_next_step_handler(message, step4)


def step4(message):
    update_user_state(message.from_user.id, purpose=message.text)
    user_state = get_user_state(message.from_user.id)
    buttons = [('\U00002705', 'yes'), ('\U0000274C', 'no')]
    keyboard = create_keyboard(buttons)
    question = get_translation(user_state[1], 'information_template', user_state[7]).format(
        name=user_state[2],
        subject=user_state[4],
        university=user_state[3],
        purpose=user_state[5]
    )
    bot.send_message(message.from_user.id,
                     text=get_translation(user_state[1], 'confirm_message_to_user', user_state[7]).format(
                         name=user_state[2],
                         subject=user_state[4],
                         university=user_state[3],
                         purpose=user_state[5]
                     ),
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'yes')
def callback_confirm(callback_obj: telebot.types.CallbackQuery):
    update_user_state(callback_obj.from_user.id, text_message_confirmed=1)
    bot.delete_message(callback_obj.from_user.id, callback_obj.message.id)
    user_state = get_user_state(callback_obj.from_user.id)
    bot.send_message(callback_obj.from_user.id, get_translation(user_state[1], 'confirm', user_state[7]))
    buttons = [('\U00002705', 'confirm')]
    keyboard = create_keyboard(buttons)
    question = get_translation(user_state[1], 'information_template', user_state[7]).format(
        name=user_state[2],
        subject=user_state[4],
        university=user_state[3],
        purpose=user_state[5]
    )
    bot.send_message(chat_id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'no')
def callback_deny(callback_obj: telebot.types.CallbackQuery):
    bot.send_message(callback_obj.from_user.id, "Запустите бота снова./start")


@bot.callback_query_handler(func=lambda call: call.data == 'confirm')
def callback_final_confirm(callback_obj: telebot.types.CallbackQuery):
    try:
        user_state = get_user_state(callback_obj.from_user.id)
        buttons = [(get_translation(user_state[1], 'new_order', user_state[7]), 'create_old_new')]
        keyboard = create_keyboard(buttons)
        bot.send_message(callback_obj.from_user.id,
                         text=f"{callback_obj.message.text}\n{get_translation(user_state[1], 'contact_teacher', user_state[7]).format(teacher_id=callback_obj.from_user.username)}",
                         reply_markup=keyboard)
        tmp = callback_obj.from_user.id
        callback_obj.from_user.id = None
        bot.send_message(chat_id,
                         text=f"{callback_obj.message.html_text}\n{get_translation(user_state[1], 'booked_order', user_state[7]).format(teacher_id=callback_obj.from_user.username)}")
        bot.delete_message(chat_id, callback_obj.message.id)
    except Exception as e:
        bot.send_message(tmp, text = f"FAILUER {e} Перезапустите бота")
        pass


@bot.callback_query_handler(func=lambda call: call.data == 'create_old_new')
def callback_create_old_new(callback_obj: telebot.types.CallbackQuery):
    bot.send_message(callback_obj.from_user.id, text='Click /start')


bot.polling(none_stop=True, interval=0)