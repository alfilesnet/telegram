#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler, InlineQueryHandler, CallbackQueryHandler)
from telegram import (InlineQueryResultArticle, ParseMode, InputTextMessageContent, MessageEntity, InlineKeyboardButton, InlineKeyboardMarkup)
from uuid import uuid4
import telegram
import logging
import re
import urllib3
from gtts import gTTS
import os
from subprocess import call
from os import scandir, getcwd
from os.path import abspath

    
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------------------
# ELIMINA LOS ACENTOS Y CARACTERES SENSIBLES DE CRASHEAR EL CÓDIGO
#------------------------------------------------------------------------------------------
def remove_accents(data):
    return ''.join((c for c in unicodedata.normalize('NFD', data) if unicodedata.category(c) != 'Mn')).lower()

#==========================================================================================
# MENSAJE DE BIENVENIDA CUANDO ALGUIEN INICIA EL BOT DE FORMA PRIVADA
#==========================================================================================
def start(bot, update):
    update.message.reply_text('Hola!')


#==========================================================================================
# MENSAJE DE BIENVENIDA CUANDO ALGUIEN ENTRA A UN GRUPO
#==========================================================================================
def new_user(bot, update):
    
    cid = update.message.chat.id # Adquirir su ID
    user_name = update.message.from_user.name # Adquirir su nombre/alias
    bot.send_message(cid, 'Bienvenido '+user_name)

#==========================================================================================
# CONVIERTE UN TEXTO A VOZ
#==========================================================================================
def audio(bot, update):

	m=update.message
	cid = m.chat.id
	uid = m.from_user.id
	texto=m.text[7:]
	try:
		bot.delete_message(cid, m.message_id)
	except:
		pass
	tts = gTTS(text=texto, lang='es-es')
	tts.save("/RUTA/"+texto+".mp3")
	os.system("mpg321 /RUTA/"+texto+".mp3")
	bot.send_voice(chat_id=cid, voice=open("/RUTA/"+texto+".mp3", 'rb'))


#------------------------------------------------------------------------------------------
# DESCARGA UN ARCHIVO DE INTERNET
#------------------------------------------------------------------------------------------

def DownloadFile(url):
    try:
        local_filename = url.split('/')[-1]
        import urllib.request
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(url, '/RUTA/'+local_filename)
    except Exception as e:
        print (e)        

#------------------------------------------------------------------------------------------
# BORRA EL CONTENIDO DE UN DIRECTORIO
#------------------------------------------------------------------------------------------

def delete_files(folder):
    import os, shutil   
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

#------------------------------------------------------------------------------------------
# LISTA LOS ARCHIVOS DE UN DIRECTORIO
#------------------------------------------------------------------------------------------

def ls(ruta = getcwd()):
    return [arch.path[42:] for arch in scandir(ruta) if arch.is_file()]    

#==========================================================================================
# FUNCIÓN QUE DESCARGA UN ARCHIVO DE INTERNET
# COMPRIME EL ARCHIVO EN TROZOS DE 45Mb. Y LO ENVÍA A TELEGRAM
# (Hay que crear la carpeta "archivo" en la ruta del bot)
#==========================================================================================

def descargar(bot, update):
    m = update.message
    cid=m.chat.id

    chat_type=m.chat.type

    try: 

        url = m.text[11:]

        if url!='':

            local_filename=DownloadFile(url)                   
            mensaje = bot.send_message(cid, 'Se están comprimiendo el archivo')

            call(['rar', 'a', '-m0', '-v45m', '/RUTA/descarga.rar', 'archivo/*'])    
            fichero_actual=0
            try:        
                    for e, files in enumerate(sorted(ls('/RUTA/'))):
    
                        if files.startswith('descarga') and files.endswith('.rar'):
                            fichero_actual+=1
                            bot.edit_message_text(chat_id=cid, message_id=mensaje.message_id, text='Enviando el archivo '+str((fichero_actual)))
                            sent_file=bot.send_document(chat_id=cid, document=open('/RUTA/'+files, 'rb'), timeout=300)                        
                    bot.send_message(cid, 'Se han enviado todos los archivos')
                    delete_files('/RUTA/archivo/')

            except Exception as e:
                bot.send_message(cid, 'Ha habido un error')
                delete_files('/RUTA/archivo/')
        
        else:
        	bot.send_message(cid, 'Escribe <b>/descargar</b> seguido de la url de un archivo', parse_mode="HTML")

    except Exception as e:
        print (e)
        delete_files('/RUTA/archivo/')

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
	# Create the EventHandler and pass it your bot's token.
	updater = Updater("TOKEN DEL BOT")


	# Get the dispatcher to register handlers
	dp = updater.dispatcher


	# on different commands - answer in Telegram
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_user)) 

	dp.add_handler(CommandHandler("audio", audio))
	dp.add_handler(CommandHandler("descargar", descargar))

	# log all errors
	dp.add_error_handler(error)

	# Start the Bot
	updater.start_polling(clean=True)

	# Run the bot until you press Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT. This should be used most of the time, since
	# start_polling() is non-blocking and will stop the bot gracefully.
	updater.idle()


if __name__ == '__main__':
    main()
