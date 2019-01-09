#!/usr/bin/env python
# -*- coding: utf-8 -*-

#################################################
# Código creado por https://telegram.me/alfiles #
#################################################

#------------------------------------------------
# Librerías necesarias                          #
#------------------------------------------------
# pip install telegram --upgrade -y
# pip install python-telegram-bot --upgrade -y
# sudo apt install qbittorrent-nox -y

#------------------------------------------------
# Carpetas necesarias                           #
#------------------------------------------------
# Para que funcione el bot, es necesario que  
# exista la carpeta "archivos" en la ruta donde 
# esté el archivo AddToQbitTorrent.py
#
# puedes crearla así:
# mkdir archivos

#-----------------------------------------------#
# ¿Qué hace el bot?                             #
#-----------------------------------------------#
# 1) Reenviando o arrastrando un .torrent al bot, 
#    éste lo añadirá al qbittorrent
#
# 2) Reenviando o arrastrando un .txt con enlaces
#    magnets, éste los añadirá al qbittorrent
#
# 3) Reenviando o escribiendo un enlace magnet en
#    el bot, éste lo añadirá al qbittorrnet
#
# 4) Reenviando o escribiendo un enlace .torrent 
#    en el bot, éste lo añadirá al qbittorrnet
#
# 5) Reenviando o escribiendo un archivo .zip
#    con .torrent en su interior, lo 
#    descomprimirá y los añadirá al qbittorrent

from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler, InlineQueryHandler, CallbackQueryHandler)
from telegram import (InlineQueryResultArticle, ParseMode, InputTextMessageContent, MessageEntity, InlineKeyboardButton, InlineKeyboardMarkup)
import telegram
import logging
#------------------------------------------------
# Libería para ejectar comandos de linux en 
# python 🔽
#------------------------------------------------
from subprocess import call
#------------------------------------------------
# Libería para usar las expresiones regulares
# (regex) 🔽
#------------------------------------------------
import re 
#------------------------------------------------
# Libería para borrar un archivo, mostrar los 
# archivos de una carpeta y renombrar archivos 🔽
#------------------------------------------------
import os
from os import remove, scandir, getcwd, rename

#------------------------------------------------
# Libería para extraer los archivos .zip
#------------------------------------------------
import zipfile


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
 
logger = logging.getLogger(__name__)

#------------------------------------------------
# Función para descargarse un archivo de 
# internet
#------------------------------------------------
def DownloadFile(url, filename):
	import urllib.request
	opener = urllib.request.build_opener()
	opener.addheaders = [('User-agent', 'Mozilla/5.0')]
	urllib.request.install_opener(opener)
	urllib.request.urlretrieve(url, './'+filename)

#------------------------------------------------
# Función para capturar el texto que se le 
# escribe al bot
#
# Si contiene magnets/.torrent los envía y en 
# caso contrario, no hace nada
#------------------------------------------------

def capturar_texto(bot, update):
	m=update.message
	regex = r"magnet:\?xt=urn:btih:(.+?).torrent"
	texto = m.text

	count=0

	if texto.endswith('.torrent') and texto.startswith('http'):
		call(['qbittorrent-nox', texto])
		bot.send_message(chat_id=m.chat.id, text="Se han enviado todos los magnets a qbittorrent", parse_mode="HTML") 
	else:
		matches = re.finditer(regex, texto)
		for magnet in matches:
			if magnet.group(1)!='':
				call(['qbittorrent-nox', 'magnet:?xt=urn:btih:'+str(magnet.group(1))+'.torrent'])
				count+=1
		if count>0:
			bot.send_message(chat_id=m.chat.id, text="Se han enviado todos los magnets a qbittorrent", parse_mode="HTML") 

#------------------------------------------------
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
# Si es un .zip, extrae solo los archivos 
# .torrent y los agrega al qbittorrent
#------------------------------------------------

def descargar_archivos(bot, update):

	m=update.message		
	filename=m.document.file_name		
	archivo = bot.getFile(m.document.file_id)	
	DownloadFile(archivo.file_path, filename)

	if filename.endswith('.torrent'):		
		call(['qbittorrent-nox', filename])
		bot.send_message(chat_id=m.chat.id, text="El archivo <b>"+filename+"</b> se ha añadido al qbittorrent con exito", parse_mode="HTML") 	

	if filename.endswith('.txt'):
		regex = r"magnet:\?xt=urn:btih:(.+?)&dn=[\w\W]+?.torrent"
		test_str=open(filename, 'r').read()
		matches = re.finditer(regex, test_str)
		for lista in matches:	
			call(['qbittorrent-nox', 'magnet:?xt=urn:btih:'+str(lista.group(1))])
		bot.send_message(chat_id=m.chat.id, text="Se han enviado todos los magnets de <b>"+filename+"</b> a qbittorrent", parse_mode="HTML") 	

	if filename.endswith('.zip'):				
		DownloadFile(archivo.file_path, filename)				
		zf = zipfile.ZipFile(filename, "r")
		for torrents in zf.namelist():
			if os.path.dirname(torrents)=='' and torrents.endswith('.torrent'):
				zf.extract(torrents, 'archivos/')					
				call(['qbittorrent-nox', 'archivos/'+torrents])					
				remove('archivos/'+torrents)
		zf.close()					

		bot.send_message(chat_id=m.chat.id, text="Se han guardado los archivos de <b>"+filename+"</b> en la carpeta", parse_mode="HTML")

	remove(filename)		

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))
 
 
def main():
    updater = Updater("Escribe aquí tu token")
    dp = updater.dispatcher
    
    dp.add_handler(MessageHandler(Filters.document, descargar_archivos)) 
    dp.add_handler(MessageHandler(Filters.text, capturar_texto))
    dp.add_error_handler(error)
    updater.start_polling(clean=True)
    updater.idle() 
 
if __name__ == '__main__':
    main()
  
