import telebot
from telebot import types
import sqlite3

bot = telebot.TeleBot('token')

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"Hello, {message.from_user.first_name}!")
    
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
        id integer,
        username text,
        BTCBalance integer,
        ETHBalance integer,
        TRXBalance integer
    )
    """)
    
    people_id = message.chat.id
    cursor.execute(f"SELECT id FROM users WHERE id = {people_id}")
    data = cursor.fetchone()
    if data is None:
        new_user = (people_id, message.from_user.username, 0, 0, 0)
        cursor.execute(f"INSERT INTO users VALUES(?, ?, ?, ?, ?)", new_user)
    else:
        bot.send_message(people_id, "Пользователь существует!")

    connect.commit()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu = types.KeyboardButton('Menu')
    wallet = types.KeyboardButton('Wallet')
    markup.add(menu, wallet)

    bot.send_message(people_id, "Выбери пункт меню", reply_markup=markup)

def d_btc_review(message):
    try:
        send_amount = int(message.text)
        bot.send_message(message.chat.id, f"Send {message.text} BTC to the address:")
        bot.send_message(message.chat.id, "0xbhIUylHYLbuFytiyTFkyugGyubYUgubYg")
    except ValueError:
        mess = bot.send_message(message.chat.id, "Please, type a number!")
        bot.register_next_step_handler(mess, d_btc_review)

def d_eth_review(message):
    try:
        send_amount = int(message.text)
        bot.send_message(message.chat.id, f"Send {message.text} ETH to the address:")
        bot.send_message(message.chat.id, "0xbhIUylHYLbuFytiyTFkyugGyubYUgubYg")
    except ValueError:
        mess = bot.send_message(message.chat.id, "Please, type a number!")
        bot.register_next_step_handler(mess, d_eth_review)

def d_trx_review(message):
    try:
        send_amount = int(message.text)
        bot.send_message(message.chat.id, f"Send {message.text} TRX to the address:")
        bot.send_message(message.chat.id, "0xbhIUylHYLbuFytiyTFkyugGyubYUgubYg")
    except ValueError:
        mess = bot.send_message(message.chat.id, "Please, type a number!")
        bot.register_next_step_handler(mess, d_trx_review)

def w_btc_review(message):
    try:
        send_amount = int(message.text)
        mess = bot.send_message(message.chat.id, "Type address:")
        bot.register_next_step_handler(mess, withdraw_btc)
    except ValueError:
        mess = bot.send_message(message.chat.id, "Please, type a number!")
        bot.register_next_step_handler(mess, w_btc_review)

def withdraw_btc(message):
    bot.send_message(message.chat.id, "Ok")

def transaction(message, name):
    sender = message.from_user.username
    try:
        send_amount = int(message.text)
        mess = bot.send_message(message.chat.id, "Type username:")
        bot.register_next_step_handler(mess, transfer(message, amount, name, sender))
    except ValueError:
        mess = bot.send_message(message.chat.id, "Please, type a number!")
        bot.register_next_step_handler(mess, transaction)

def transfer(message, _amount, _name, _sender):
    username = message.text
    amount = _amount
    name = _name
    sender = _sender

    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()

    cursor.execute(f"SELECT {name}Balance FROM users WHERE username = {username}")
    old_balance = int(cursor.fetchone())
    new_balance = old_balance + amount
    cursor.execute(f"UPDATE users SET {name}Balance = {new_balance} WHERE username = {username}")
    connect.commit()

    cursor.execute(f"SELECT id FROM users WHERE username = {username}")
    chat_id = cursor.fetchone()
    bot.send_message(chat_id, f"User {sender} sent you {amount} {name}")

    



@bot.message_handler(commands=['delete'])
def delete(message):
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    people_id = message.chat.id
    cursor.execute(f"DELETE FROM users WHERE id = {people_id}")
    connect.commit()

    bot.send_message(people_id, "Вы были удалены из базы")

@bot.message_handler(content_types=['text'])
def user_message(message):
    if message.text == 'Wallet':
        wallet_markup = types.InlineKeyboardMarkup()
        deposit = types.InlineKeyboardButton(text='Deposit', callback_data='deposit')
        withdraw = types.InlineKeyboardButton(text='Withdraw', callback_data='withdraw')
        transaction = types.InlineKeyboardButton(text='Transaction', callback_data='transaction')
        wallet_markup.add(deposit, withdraw, transaction)
        bot.send_message(message.chat.id, f'<b>Your wallet:</b> \n 0 BTC \n 0 ETH \n 0 TRX', parse_mode='html', reply_markup=wallet_markup)
    elif message.text == 'Menu':
        bot.send_message(message.chat.id, "This section is still under development")


@bot.callback_query_handler(func = lambda call: True)
def answer(call):
    if call.data == 'deposit':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        currency_markup = types.InlineKeyboardMarkup()
        btc = types.InlineKeyboardButton(text='BTC', callback_data='deposit_btc')
        eth = types.InlineKeyboardButton(text='ETH', callback_data='deposit_eth')
        trx = types.InlineKeyboardButton(text='TRX', callback_data='deposit_trx')
        currency_markup.add(btc, eth, trx)
        bot.send_message(call.message.chat.id, 'Select a currency:', reply_markup=currency_markup)

    elif call.data == 'deposit_btc':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        mess = bot.send_message(call.message.chat.id, 'Type amount:')
        bot.register_next_step_handler(mess, d_btc_review)
    elif call.data == 'deposit_eth':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        mess = bot.send_message(call.message.chat.id, 'Type amount:')
        bot.register_next_step_handler(mess, d_eth_review)
    elif call.data == 'deposit_trx':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        mess = bot.send_message(call.message.chat.id, 'Type amount:')
        bot.register_next_step_handler(mess, d_trx_review)

    elif call.data == 'withdraw':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        currency_markup = types.InlineKeyboardMarkup()
        btc = types.InlineKeyboardButton(text='BTC', callback_data='withdraw_btc')
        eth = types.InlineKeyboardButton(text='ETH', callback_data='withdraw_eth')
        trx = types.InlineKeyboardButton(text='TRX', callback_data='withdraw_trx')
        currency_markup.add(btc, eth, trx)
        bot.send_message(call.message.chat.id, 'Select a currency:', reply_markup=currency_markup)

    elif call.data == 'withdraw_btc':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        mess = bot.send_message(call.message.chat.id, 'Type amount:')
        bot.register_next_step_handler(mess, w_btc_review)
    elif call.data == 'withdraw_eth':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        mess = bot.send_message(call.message.chat.id, 'Type amount:')
        bot.register_next_step_handler(mess, w_btc_review)
    elif call.data == 'withdraw_trx':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        mess = bot.send_message(call.message.chat.id, 'Type amount:')
        bot.register_next_step_handler(mess, w_btc_review)

    elif call.data == 'transaction':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        transaction_markup = types.InlineKeyboardMarkup()
        btc = types.InlineKeyboardButton(text='BTC', callback_data='send_btc')
        eth = types.InlineKeyboardButton(text='ETH', callback_data='send_eth')
        trx = types.InlineKeyboardButton(text='TRX', callback_data='send_trx')
        transaction_markup.add(btc, eth, trx)
        mess = bot.send_message(call.message.chat.id, 'Select currency:', reply_markup=transaction_markup)
        # bot.register_next_step_handler(mess, w_btc_review)

    elif call.data == 'send_btc':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        mess = bot.send_message(call.message.chat.id, 'Type amount:')
        bot.register_next_step_handler(mess, transaction(message=message, name="BTC"))
    elif call.data == 'send_eth':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        mess = bot.send_message(call.message.chat.id, 'Type amount:')
        bot.register_next_step_handler(mess, transaction(message=message, name="ETH"))
    elif call.data == 'send_trx':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        mess = bot.send_message(call.message.chat.id, 'Type amount:')
        bot.register_next_step_handler(mess, transaction(message=message, name="TRX"))

if __name__ == '__main__': # чтобы код выполнялся только при запуске в виде сценария, а не при импорте модуля
    try:
       bot.polling(none_stop=True) # запуск бота
    except Exception as e:
       print(e) # или import traceback; traceback.print_exc() для печати полной инфы
       time.sleep(15)


# @bot.message_handler(commands=['website'])
# def website(message):
#     markup = types.InlineKeyboardMarkup()
#     markup.add(types.InlineKeyboardButton('Visit website', url='https://youtube.com'))
#     bot.send_message(message.chat.id, 'Visit website', reply_markup=markup)

# @bot.message_handler(commands=['help'])
# def website(message):
#     markup = types.ReplyKeyboardMarkup()
#     start = types.KeyboardButton('Start')
#     website = types.KeyboardButton('Website')
#     markup.add(start, website)
#     bot.send_message(message.chat.id, 'Help', reply_markup=markup)


