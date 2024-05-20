import logging, re, paramiko, psycopg2, os
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

db_user=os.getenv('DB_USER')
db_password=os.getenv('DB_PASSWORD')
db_host=os.getenv('DB_HOST')
db_port=os.getenv('DB_PORT')
db_database=os.getenv('DB_DATABASE')

logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def connection(command):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command(command)
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    return data


def get_db_connection():
    conn = psycopg2.connect(
        database=db_database,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    return conn

emailRegex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

passwordRegex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()])(?!.*\s).{8,}$')

def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}! Для просмотра команд напиши /select')

def helpCommand(update: Update, context):
    update.message.reply_text('Help!')

def findEmailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска email-адресов: ')
    return 'findEmail'

def findEmail(update: Update, context):
    user_input = update.message.text
    emailList = emailRegex.findall(user_input)
    if not emailList:
        update.message.reply_text('Email-адреса не найдены')
        return ConversationHandler.END
    emails_str = '\n'.join(emailList)
    update.message.reply_text(f'Найдены следующие email-адреса:\n{emails_str}\nХотите записать их в базу данных? (да/нет)')
    context.user_data['emails'] = emailList  # Сохраняем список email-адресов в контексте бота
    return 'recordEmails'

def findPhoneNumberCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска номеров телефонов: ')
    return 'findPhoneNumber'

def findPhoneNumber(update: Update, context):
    user_input = update.message.text
    phoneNumRegex = re.compile(r'\+?7\s?[-(]?\d{3}[-)\s]?\s?\d{3}[-\s]?\d{2}[-\s]?\d{2}|8\s?[-(]?\d{3}[-)\s]?\s?\d{3}[-\s]?\d{2}[-\s]?\d{2}')
    phoneNumberList = phoneNumRegex.findall(user_input)
    if not phoneNumberList:
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END
    phoneNumbers = '\n'.join(phoneNumberList)
    update.message.reply_text(f'Найдены следующие номера телефонов:\n{phoneNumbers}\nХотите записать их в базу данных? (да/нет)')
    context.user_data['phoneNumbers'] = phoneNumberList  # Сохраняем список номеров телефонов в контексте бота
    return 'recordPhoneNumbers'

def recordEmails(update: Update, context):
    user_input = update.message.text.lower()
    if user_input == 'да':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            for email in context.user_data['emails']:  # Используем данные из контекста бота
                cursor.execute("INSERT INTO emails (email) VALUES (%s)", (email,))
            conn.commit()
            cursor.close()
            conn.close()
            update.message.reply_text('Email-адреса успешно записаны в базу данных.')
        except Exception as e:
            update.message.reply_text(f'Ошибка при записи email-адресов: {e}')
    else:
        update.message.reply_text('Отмена записи email-адресов.')
    return ConversationHandler.END

def recordPhoneNumbers(update: Update, context):
    user_input = update.message.text.lower()
    if user_input == 'да':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            for phoneNumber in context.user_data['phoneNumbers']:  # Используем данные из контекста бота
                cursor.execute("INSERT INTO Numbersphone (number) VALUES (%s)", (phoneNumber,))
            conn.commit()
            cursor.close()
            conn.close()
            update.message.reply_text('Номера телефонов успешно записаны в базу данных.')
        except Exception as e:
            update.message.reply_text(f'Ошибка при записи номеров телефонов: {e}')
    else:
        update.message.reply_text('Отмена записи номеров телефонов.')
    return ConversationHandler.END

def verifyPassword(update: Update, context):
    update.message.reply_text('Введите пароль для проверки: ')
    return 'verifyPassword'

def checkPassword(update: Update, context):
    user_input = update.message.text
    if passwordRegex.match(user_input):
        update.message.reply_text('Пароль сложный')
    else:
        update.message.reply_text('Пароль простой')
    return ConversationHandler.END

def echo(update: Update, context):
    update.message.reply_text(update.message.text)

def selectCommand(update: Update, context):
    update.message.reply_text('Выберите команду:\n1. Запуск бота: /start\n2. "Help!": /help\n3. Выделить из текста Email-адреса: /find_email\n4. Выделить из текста номера телефонов: /find_phone_number\n5. Проверить сложность пароля: /verify_password\n6. Информация о резиле системы: /get_release\n7. Информация об архитектуры процессора, имени хоста системы и версии ядра: /get_uname\n8. Информация о времени работы: /get_uptime\n9. Сбор информации о состоянии файловой системы: /get_df\n10. Сбор информации о состоянии оперативной памяти: /get_free\n11. Сбор информации о производительности системы: /get_mpstat\n12. Сбор информации о работающих в данной системе пользователях: /get_w\n13. Последние 10 входов в систему: /get_auths\n14. Последние 5 критических событий: /get_critical\n15. Сбор информации о запущенных процессах: /get_ps\n16. Сбор информации об используемых портах: /get_ss\n17. Сбор информации об установленных пакетах: /get_apt_list\n18. Сбор информации о запущенных сервисах: /get_services\n19. Логи о репликации /get_repl_logs\n20. Emails в бд /get_emails\n21. Номера телефонов в бд /get_phone_numbers')
    return 'selectCommand'

