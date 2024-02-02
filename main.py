import json
import telebot
import sqlite3
from telebot import types

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
    # Создание новой таблицы для хранения временных данных
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS temp_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER
    )
    ''')
    conn.commit()
    conn.close()

init_db()

# ...

# Добавление временной информации о студенте
def add_temp_data(student_id):
    conn = sqlite3.connect('bot_states.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO temp_data (student_id)
    VALUES (?)
    ''', (student_id,))
    conn.commit()
    conn.close()

# Получение временной информации о студенте
def get_temp_data():
    conn = sqlite3.connect('bot_states.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM temp_data ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return row[1]

# Удаление временной информации о студенте
def delete_temp_data():
    conn = sqlite3.connect('bot_states.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM temp_data')
    conn.commit()
    conn.close()


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
        buttons = [('English', 'en'), ('Russian', 'ru'), ('Czech', 'cs')]
        keyboard = create_keyboard(buttons)
        bot.send_message(message.from_user.id, 'Choose a language', reply_markup=keyboard)
        bot.register_next_step_handler(message, step1)


def create_keyboard(buttons):
    keyboard = types.InlineKeyboardMarkup()
    for text, callback_data in buttons:
        key = types.InlineKeyboardButton(text=text, callback_data=callback_data)
        keyboard.add(key)
    return keyboard


@bot.callback_query_handler(func=lambda call: call.data in ['en', 'ru', 'cs'])
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
def callback_confirm_from_student(callback_obj: telebot.types.CallbackQuery):
    user_id = callback_obj.from_user.id
    update_user_state(user_id, text_message_confirmed=1)
    add_temp_data(user_id)  # Добавляем user_id студента в temp_data
    bot.delete_message(user_id, callback_obj.message.id)
    user_state = get_user_state(user_id)
    bot.send_message(user_id, get_translation(user_state[1], 'confirm', user_state[7]))
    bot.send_message(user_id, text="Создайте новый(Для теста) Overflow'ов и Callback'ов. \nБлагодарю Diar(C).\nClick /start")
    buttons = [('\U00002705', 'confirm')]
    keyboard = create_keyboard(buttons)
    question = get_translation(user_state[1], 'information_template', user_state[7]).format(
        name=user_state[2],
        subject=user_state[4],
        university=user_state[3],
        purpose=user_state[5]
    )
    bot.send_message(chat_id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'confirm')
def callback_final_confirm_from_teacher_contact(callback_obj: telebot.types.CallbackQuery):
    try:
        student_id = get_temp_data()
        delete_temp_data()
        if student_id is None:
            raise Exception("No student data found")

        student_state = get_user_state(student_id)

        # обновляем сообщение, убирая кнопку и добавляя username преподавателя
        new_text = f"{callback_obj.message.text}\nЗаказ принят пользователем: @{callback_obj.from_user.username}"
        bot.edit_message_text(chat_id=callback_obj.message.chat.id,
                              message_id=callback_obj.message.message_id,
                              text=new_text)

        # получаем переводы
        teacher_confirm = get_translation(student_state[1], 'confirm', student_state[7])
        contact_teacher = get_translation(student_state[1], 'contact_teacher', student_state[7]).format(
            teacher_id=callback_obj.from_user.username)

        # сообщение для студента
        student_info = get_translation(student_state[1], 'information_template', student_state[7]).format(
            name=student_state[2],
            university=student_state[3],
            subject=student_state[4],
            purpose=student_state[5]
        )

        # сообщение для студента, объединяющее информацию о запросе и контакте учителя
        student_message = f"{student_info}\n{contact_teacher}\n"

        # отправляем сообщение студенту
        bot.send_message(student_id, text=student_message)

    except Exception as e:
        bot.send_message(callback_obj.from_user.id, text=f"FAILURE {e} Перезапустите бота")

@bot.callback_query_handler(func=lambda call: call.data == 'no')
def callback_deny_from_student(callback_obj: telebot.types.CallbackQuery):
    bot.send_message(callback_obj.from_user.id, "Restart./start")


@bot.callback_query_handler(func=lambda call: call.data == 'create_old_new')
def callback_create_old_new(callback_obj: telebot.types.CallbackQuery):
    bot.send_message(callback_obj.from_user.id, text='Click /start')


bot.polling(none_stop=True, interval=0)