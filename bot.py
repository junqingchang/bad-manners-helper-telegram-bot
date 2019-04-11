 from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup)

import random
import os
import pyrebase
import string

from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler, CallbackQueryHandler)

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

ASSIGN, NAMES, TASK, GENERATE, PAYMENT, PAYMENTOUTPUT = range(6)

# Start bot

def start(bot, update):
    update.message.reply_text(
        'What do you want? I am the BadMannersHelperBot v1.01, stop wasting my time\n'
        'Send /cancel to stop talking to me.\n'
        'Send /assign to assign jobs.\n'
        'Send /generate to generate job list\n'
        'Send /newpayment to create a new payment tracker\n'
        'Send /paymentstatus <payment_id> to check payment status\n'
        'Send /paymentcomplete <payment_id>|<passcode> to complete the payment and remove the entry\n'
        'Make up your mind. Choose what you want to do', reply_markup=ReplyKeyboardRemove())

# Assign Task Function

def assign(bot, update, user_data):
    update.message.reply_text(
    'I need the names of people to assign task to. Hurry up you *******\n'
    'Enter the names separated by | e.g.   personA|personB|personC',
                            reply_markup=ReplyKeyboardRemove())
    return NAMES

def names(bot, update, user_data):
    logger.info("Names from user:{}".format(update.message.text))
    user_data['names'] = (update.message.text).split("|")
    update.message.reply_text(
        'I need the task as well you idiot\n'
        'Enter the task separated by | e.g.   taskA|taskB|taskC')
    return TASK

