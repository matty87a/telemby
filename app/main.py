#!/usr/bin/python3

import json
import logging
import time
from configparser import ConfigParser

import requests
import telegram
from telegram import ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def get_config():
    config = ConfigParser()
    config.read('config.ini')
    config_vars = dict()
    config_vars['API_TOKEN'] = config['BOT']['API_TOKEN']
    config_vars['USER_ID'] = config['BOT']['USER_ID']
    config_vars['SERVER'] = config['EMBY']['SERVER']
    config_vars['EMBY_API'] = config['EMBY']['API_KEY']
    return config_vars


def get_endpoint(param):
    config = get_config()
    endpoint = config['SERVER'] + param + "?api_key=" + config['EMBY_API']
    return endpoint


def get_endpoint2(param):
    config = get_config()
    endpoint = config['SERVER'] + param + "&api_key=" + config['EMBY_API']
    return endpoint


def get_sched_task(name):
    get_config()
    string = "ScheduledTasks"
    url = get_endpoint(string)
    response = requests.get(url)
    data = response.json()
    for task in data:
        if task["Name"] == name:
            id = task["Id"]
            return id


def get_uid(name):
    get_config()
    string = "Users"
    url = get_endpoint(string)
    response = requests.get(url)
    data = response.json()
    for user in data:
        if user["Name"] == name:
            id = user["Id"]
            return id


def system_info_item(string, item):
    config = get_config()
    string = string
    url = get_endpoint(string)
    response = requests.get(url)
    data = response.json()

    return data[item]


def user_info():
    config = get_config()
    string = "Users"
    url = get_endpoint(string)
    response = requests.get(url)
    data = response.json()
    users = [value['Name'] for value in data]
    # for each in data:
    #     name = each['name']
    #     print(name)
    list = json.dumps(users, indent=4, sort_keys=True)
    return list


def device_info():
    config = get_config()
    string = "user_usage_stats/session_list"
    url = get_endpoint(string)
    response = requests.get(url)
    data = response.json()
    devices = [value['device_name'] for value in data]
    list = json.dumps(devices, indent=4, sort_keys=True)
    return list


def activity_feed():
    config = get_config()
    string = "emby/System/ActivityLog/Entries?Limit=10"
    url = get_endpoint2(string)
    response = requests.get(url)
    data = response.json()
    feed = data["Items"]
    activity = list(feed)
    message = json.dumps(activity, indent=4, sort_keys=True)
    return message


def run_sched_task(task):
    config = get_config()
    task_id = get_sched_task(task)
    url = get_endpoint("ScheduledTasks/Running/{}".format(task_id))
    requests.post(url)


def update_library(bot, update):
    config = get_config()
    if update.message.from_user.id != int(config['USER_ID']):
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="UNAUTHORIZED")
    else:
        url = get_endpoint("Library/Refresh")
        try:
            response = requests.post(url)
            data = response.text
            update.message.reply_text("Library Refresh Started")
        except:
            update.message.reply_text("ERROR")


def update_guide(bot, update):
    config = get_config()
    if update.message.from_user.id != int(config['USER_ID']):
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="UNAUTHORIZED")
    else:
        try:
            run_sched_task("Refresh Guide")
            update.message.reply_text("TV Guide Refresh Started")
        except:
            update.message.reply_text("ERROR")


def trigger_backup(bot, update):
    config = get_config()
    if update.message.from_user.id != int(config['USER_ID']):
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="UNAUTHORIZED")
    else:
        try:
            run_sched_task("Configuration Backup")
            update.message.reply_text("Configuration Backup Requested")
        except:
            update.message.reply_text("ERROR")


def restart_server(bot, update):
    config = get_config()
    if update.message.from_user.id != int(config['USER_ID']):
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="UNAUTHORIZED")
    else:
        url = get_endpoint("System/Restart")
        try:
            response = requests.post(url)
            data = response.text
            update.message.reply_text("Server will be Restarted")
        except:
            update.message.reply_text("ERROR")


def check_server(bot, update):
    url = get_endpoint("System/Ping")
    try:
        response = requests.post(url)
        data = response.text
        if data == "Emby Server":
            # update.message.reply_text("Your Server is Online")
            return "Your Server is Online"
    except:
        update.message.reply_text("ERROR")


def system_info(bot, update):
    config = get_config()
    if update.message.from_user.id != int(config['USER_ID']):
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="UNAUTHORIZED")
    else:
        system_info_item('System/Info', 'OperatingSystemDisplayName')
        Status = str(check_server(bot, update))
        Server_Name = system_info_item('System/Info', 'ServerName')
        Local_Address = system_info_item('System/Info', 'LocalAddress')
        WAN_Address = system_info_item('System/Info', 'WanAddress')
        Emby_Version = system_info_item('System/Info', 'Version')
        Update_Available = str(system_info_item('System/Info', 'HasUpdateAvailable'))
        Movies = str(system_info_item('Items/Counts', 'MovieCount'))
        Series = str(system_info_item('Items/Counts', 'SeriesCount'))
        Episodes = str(system_info_item('Items/Counts', 'EpisodeCount'))
        Channels = str(system_info_item('LiveTV/Channels', 'TotalRecordCount'))

        msg = Status + " \n"
        msg += " \n"
        msg += "Server Name: {} \n".format(Server_Name)
        msg += "Local Address: {} \n".format(Local_Address)
        msg += "Remote Address: {} \n".format(WAN_Address)
        msg += "Version: {} \n".format(Emby_Version)
        msg += "Update Available:  {} \n".format(Update_Available)
        msg += " \n"
        msg += "Movies: {} \n".format(Movies)
        msg += "Series: {} \n".format(Series)
        msg += "Episodes: {} \n".format(Episodes)
        msg += "TV Channels: {} \n".format(Channels)

        bot.send_message(chat_id=update.message.chat_id,
                         text=msg.format(
                             user_name=update.message.from_user.first_name,
                             bot_name=bot.name))


