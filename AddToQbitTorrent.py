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

#################################################
# Código creado por https://telegram.me/alfiles #
#################################################


from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler, InlineQueryHandler, CallbackQueryHandler)
from telegram import (InlineQueryResultArticle, ParseMode, InputTextMessageContent, MessageEntity, InlineKeyboardButton, InlineKeyboardMarkup)
import telegram
import logging
#----------------------------------------------
# Libería para ejectar comandos de linux en 
# python 🔽
#----------------------------------------------
from subprocess import call
#----------------------------------------------
# Libería para usar las expresiones regulares
# (regex) 🔽
#----------------------------------------------
import re 

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
 
logger = logging.getLogger(__name__)



#----------------------------------------------
# Función para descargarse un archivo de 
# internet
#----------------------------------------------
def DownloadFile(url, filename):
	try:
		# local_filename = url.split('/')[-1]
		import urllib.request
		opener = urllib.request.build_opener()
		opener.addheaders = [('User-agent', 'Mozilla/5.0')]
		urllib.request.install_opener(opener)
		urllib.request.urlretrieve(url, './'+filename)
	except Exception as e:
		print (e) 


#----------------------------------------------
# Función para borrar todos los archivos de un
# directorio
#----------------------------------------------
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

#----------------------------------------------
# Función para capturar el texto que se le 
# escribe al bot
#
# Si contiene magnets los envía y en caso
# contrario, no hace nada
#----------------------------------------------

def capturar_texto(bot, update):
	m=update.message
	regex = r"magnet:\?xt=urn:btih:(.+?).torrent"
	texto = m.text

	try:
		matches = re.finditer(regex, texto)
		for magnet in matches:
			call(['qbittorrent-nox', 'magnet:?xt=urn:btih:'+str(magnet.group(1))+'.torrent'])
		bot.send_message(chat_id=m.chat.id, text="Se han enviado todos los magnets a qbittorrent", parse_mode="HTML") 
	except:
		pass


#----------------------------------------------
# Función para descargar archivos y enviarlos a
# qbittorrent
#
# Si es un .torrent, lo envía al qbittorrent
# directamente
#
# Si es un .txt con los magnets, los procesa
# mediante regex y los envía al qbittorrent de
# forma individual
#
# Si no es un .torrent o un .txt, no hace nada
#
# NOTA: En el ejemplo es necesario crear el
# directorio 'tmp_qbt/', aunque le puedes poner
# la ruta que quieras
#----------------------------------------------

def descargar_archivos(bot, update):

	try:
		m=update.message
		# print (m)
		filename=m.document.file_name	
		archivo = bot.getFile(m.document.file_id)	
		DownloadFile(archivo.file_path, 'tmp_qbt/'+filename)

		if filename.endswith('.torrent'):		
			call(['qbittorrent-nox', 'tmp_qbt/'+filename])
			bot.send_message(chat_id=m.chat.id, text="El archivo <b>"+filename+"</b> se ha añadido al qbittorrent con exito", parse_mode="HTML") 

		if filename.endswith('.txt'):
			regex = r"magnet:\?xt=urn:btih:(.+?)&dn=[\w\W]+?.torrent"
			test_str=open('tmp_qbt/'+filename, 'r').read()
			matches = re.finditer(regex, test_str)
			for lista in matches:	
				call(['qbittorrent-nox', 'magnet:?xt=urn:btih:'+str(lista.group(1))])
			bot.send_message(chat_id=m.chat.id, text="Se han enviado todos los magnets de <b>"+filename+"</b> a qbittorrent", parse_mode="HTML") 
	except:
		pass

	delete_files('tmp_qbt/')
	

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))
 
 
def main():
    # Create the EventHandler and pass it your bot's token.

    updater = Updater("ESCRIBE AQUÍ EL TOKEN DE TU BOT")
    dp = updater.dispatcher
    
    dp.add_handler(MessageHandler(Filters.document, descargar_archivos)) 
    dp.add_handler(MessageHandler(Filters.text, capturar_texto))
    # Get the dispatcher to register handlers
    
     
 
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
   