def task(bot, update, user_data):
    logger.info("Task from user:{}".format(update.message.text))
    logger.info("Stored Names:{}".format(user_data))
    task = (update.message.text).split("|")
    if len(task) != len(user_data['names']):
        update.message.reply_text('Number of task and number of people doesnt tally you retard. Goodbye',
                              reply_markup=ReplyKeyboardRemove())
    else:
        random.shuffle(task)
        random.shuffle(user_data['names'])
        output = ''
        for i in range(len(task)):
            output += ('{} assigned to {}\n'.format(user_data['names'][i], task[i]))
        update.message.reply_text(output + 
                        '\nNow I can get on with my life',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Generate Task Function

def generate(bot, update, user_data):
    update.message.reply_text(
        'I need the task and number of times you need it repeated. Get on with it\n'
        'Enter the task and number using : and separated by | e.g.   taskA:1|taskB:5|taskC:3',
                            reply_markup=ReplyKeyboardRemove())
    return GENERATE

def generate_output(bot, update, user_data):
    tasklist = (update.message.text).split("|")
    all_task = []
    for task in tasklist:
        action, rep = task.split(":")
        logger.info("action:{}".format(action))
        logger.info("rep:{}".format(rep))
        all_task += [action] * int(rep)
    update.message.reply_text("|".join(all_task) + "\nThat was so easy and you couldn't do it. You're such a failure",
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Payment

def newpayment(bot, update, user_data):
    update.message.reply_text(
        'I need the message you want to send out...?\n'
        'Enter the message e.g.   Pay the friggin money',
                            reply_markup=ReplyKeyboardRemove())
    return PAYMENT

def paymentnames(bot, update, user_data):
    message = update.message.text
    user_data['newmessage'] = message
    update.message.reply_text(
        'LUL. Now who owes you money\n'
        'Enter the names separated by | e.g.   personA|personB|personC',
                            reply_markup=ReplyKeyboardRemove())
    return PAYMENTOUTPUT

def paymentcompleted(bot, update, user_data):
    message = user_data['newmessage']
    names = (update.message.text).split('|')
    message_id = str(random.randint(100000,999999))
    while message_id in user_data:
        message_id = str(random.randint(100000,999999))

    passcode = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    
    DB_NAME = os.environ.get("DB_NAME")
    DB_API = os.environ.get("DB_API")
    config = {
    "apiKey": DB_API,
    "authDomain": "{}.firebaseapp.com".format(DB_NAME),
    "databaseURL": "https://{}.firebaseio.com".format(DB_NAME),
    "storageBucket": "{}.appspot.com".format(DB_NAME)
    }

    firebase = pyrebase.initialize_app(config)
    db = firebase.database()

    new_payment = {}
    new_payment['message'] = message
    new_payment['passcode'] = passcode
    new_payment['payers'] = {}
    for name in names:
        new_payment['payers'][name] = ''

    results = db.child(message_id).set(new_payment)

    update.message.reply_text(
        'Done. Now leave me alone\n'
        'To check status of this payment, type /paymentstatus {}\nTo finish and delete this payment, type /paymentcomplete {}|{}'.format(message_id, message_id, passcode),
                            reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def paymentstatus(bot, update, user_data, args):
    message_id = args[0]

    DB_NAME = os.environ.get("DB_NAME")
    DB_API = os.environ.get("DB_API")
    config = {
    "apiKey": DB_API,
    "authDomain": "{}.firebaseapp.com".format(DB_NAME),
    "databaseURL": "https://{}.firebaseio.com".format(DB_NAME),
    "storageBucket": "{}.appspot.com".format(DB_NAME)
    }

    firebase = pyrebase.initialize_app(config)
    db = firebase.database()

    payment_info = (db.child(message_id).get()).val()

    

    if payment_info != None:
        keyboard = [[]]
        formatter = 0
        output = 'PAY UP YOU LAZY PEOPLE\n\n' + payment_info['message'] + '\n\n'
        for key in payment_info['payers']:
            keyboard[formatter].append(InlineKeyboardButton(key, callback_data='{}|{}'.format(key, message_id)))
            if len(keyboard[formatter]) == 5:
                keyboard.append([])
                formatter += 1
            if payment_info['payers'][key] == 'paid':
                output += '\n' + key + ' ---- PAID'
            else:
                output += '\n' + key

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(output, reply_markup=reply_markup)

    else:
        update.message.reply_text('Do you think I\'m 3? That payment ID doesnt exist',
                              reply_markup=ReplyKeyboardRemove())
    
    return ConversationHandler.END

def button(bot, update):
    query = update.callback_query
    user, message_id = query.data.split("|")
    logger.info("name " + user)
    logger.info("Message_id " + message_id)

    DB_NAME = os.environ.get("DB_NAME")
    DB_API = os.environ.get("DB_API")
    config = {
    "apiKey": DB_API,
    "authDomain": "{}.firebaseapp.com".format(DB_NAME),
    "databaseURL": "https://{}.firebaseio.com".format(DB_NAME),
    "storageBucket": "{}.appspot.com".format(DB_NAME)
    }

    firebase = pyrebase.initialize_app(config)
    db = firebase.database()

    payment_info = (db.child(message_id).get()).val()
    if payment_info != None:
        if user in payment_info['payers']:
            if payment_info['payers'][user] == 'paid':
                logger.info("undo-ing pay")
                payment_info['payers'][user] = ''
                db.child(message_id).update(payment_info)
            else:
                logger.info("paying")
                payment_info['payers'][user] = 'paid'
                db.child(message_id).update(payment_info)
        else:
            update.message.reply_text('Do you think I\'m 3? That user doesnt exist')
        keyboard = [[]]
        formatter = 0
        output = 'PAY UP YOU LAZY PEOPLE\n\n' + payment_info['message'] + '\n\n'

        for key in payment_info['payers']:
            keyboard[formatter].append(InlineKeyboardButton(key, callback_data='{}|{}'.format(key, message_id)))
            if len(keyboard[formatter]) == 5:
                keyboard.append([])
                formatter += 1
            if payment_info['payers'][key] == 'paid':
                output += '\n' + key + ' ---- PAID'
            else:
                output += '\n' + key

        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=output,reply_markup = reply_markup)
    else:
        update.message.reply_text('Do you think I\'m 3? That payment ID doesnt exist',
                              reply_markup=ReplyKeyboardRemove())

# DEPRECATED
# def paid(bot, update, user_data, args):
#     message_id, user = args[0].split('|')

#     DB_NAME = os.environ.get("DB_NAME")
#     DB_API = os.environ.get("DB_API")
#     config = {
#     "apiKey": DB_API,
#     "authDomain": "{}.firebaseapp.com".format(DB_NAME),
#     "databaseURL": "https://{}.firebaseio.com".format(DB_NAME),
#     "storageBucket": "{}.appspot.com".format(DB_NAME)
#     }

#     firebase = pyrebase.initialize_app(config)
#     db = firebase.database()

#     payment_info = (db.child(message_id).get()).val()

#     if payment_info != None:
#         if user in payment_info['payers']:
#             db.child(message_id).child('payers').update({user: 'paid'}) 
#             update.message.reply_text('{} paid'.format(user),
#                               reply_markup=ReplyKeyboardRemove())
#         else:
#             update.message.reply_text('Do you think I\'m 3? That user doesnt exist',
#                               reply_markup=ReplyKeyboardRemove())
#     else:
#         update.message.reply_text('Do you think I\'m 3? That payment ID doesnt exist',
#                               reply_markup=ReplyKeyboardRemove())

def paymentcomplete(bot, update, args):
    message_id, passcode = args[0].split('|')

    DB_NAME = os.environ.get("DB_NAME")
    DB_API = os.environ.get("DB_API")
    config = {
    "apiKey": DB_API,
    "authDomain": "{}.firebaseapp.com".format(DB_NAME),
    "databaseURL": "https://{}.firebaseio.com".format(DB_NAME),
    "storageBucket": "{}.appspot.com".format(DB_NAME)
    }

    firebase = pyrebase.initialize_app(config)
    db = firebase.database()

    payment_info = (db.child(message_id).get()).val()

    if payment_info != None:
        if payment_info['passcode'] != passcode:
            update.message.reply_text('HAHAHA YOU FORGOT YOUR PASSCODE',
                              reply_markup=ReplyKeyboardRemove())
        else:
            db.child(message_id).remove()
            update.message.reply_text('Payment Completed. Stop lending money to people',
                              reply_markup=ReplyKeyboardRemove())

def mastercleandb(bot, update, args):
    passcode = args[0]

    if passcode == os.environ.get("MASTER_RESET"):

        DB_NAME = os.environ.get("DB_NAME")
        DB_API = os.environ.get("DB_API")
        config = {
        "apiKey": DB_API,
        "authDomain": "{}.firebaseapp.com".format(DB_NAME),
        "databaseURL": "https://{}.firebaseio.com".format(DB_NAME),
        "storageBucket": "{}.appspot.com".format(DB_NAME)
        }

        firebase = pyrebase.initialize_app(config)
        db = firebase.database()
        db.remove()
# Fallback

def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Wow. you just wasted my time. Thanks.',
                            reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def error(bot, update, error):
    """Log Errors caused by Updates."""
    update.message.reply_text("Great. You broke me. What was I even expecting")
    logger.warning('Update "%s" caused error "%s"', update, error)

# Help message

def help(bot, update):
    update.message.reply_text('Send /assign to assign jobs to people\n'
                                'Send /generate to create the task list for assigning jobs\n' 
                                'Send /newpayment to create a new payment tracker\n'
                                'Send /paymentstatus <payment_id> to check payment status\n'
                                'Send /paymentcomplete <payment_id>|<passcode> to complete the payment and remove the entry\n'
                                'If you have any other queries please direct them to Jun Qing or raise an issue at https://github.com/junqingchang/bad-manners-helper-telegram-bot')

# Main

def main():
    TOKEN = os.getenv("TOKEN")
    PORT = int(os.environ.get('PORT', '8443'))
    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    assign_handler = ConversationHandler(
        entry_points=[CommandHandler('assign', assign, pass_user_data = True)],

        states={
            NAMES: [MessageHandler(Filters.text, names, pass_user_data=True)],

            TASK: [MessageHandler(Filters.text, task, pass_user_data=True)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    generate_handler = ConversationHandler(
        entry_points=[CommandHandler('generate', generate, pass_user_data = True)],

        states={
            GENERATE: [MessageHandler(Filters.text, generate_output, pass_user_data=True)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    payment_handler = ConversationHandler(
        entry_points=[CommandHandler('newpayment', newpayment, pass_user_data = True)],
        
        states={
            PAYMENT: [MessageHandler(Filters.text, paymentnames, pass_user_data=True)],

            PAYMENTOUTPUT: [MessageHandler(Filters.text, paymentcompleted, pass_user_data=True)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    status_handler = CommandHandler('paymentstatus', paymentstatus, pass_user_data = True, pass_args = True)

    # DEPRECATED
    # paid_handler = CommandHandler('paid', paid, pass_user_data = True, pass_args = True)

    help_handler = CommandHandler('help', help)

    start_handler = CommandHandler('start', start)

    complete_handler = CommandHandler('paymentcomplete', paymentcomplete, pass_args = True)

    master_handler = CommandHandler('mastercleandb', mastercleandb, pass_args = True)


    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(assign_handler)
    dispatcher.add_handler(generate_handler)
    dispatcher.add_handler(payment_handler)
    dispatcher.add_handler(status_handler)
    # DEPRECATED
    # dispatcher.add_handler(paid_handler)
    dispatcher.add_handler(complete_handler)
    dispatcher.add_handler(master_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_error_handler(error)
    dispatcher.add_handler(CallbackQueryHandler(button))
    
    updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=TOKEN)
    updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))

    updater.idle()



if __name__ == '__main__':
    main()