def list_users(bot, update):
    config = get_config()
    if update.message.from_user.id != int(config['USER_ID']):
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="UNAUTHORIZED")
    else:
        users = str(user_info())

        msg = "Enabled Users: \n"
        msg += users

        bot.send_message(chat_id=update.message.chat_id,
                         text=msg.format(
                             user_name=update.message.from_user.first_name,
                             bot_name=bot.name))


def list_activity(bot, update):
    config = get_config()
    if update.message.from_user.id != int(config['USER_ID']):
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="UNAUTHORIZED")
    else:
        feed = activity_feed()
        update.message.reply_text(feed)


def list_devices(bot, update):
    config = get_config()
    if update.message.from_user.id != int(config['USER_ID']):
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="UNAUTHORIZED")
    else:
        devices = (device_info())

        msg = "Connected Devices: \n"
        msg += devices

        bot.send_message(chat_id=update.message.chat_id,
                         text=msg.format(
                             user_name=update.message.from_user.first_name,
                             bot_name=bot.name))


def unknown(bot, update):
    config = get_config()
    if update.message.from_user.id != int(config['USER_ID']):
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="UNAUTHORIZED")
    else:
        update.message.reply_text("Sorry, I didn't understand that command.")


def show_help(bot, update):
    config = get_config()
    if update.message.from_user.id != int(config['USER_ID']):
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="UNAUTHORIZED")

    else:
        msg = "/status - Check your Emby Server is Online \n"
        msg += "/refreshlibrary - Refreshes all Media Libraries \n"
        msg += "/refreshguide - Refreshes TV Guide Data \n"
        msg += "/users - Lists Emby Users \n"
        msg += "/devices - Lists Emby Devices \n"
        msg += "/activity - Lists Last 10 Activity Items \n"
        msg += "/backup - Triggers a Configuration Backup \n"
        msg += "/help - Prints this message"

        # Send the message
        bot.send_message(chat_id=update.message.chat_id,
                         text=msg.format(
                             user_name=update.message.from_user.first_name,
                             bot_name=bot.name))


def start(bot, update):
    config = get_config()

    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)
    bot.sendMessage(chat_id=update.message.chat_id, text="Hi, {}".format(update.message.from_user.first_name))

    if update.message.from_user.id != int(config['USER_ID']):
        msg = "Hello {user_name} \n"
        msg += "You are not authorized to use this bot \n"
        msg += "Please enter your Telegram ID in the config.ini file \n"

        # Send the message
        bot.send_message(chat_id=update.message.chat_id,
                         text=msg.format(
                             user_name=update.message.from_user.first_name,
                             bot_name=bot.name))

    else:
        bot.sendChatAction(chat_id=update.message.chat_id,
                           action=ChatAction.TYPING)
        time.sleep(1)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Checking your Emby Server...")
        bot.sendChatAction(chat_id=update.message.chat_id,
                           action=ChatAction.TYPING)
        time.sleep(0.5)
        check_server(bot, update)
        system_info(bot, update)
        keyboard(bot, update)

        msg = "/status - Check your Emby Server is Online \n"
        msg += "/refreshlibrary - Refreshes all Media Libraries \n"
        msg += "/refreshguide - Refreshes TV Guide Data \n"
        msg += "/users - Lists Emby Users \n"
        msg += "/devices - Lists Emby Devices \n"
        msg += "/activity - Lists Last 10 Activity Items \n"
        msg += "/backup - Triggers a Configuration Backup \n"
        msg += "/help - Prints this message"

        bot.send_message(chat_id=update.message.chat_id,
                         text=msg.format(
                             user_name=update.message.from_user.first_name,
                             bot_name=bot.name))


def keyboard(bot, update):
    kb = [[telegram.KeyboardButton('/status')],
          [telegram.KeyboardButton('/refreshlibrary')],
          [telegram.KeyboardButton('/refreshguide')],
          [telegram.KeyboardButton('/activity')],
          [telegram.KeyboardButton('/users')],
          [telegram.KeyboardButton('/devices')],
          [telegram.KeyboardButton('/backup')],
          [telegram.KeyboardButton('/help')]]
    kb_markup = telegram.ReplyKeyboardMarkup(kb, resize_keyboard=True)

    bot.send_message(chat_id=update.message.chat_id,
                     text="Options: ",
                     reply_markup=kb_markup)


def main():
    config = get_config()
    updater = Updater(config['API_TOKEN'])
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(CommandHandler('refreshlibrary', update_library))
    dispatcher.add_handler(CommandHandler('refreshguide', update_guide))
    dispatcher.add_handler(CommandHandler('restartserver', restart_server))
    dispatcher.add_handler(CommandHandler('activity', list_activity))
    dispatcher.add_handler(CommandHandler('users', list_users))
    dispatcher.add_handler(CommandHandler('devices', list_devices))
    dispatcher.add_handler(CommandHandler('status', system_info))
    dispatcher.add_handler(CommandHandler('backup', trigger_backup))
    dispatcher.add_handler(CommandHandler('help', show_help))
    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

