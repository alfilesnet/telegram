from __future__ import unicode_literals
import re
import youtube_dl
from shutil import move
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler, InlineQueryHandler, CallbackQueryHandler)
from telegram import (InlineQueryResultArticle, ParseMode, InputTextMessageContent, MessageEntity, InlineKeyboardButton, InlineKeyboardMarkup)
import telegram


def sin_tildes(s):
	import unicodedata
	return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))  

def descargar_mp3(bot, update, chat_id, mid, id_video):

	class MyLogger(object):
		def debug(self, msg):
			pass

		def warning(self, msg):
			pass

		def error(self, msg):
			print(msg)


	def my_hook(d):
		if d['status'] == 'finished':
			print('Done downloading, now converting ...')     			
			bot.edit_message_text(chat_id=chat_id, message_id=mid, text='El vídeo se ha bajado con éxito y se está convirtiendo')

	ydl_opts = {
		'outtmpl': '%(title)s.%(ext)s',
		'format': 'bestaudio/best',    
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '192',        
		}],
		'logger': MyLogger(),
		'progress_hooks': [my_hook],
	}

	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		uri='https://www.youtube.com/watch?v='+id_video
		info = ydl.extract_info(uri, download=True)
		archivo = ydl.prepare_filename(info)
		archivo=archivo.replace('webm', 'mp3').replace('wav', 'mp3').replace('ogg', 'mp3').replace('m4a', 'mp3')
		archivop=sin_tildes(archivo).replace('|', '').replace('¡', '').replace('!', '').replace('?', '').replace('¿', '').replace('\'', '')
		move (archivo, 'audios/'+archivop)
		bot.edit_message_text(chat_id=chat_id, message_id=mid, text='El archivo se ha convertido, enviando...')				

	return (archivop)	

def capturando_enlaces_de_yt(bot, update):
	try:
		m=update.message		
		regex = r"https://www\.youtube\.com/watch\?v=(.+)"
		yt_id = re.search(regex, m.text.replace('&feature=share', '')).group(1)
		aviso=bot.send_message(m.chat.id, 'Descargando video...')
		filename=descargar_mp3(bot, update, m.chat.id, aviso.message_id, yt_id)
		bot.send_document(m.chat.id, open('audios/'+sin_tildes(filename), 'rb'), caption=filename[:-4])
		bot.delete_message(m.chat.id, aviso.message_id)
		bot.delete_message(m.chat.id, m.message_id)
	except Exception as e:
		print (e)
		bot.send_message(m.chat.id, 'No has puesto una url de youtube\nEn caso de haberlo hecho, ponla de nuevo', parse_mode="HTML")

def main():

	updater = Updater("ESCRIBE AQUÍ TU TOKEN")
	dp = updater.dispatcher
	dp.add_handler(MessageHandler(Filters.text, capturando_enlaces_de_yt))
	updater.start_polling(clean=True)
	updater.idle()


if __name__ == '__main__':
	main()