from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)

import random

from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler)

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

MENU, NAMES, TASK, GENERATE= range(4)

def start(bot, update, user_data):
    reply_keyboard = [['AssignJobs', 'GenerateTask']]
    update.message.reply_text(
        'What do you want? I am the BadMannersHelperBot, stop wasting my time\n'
        'Send /cancel to stop talking to me.\n'
        'Make up your mind. Choose what you want to do', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return MENU

def menu(bot, update, user_data):
    response = update.message.text
    if response == "AssignJobs":
        update.message.reply_text(
        'I need the names of people to assign task to. Hurry up you *******\n'
        'Enter the names separated by | e.g.   personA|personB|personC')
        return NAMES
    elif response == "GenerateTask":
        update.message.reply_text(
        'I need the task and number of times you need it repeated. Get on with it\n'
        'Enter the task and number using : and separated by | e.g.   taskA:1|taskB:5|taskC:3')
        return GENERATE
    else:
        update.message.reply_text('What a waste of time. Get lost')
        return ConversationHandler.END

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
        update.message.reply_text('Number of task and number of people doesnt tally you retard. Goodbye')
    else:
        random.shuffle(task)
        random.shuffle(user_data['names'])
        output = ''
        for i in range(len(task)):
            output += ('{} assigned to {}\n'.format(user_data['names'][i], task[i]))
        update.message.reply_text(output + 
                        '\nNow I can get on with my life')
    return ConversationHandler.END

def generate(bot, update, user_data):
    tasklist = (update.message.text).split("|")
    all_task = []
    for task in tasklist:
        action, rep = task.split(":")
        logger.info("action:{}".format(action))
        logger.info("rep:{}".format(rep))
        all_task += [action] * int(rep)
    update.message.reply_text("|".join(all_task) + "\nThat was so easy and you couldn't do it. You're such a failure")
    return ConversationHandler.END

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

def help(bot, update):
    update.message.reply_text("Send \start to use me. What were you expecting?\nAssignJob assigns job..?\n GenerateTask creates the task list for lazy people like you")


def main():
    updater = Updater(token='624420179:AAGtbR0DJlxwrC7KW5HrANktOQcSvYciHKI')
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start, pass_user_data=True)],

        states={
            MENU: [MessageHandler(Filters.text, menu, pass_user_data=True)
                    ,RegexHandler('^(AssignJobs|GenerateTask)$', menu)],

            NAMES: [MessageHandler(Filters.text, names, pass_user_data=True)],

            TASK: [MessageHandler(Filters.text, task, pass_user_data=True)],

            GENERATE: [MessageHandler(Filters.text, generate, pass_user_data=True)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    help_handler = CommandHandler('help', help)

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_error_handler(error)
    
    updater.start_polling()

    updater.idle()



if __name__ == '__main__':
    main()