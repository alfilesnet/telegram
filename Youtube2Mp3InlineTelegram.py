from __future__ import unicode_literals
import youtube_dl
from shutil import move
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler, InlineQueryHandler, CallbackQueryHandler)
from telegram import (InlineQueryResultArticle, ParseMode, InputTextMessageContent, MessageEntity, InlineKeyboardButton, InlineKeyboardMarkup)
from uuid import uuid4
import telegram


def sin_tildes(s):
	import unicodedata
	return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))  

def descargar_mp3(bot, update, chat_id, mid, url_video):

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
		info = ydl.extract_info(url_video, download=True)
		archivo = ydl.prepare_filename(info)
		archivo=archivo.replace('webm', 'mp3').replace('wav', 'mp3').replace('ogg', 'mp3').replace('m4a', 'mp3')
		archivop=sin_tildes(archivo).replace('|', '').replace('¡', '').replace('!', '').replace('?', '').replace('¿', '').replace('\'', '')
		move (archivo, 'audios/'+archivop)
		try:			
			bot.edit_message_text(chat_id=chat_id, message_id=mid, text='El archivo se ha convertido, enviando...')		
		except Exception as e:
			print ('error editando el txt final')
			print (e)

	return (archivop)	


def file_get_content(url):  
	import requests
	session = requests.Session()
	session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0'
	resp = session.get(url)
	resp.encodign='utf-8'
	return resp.text

def indexof(haystack, needle, n=1):
	start = haystack.find(needle)
	while start >= 0 and n > 1:
		start = haystack.find(needle, start+len(needle))
		n -= 1
	return start  


def search_videos(keywords):
	import requests

	keywords=keywords.replace(' ','+')

	#=====================================================================
	# Proceso para conseguir la Key de google:
	#=====================================================================
	#
	# Necesitas ir a https://developers.google.com/ y darte de alta para 
	# conseguir las credenciales --> &key= <-- 

	url='https://www.googleapis.com/youtube/v3/search?part=snippet&q='+keywords+'&maxResults=25&key=CREDENCIALES'

	r = requests.get(url)
	s=(r.json())

	videos=[]

	for datos in s['items']:
		try:
			videos.append([datos['id']['videoId'],datos['snippet']['title'], datos['snippet']['thumbnails']['high']['url']])
		except: 
			pass    
	return (videos)


def inline(bot, update):
	
	resultados=[]

	if str(update.inline_query.query)!='':
		TU_USER_ID=1234567 #<-- Debes poner tu ID de usuario de telegram
		if update.inline_query.from_user.id == TU_USER_ID:
			print (str(update.inline_query.from_user.first_name)+' - '+str(update.inline_query.query))			
			data=search_videos(update.inline_query.query)

			if len(data)>0:

				for datos in data:
					if indexof(datos[1], 'movieposter')<0:
						title=datos[1]
						poster=datos[2]					
						yt_id=datos[0]

						try:
							resultados.append(InlineQueryResultArticle(id=uuid4(), title=str(title), input_message_content=InputTextMessageContent('https://www.youtube.com/watch?v='+yt_id), reply_markup=None, url=None, hide_url=False, description='', thumb_url=poster, thumb_width=640, thumb_height=480))
						except Exception as e:
							print (e)
			else:
				resultados.append(InlineQueryResultArticle(id=uuid4(), title=str('Has superado el límite diario'), input_message_content=InputTextMessageContent('Has superado el límite diario. Compárteme los videos desde la app de youtube'), reply_markup=None, url=None, hide_url=False, description='Compárteme los videos desde la app de youtube', thumb_url='', thumb_width=640, thumb_height=480))	
		else:
			resultados.append(InlineQueryResultArticle(id=uuid4(), title=str('No estas autorizad@'), input_message_content=InputTextMessageContent('No estas autorizado para utilizar el bot'), reply_markup=None, url=None, hide_url=False, description='para utilizar el bot', thumb_url='', thumb_width=640, thumb_height=480))
		
		update.inline_query.answer(resultados, cache_time=1, is_personal=True)


def capturando_enlaces_de_youtube(bot, update):

	m=update.message

	TU_USER_ID=1234567 #<-- Debes poner tu ID de usuario de telegram

	if m.from_user.id == TU_USER_ID:

		try:		
			aviso=bot.send_message(m.chat.id, 'Descargando el video...')
			filename=descargar_mp3(bot, update, m.chat.id, aviso.message_id, m.text)
			print(filename)
			try:
				bot.send_document(m.chat.id, open('audios/'+sin_tildes(filename), 'rb'), caption=filename[:-4])
			except Exception as e:
				print ('error al enviar el archivo')
				print (e)

			bot.delete_message(m.chat.id, aviso.message_id)
			bot.delete_message(m.chat.id, m.message_id)
		except Exception as e:
			print (e)
			bot.send_message(m.chat.id, 'No has puesto una url de youtube\nEn caso de haberlo hecho, ponla de nuevo', parse_mode="HTML")
	else:

		if m.text!='No estas autorizado para utilizar el bot':
			bot.send_message(m.chat.id, 'No estás autorizad@ a utilizar el bot', parse_mode="HTML")		

def main():

	updater = Updater("Escribe aquí tu token")
	dp = updater.dispatcher
	dp.add_handler(InlineQueryHandler(inline))
	dp.add_handler(MessageHandler(Filters.text, capturando_enlaces_de_youtube))
	updater.start_polling(clean=True)
	updater.idle()


if __name__ == '__main__':
	main()
