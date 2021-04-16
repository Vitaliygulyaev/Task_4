import telebot
import sqlite3
import json
from newsapi import NewsApiClient



bot = telebot.TeleBot("1730501335:AAFrbz7qCMIn0P98pVmYRXK_GzadcJfd2AI")
newsapi = NewsApiClient(api_key='e8f7d068fabb4bc99ae318f05f7b1829')

@bot.message_handler(commands = ['start'])
def send_welcome(message):
	first_name = message.from_user.first_name
	bot.send_message(message.chat.id, "Привет,"+str(first_name)+"!"+"\n"+
									"Я - Кремлебот Владимир Соловьев. Вот что могу тебе предложить: ")
	bot.send_message(message.chat.id, "/goTo - присоединиться к нам!"+"\n"+
									"/choose_news_categories - выбрать категории Новостей (желательно ченить про загнивающий запад и хохлов)"+"\n"+
									"/get_news - Вывести 10 релевантных новостей по моим подпискам"+"\n"+
									"/remove_categories - посмотреть/удалить активные подписки на категории новостей"+"\n"+
									"/remove_keywords - посмотреть/удалить активные подписки по ключевым словам")
	
@bot.message_handler(commands = ['goTo'])
def autentification_user(message):
	user_id = message.from_user.id
	first_name = message.from_user.first_name
	last_name = message.from_user.last_name
	registration_to_db(user_id, first_name, last_name)

@bot.message_handler(commands=['choose_news_categories'])
def choose_news_categories(message):
	try:
		user_id = message.from_user.id
		conn = sqlite3.connect('newsdb.db')
		cur = conn.cursor()
		cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id, ))
		u_id = cur.fetchone()
		if u_id is None:
			bot.send_message(message.chat.id, 'Введи команду /goTo для регистрации')
		else:
			keyboard = telebot.types.ReplyKeyboardMarkup()
			keyboard.row(
				telebot.types.KeyboardButton("Бизнес"),
				telebot.types.KeyboardButton("Спорт"),
				telebot.types.KeyboardButton("Технологии")
			)
			keyboard.row(
				telebot.types.KeyboardButton("Здоровье"),
				telebot.types.KeyboardButton("Наука")
			)
			keyboard.row(
				telebot.types.KeyboardButton("Главные новости"),
				telebot.types.KeyboardButton("Развлечения")
			)
			keyboard.row(
				telebot.types.KeyboardButton("Завершить выбор категорий")
			)
			bot.send_message(message.chat.id, "Выберите желаемые категории новостей:", reply_markup=keyboard)
	except sqlite3.IntegrityError:
		pass
	finally:
		conn.close()


@bot.message_handler(commands=['get_news'])
def get_news(message):
	users_id = message.from_user.id
	try:
		conn = sqlite3.connect('newsdb.db')
		cur = conn.cursor()
		cur.execute("SELECT user_id FROM users WHERE user_id = ?", (users_id, ))
		u_id = cur.fetchone()
		if u_id is None:
			bot.send_message(message.chat.id, 'Введи команду /goTo для регистрации')
		else:
			cur.execute("SELECT Category FROM users_categories WHERE user_id = ?", (users_id, ))
			categories = cur.fetchall()
			conn.close()
			conn = sqlite3.connect('newsdb.db')
			cur = conn.cursor()
			cur.execute("SELECT Keyword FROM keywords WHERE user_id = ?", (users_id, ))
			keywords = cur.fetchall()
			conn.close()
			news_url = []
			for cate in categories:
				for key in keywords:
					top_headLines = newsapi.get_top_headlines(category=cate[0],q=key[0], language='ru')
					new_data = top_headLines
					for data in new_data['articles']:
						news_url.append(data["url"])
			for key in keywords:
				top_headLines = newsapi.get_top_headlines(q=key[0], language='ru')
				new_data = top_headLines
				for data in new_data['articles']:
					news_url.append(data["url"])
			for cate in categories:
				top_headLines = newsapi.get_top_headlines(category=cate[0], language='ru')
				new_data = top_headLines
				for data in new_data['articles']:
					news_url.append(data["url"])
		count = 0
		while count != 10:
			bot.send_message(message.chat.id, news_url[count])
			count+=1
	except sqlite3.IntegrityError:
		pass

@bot.message_handler(commands=['remove_categories'])
def remove_keyboard(message):
	user_id = message.from_user.id
	keyboard = make_keyboard(user_id)
	bot.send_message(message.chat.id, "Выберите категории для удаления:", reply_markup=keyboard)

