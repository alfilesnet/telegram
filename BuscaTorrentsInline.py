from sys import stdout
import dryscrape
import logging
import re
import requests
import unicodedata
from uuid import uuid4
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler, InlineQueryHandler, CallbackQueryHandler)
from telegram import (ChatAction, InlineQueryResultArticle, ParseMode, InputTextMessageContent, MessageEntity, InlineKeyboardButton, InlineKeyboardMarkup, Document)
import telegram
from time import sleep



def error(bot, update, error):
	logger.warn('Update "%s" caused error "%s"' % (update, error))

def sin_tildes(s):
	return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))  

def start_sess():
	dryscrape.start_xvfb()
	sess = dryscrape.Session()
	sess.set_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0")
	sess.set_attribute('auto_load_images', 0)
	print ('Visitando skytorrents')
	sess.visit('https://www.skytorrents.lol/')		
	print ('Saltando la proteccion de Cloudflare...')
	for a in range(10,0,-1):
		if a<10:
			b='0'+str(a)
		else:
			b=str(a)

		stdout.write("\r"+str(b))
		stdout.flush()			
		sleep(1)
	stdout.write("\033[K") #clear line
	stdout.flush()
	print ()
	print ('Ya puedes usar el buscador inline en Telegram')
	return (sess)


sess=start_sess()

def get_html(sess,query):	

	html=''

	query = query.replace(' ', '+')
	sess.visit('https://www.skytorrents.lol/?query='+query+'&sort=seeders&page=1')
	html+=sess.body()
	sess.visit('https://www.skytorrents.lol/?query='+query+'&sort=seeders&page=2')
	html+=sess.body()
	return html

def buscar_magnets(sess, set_query):
	try:
		html=get_html(sess, set_query.replace(' ','+'))		
		regex = r"<td style=\"word-wrap: break-word;\">[\w\W]*?<a[\w\W]*? href=\"[\w\W]+?\">(.+?)<\/a>[\w\W]+?<a href=\"(.+?)\" rel=\"nofollow\">[\s]*?<img alt=\"[\w\W]+?href=\"(.+?)\" rel=\"nofollow\"[\w\W]+?\"label label-[\w\W]+?\">(.+?)<\/a>[\w\W]+?<td class=\"is-hidden-touch\">(.+?)<\/td>[\w\W]+?green;\">(.+?)<\/td>[\w\W]+?red;\">(.+?)<\/td>"
		matches=re.finditer(regex, html)
		array=[[],[],[],[],[]]

		try:
			for match in matches:				
				title=str(match.group(1))

				magnet=str(match.group(3)+'.torrent')
				try:
					size=str(match.group(5))
				except Exception as e:					
					size='0'
					print (e)

				try:
					seeder=str(match.group(6))
				except:
					seeder='0'

				try:
					leecher=str(match.group(7))
				except:
					leecher='0'				
						
				if int(seeder.replace(',', ''))>0:				
					array[0].append(title)
					array[1].append(magnet)
					array[2].append(size)
					array[3].append('Seeders: '+seeder)
					array[4].append('Leecher: '+leecher)
		except Exception as e:
			print (e)
		return array
	except Exception as e:		
		print (e)

def inline(bot, update):	

	try:
		contenidos=buscar_magnets(sess, update.inline_query.query)
	except Exception as e:
		print (e)

	resultados=[]
	try:		
		if len(contenidos[0])>0:
			for e,contenido in enumerate(contenidos[0]):
				salida=''
				salida+=('<b>'+str(contenidos[0][e])+'</b>\n\n')
				salida+=('<b>'+str(contenidos[1][e])+'</b>\n\n')
				salida+=('<b>'+str(contenidos[2][e])+'</b>\n')
				salida+=('<b>'+str(contenidos[3][e])+'</b>\n')
				salida+=('<b>'+str(contenidos[4][e])+'</b>\n')							
				desc=str(contenidos[3][e])+'\n'+str(contenidos[4][e])
				resultados.append(InlineQueryResultArticle(id=uuid4(), title=str(str(contenidos[0][e])), input_message_content=InputTextMessageContent(salida, parse_mode="HTML"), reply_markup=None, description=desc))
				salida=''
		else:
			resultados.append(InlineQueryResultArticle(id=uuid4(), title='Busca por otro nombre', input_message_content=InputTextMessageContent('Busca por otro nombre', parse_mode="HTML"), reply_markup=None))

		update.inline_query.answer(resultados, cache_time=1)			
	except Exception as e:
		bot.send_message(update.inline_query.from_user.id, 'Fallo, vuelva a buscar')

def main():
	try:
		updater = Updater("Escribe aquí tu token")
		dp = updater.dispatcher                
		dp.add_handler(InlineQueryHandler(inline))
		dp.add_error_handler(error)
		updater.start_polling(clean=True)
		updater.idle()
	except Exception as e:
		print (e)

if __name__ == '__main__':
	main()
