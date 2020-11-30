import sys
import telebot
import pymysql
from config import dbHost, dbUser, dbPassword, dbName

bot = telebot.TeleBot("1284478312:AAFtAyo3ttPW_mWs07q7uhya2JFiekmmF9o")

try:
    connection = pymysql.connect(dbHost, dbUser, dbPassword, dbName)
except pymysql.connect.Error as err:
    if err.errno == err.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
        sys.exit()
    elif err.errno == err.ER_BAD_DB_ERROR:
        print("Database does not exist")
        sys.exit()
    else:
        print(err)
        sys.exit()

cursor = connection.cursor()

cursor.execute("SHOW DATABASES")

for x in cursor:
    print(x)

cursor.execute("CREATE TABLE users (first_name VARCHAR(255), last_name VARCHAR(255))")

cursor.execute("SHOW TABLES")

for x in cursor:
    print(x)

cursor.execute("ALTER TABLE users ADD COLUMN (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT UNIQUE)")

sql = "INSERT INTO users (first_name, last_name, user_id) VALUES (%s, %s, %s)"
val = ("Orlov", "Daniil", 1)
cursor.execute(sql, val)
connection.commit()

print(cursor.rowcount, "запись добавлена.")

sql = "INSERT INTO users (first_name, last_name, user_id) VALUES (%s, %s, %s)"
val = [
    ('Nikita', 'Ivanov', 2),
]

cursor.executemany(sql, val)
connection.commit()

print(cursor.rowcount, "записи были добавлены.")

user_data = {}


######## JOIN ############################
cursor.execute("CREATE TABLE user_groups (id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(255))")
sql = "INSERT INTO user_groups (title) VALUES (%s)"
val = [('Администратор',), ('Модератор',), ('Пользователь',)]

cursor.executemany(sql, val)
connection.commit()

cursor.execute("ALTER TABLE users ADD COLUMN (user_group_id INT)")

sql = "SELECT \
    users.first_name AS user, \
    user_groups.title AS user_group \
    FROM users \
    JOIN user_groups ON users.user_group_id = user_groups.id"

cursor.execute(sql)
users = cursor.fetchall()

for user in users:
    print(user)

sql = "SELECT \
    users.first_name AS user, \
    user_groups.title AS user_group \
    FROM users \
    LEFT JOIN user_groups ON users.user_group_id = user_groups.id"

cursor.execute(sql)
users = cursor.fetchall()

for user in users:
    print(user)

#### RIGHT JOIN #############
sql = "SELECT \
    users.first_name AS user, \
    user_groups.title AS user_group \
    FROM users \
    RIGHT JOIN user_groups ON users.user_group_id = user_groups.id"

cursor.execute(sql)
users = cursor.fetchall()

for user in users:
    print(user)


class User:
    def __init__(self, first_name):
        self.first_name = first_name
        self.last_name = ''


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    msg = bot.send_message(message.chat.id, "Введите имя")
    bot.register_next_step_handler(msg, process_firstname_step)


def process_firstname_step(message):
    try:
        user_id = message.from_user.id
        user_data[user_id] = User(message.text)

        msg = bot.send_message(message.chat.id, "Введите фамилию")
        bot.register_next_step_handler(msg, process_lastname_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')


def process_lastname_step(message):
    try:
        user_id = message.from_user.id
        user = user_data[user_id]
        user.last_name = message.text

        sql = "INSERT INTO users (first_name, last_name, user_id) \
                                  VALUES (%s, %s, %s)"
        val = (user.first_name, user.last_name, user_id)
        cursor.execute(sql, val)
        connection.commit()

        bot.send_message(message.chat.id, "Вы успешно зарегистрированны!")
    except Exception as e:
        bot.reply_to(message, 'Ошибка, или вы уже зарегистрированны!')


bot.enable_save_next_step_handlers(delay=2)

bot.load_next_step_handlers()

if __name__ == '__main__':
    bot.polling(none_stop=True)