def make_keyboard(user_id):
	conn = sqlite3.connect("newsdb.db")
	cur = conn.cursor()
	cur.execute("SELECT Category FROM users_categories WHERE user_id=?", (user_id, ))
	categories = cur.fetchall()
	keyboard = telebot.types.InlineKeyboardMarkup()
	for i in categories:
		if i[0] == "business":
			keyboard.add(telebot.types.InlineKeyboardButton(text="Бизнес", callback_data=i[0]))		
		elif i[0] == "sports":
			keyboard.add(telebot.types.InlineKeyboardButton(text="Спорт", callback_data=i[0]))
		elif i[0] == "technology":
			keyboard.add(telebot.types.InlineKeyboardButton(text="Технологии", callback_data=i[0]))
		elif i[0] == "health":
			keyboard.add(telebot.types.InlineKeyboardButton(text="Здоровье", callback_data=i[0]))
		elif i[0] == "science":
			keyboard.add(telebot.types.InlineKeyboardButton(text="Наука", callback_data=i[0]))
		elif i[0] == "entertainment":
			keyboard.add(telebot.types.InlineKeyboardButton(text="Развлечения", callback_data=i[0]))
		elif i[0] == "general":
			keyboard.add(telebot.types.InlineKeyboardButton(text="Главные новости", callback_data=i[0]))
		else:
			pass
	keyboard.add(telebot.types.InlineKeyboardButton(text="Завершить редактирование", callback_data="del_stop"))
	conn.close()
	return keyboard

def make_keyword_keyboard(user_id):
	conn = sqlite3.connect("newsdb.db")
	cur = conn.cursor()
	cur.execute("SELECT Keyword FROM keywords WHERE user_id=?", (user_id, ))
	keywords = cur.fetchall()
	keyboard = telebot.types.InlineKeyboardMarkup()
	for i in keywords:
		keyboard.add(telebot.types.InlineKeyboardButton(text=i[0], callback_data='keywords '+i[0]))
	keyboard.add(telebot.types.InlineKeyboardButton(text="Завершить редактирование списка ключевых слов", callback_data="stop_remove_keywords"))
	conn.close()
	return keyboard

@bot.message_handler(commands=['remove_keywords'])
def get_keywords(message):
	user_id = message.from_user.id
	keyboard_key = make_keyword_keyboard(user_id)
	bot.send_message(message.chat.id, text="Выберите от каких категорий отписаться:", reply_markup=keyboard_key)


@bot.callback_query_handler(func=lambda call: True)
def remove_keywords(call):
	print(call.data)
	if call.data == "stop_remove_keywords":
		bot.delete_message(chat_id=call.message.chat.id, message_id = call.message.message_id)
	elif call.data == "del_stop":
		bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
	elif call.data.startswith('keywords '):
		user_id = call.from_user.id
		conn = sqlite3.connect("newsdb.db")
		cur = conn.cursor()
		call.data = call.data.replace("keywords ", "")
		cur.execute("DELETE FROM keywords WHERE user_id=? AND Keyword=?", (user_id, call.data))
		conn.commit()
		bot.edit_message_text(chat_id=call.message.chat.id, message_id = call.message.message_id, text="Выберите от каких ключевых фраз отписаться:", reply_markup=make_keyword_keyboard(user_id))
		conn.close()
	else:
		user_id = call.from_user.id
		conn = sqlite3.connect('newsdb.db')
		cur = conn.cursor()
		cur.execute('DELETE FROM users_categories WHERE user_id = ? AND Category = ?', (user_id, call.data))
		conn.commit()
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Выберите от каких категорий отписаться:', reply_markup=make_keyboard(user_id))
		conn.close()

def input_lines(user_id, message):
	print(message.text)
	if message.text == "Бизнес":
		category = "business"
		insert_category(user_id, category)
	elif message.text == "Спорт":
		category = "sports"
		insert_category(user_id, category)
	elif message.text == "Технологии":
		category = "technology"
		insert_category(user_id, category)
	elif message.text == "Здоровье":
		category = "health"
		insert_category(user_id, category)
	elif message.text == "Наука":
		category = "science"
		insert_category(user_id, category)
	elif message.text == "Развлечения":
		category = "entertainment"
		insert_category(user_id, category)
	elif message.text == "Главные новости":
		category = "general"
		insert_category(user_id, category)
	elif message.text == "Завершить выбор категорий":
		bot.send_message(message.chat.id, "Выбор категорий завершен...", reply_markup=telebot.types.ReplyKeyboardRemove())
	elif message.text[0:1] == "#":
		conn = sqlite3.connect("newsdb.db")
		cur = conn.cursor()
		cur.execute("INSERT INTO keywords(Keyword, user_id) VALUES(?, ?);", (message.text[1:], user_id))
		conn.commit()
		conn.close()
	else:
		pass


@bot.message_handler(content_types=['text'])
def choosen_news_categories(message):
	user_id = message.from_user.id
	input_lines(user_id, message)


def insert_category(user_id, category):
	try:
		conn = sqlite3.connect("newsdb.db")
		cur = conn.cursor()
		cur.execute("SELECT category_id FROM categories WHERE Category = ?", (category,))
		category_id = cur.fetchone()
		cur.execute("INSERT INTO users_categories(user_id, category_id, Category) VALUES(?,?,?);", (user_id, category_id[0], category))
		conn.commit()
		conn.close()
	except sqlite3.IntegrityError:
		pass

# Запись нового пользователя в БД
def registration_to_db(user_id, first_name, last_name):
	user = (user_id, first_name, last_name)
	try:
		conn = sqlite3.connect("newsdb.db")
		cur = conn.cursor()
		cur.execute("INSERT INTO users(user_id, FirstName, SecondName) VALUES(?, ?, ?);", user)
		conn.commit()
	except sqlite3.IntegrityError:
		pass
	finally:
		conn.close()

bot.polling()