def get_release(update: Update, context):
    update.message.reply_text(connection('uname -r'))
    return ConversationHandler.END

def get_uname(update: Update, context):
    update.message.reply_text(connection('uname -a'))
    return ConversationHandler.END

def get_uptime(update: Update, context):
    update.message.reply_text(connection('uptime'))
    return ConversationHandler.END

def get_df(update: Update, context):
    update.message.reply_text(connection('df -h'))
    return ConversationHandler.END

def get_free(update: Update, context):
    update.message.reply_text(connection('free -h'))
    return ConversationHandler.END

def get_mpstat(update: Update, context):
    update.message.reply_text(connection('mpstat'))
    return ConversationHandler.END

def get_w(update: Update, context):
    update.message.reply_text(connection('w'))
    return ConversationHandler.END
    

def get_critical(update: Update, context):
    update.message.reply_text(connection('journalctl -p 2 -n 5'))
    return ConversationHandler.END

def get_auths(update: Update, context):
    update.message.reply_text(connection('last -n 10'))
    return ConversationHandler.END

def get_ps(update: Update, context):
    update.message.reply_text(connection('ps aux'))
    return ConversationHandler.END

def get_ss(update: Update, context):
    update.message.reply_text(connection('ss -tuln'))
    return ConversationHandler.END

def get_services(update: Update, context):
    if len(connection('systemctl list-units --type=service'))>4096:
        for x in range(0, len(connection('systemctl list-units --type=service')),4096):
            update.message.reply_text(connection('systemctl list-units --type=service')[x:x+4096])  
        else:  
            update.message.reply_text(connection('systemctl list-units --type=service'))
    return ConversationHandler.END
    

def get_apt_list(update: Update, context):
    update.message.reply_text('Введите "all" для получения списка всех установленных пакетов или имя пакета для поиска информации: ')
    return 'aptAction'

def aptAction(update: Update, context):
    user_input = update.message.text
    if user_input.lower() == 'all':
        if len(connection('apt list --installed'))>4096:
            for x in range(0, len(connection('apt list --installed')),4096):
                update.message.reply_text(connection('apt list --installed')[x:x+4096])  
            else:  
                update.message.reply_text(connection('apt list --installed'))
    else:
        result = connection(f'apt show {user_input}')
        if result:
            update.message.reply_text(result) 
        else:
            update.message.reply_text("Не удалось получить информацию о пакете.")
    return ConversationHandler.END



def get_repl_logs(update: Update, context):
    reply=''
    filename=os.listdir('//temp/db_logs/')[0]
    log=open('/temp/db_logs/'+filename,'r').readlines()
    for i in log:
    	if 'repl' in i.lower():
    	   reply += i + '\n'
    update.message.reply_text(reply)
    return ConversationHandler.END

def get_emails(update: Update, context):
    try:
        conn = get_db_connection()
        print(get_db_connection)
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM emails")
        emails = cursor.fetchall()
        cursor.close()
        conn.close()

        email_list = [email[0] for email in emails]
        emails_str = '\n'.join(email_list)
        update.message.reply_text(emails_str)
    except Exception as e:
        update.message.reply_text(f"Ошибка при получении email-адресов: {e}")

def get_phone_numbers(update: Update, context):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT number FROM numbersphone")
    phone_numbers = cursor.fetchall()
    cursor.close()
    conn.close()

    phone_numbers_list = [phone_number[0] for phone_number in phone_numbers]
    phone_numbers_str = '\n'.join(phone_numbers_list)
    update.message.reply_text(phone_numbers_str)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    convHandlerGetAptList= ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_list)],
        states={
            'aptAction': [MessageHandler(Filters.text & ~Filters.command, aptAction)],
        },
        fallbacks=[]
    )
    
    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPassword)],
        states={
            'verifyPassword': [MessageHandler(Filters.text & ~Filters.command, checkPassword)],
        },
        fallbacks=[]
    )

    convHandlerSelectCommand = ConversationHandler(
        entry_points=[CommandHandler('select', selectCommand)],
        states={
            'selectCommand': [MessageHandler(Filters.regex('^(1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21)$'), selectCommand)],
        },
        fallbacks=[]
    )

    convHandlerFindEmail = ConversationHandler(
    entry_points=[CommandHandler('find_email', findEmailCommand)],
    states={
        'findEmail': [MessageHandler(Filters.text & ~Filters.command, findEmail)],
        'recordEmails': [MessageHandler(Filters.regex('^(да|нет)$'), recordEmails)],
    },
    fallbacks=[]
    )

    convHandlerFindPhoneNumber = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumberCommand)],
        states={
            'findPhoneNumber': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumber)],
            'recordPhoneNumbers': [MessageHandler(Filters.regex('^(да|нет)$'), recordPhoneNumbers)],
        },
        fallbacks=[]
    )
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(convHandlerSelectCommand)
    dp.add_handler(convHandlerGetAptList)
    dp.add_handler(convHandlerVerifyPassword)
    dp.add_handler(convHandlerFindEmail)
    dp.add_handler(convHandlerFindPhoneNumber)
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical)) 
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
