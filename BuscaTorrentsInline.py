import re
import requests
import unicodedata
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler, InlineQueryHandler, CallbackQueryHandler)
from telegram import (ChatAction, InlineQueryResultArticle, ParseMode, InputTextMessageContent, MessageEntity, InlineKeyboardButton, InlineKeyboardMarkup, Document)
import telegram
import logging
from time import sleep
from uuid import uuid4

def error(bot, update, error):
	logger.warn('Update "%s" caused error "%s"' % (update, error))

def sin_tildes(s):
	return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))  

def get_html(query):
	cookies = {
		'__cfduid': 'd9345cc1b82d88e67ad6ca9d917e454d51525878283',
		'PHPSESSID': '4j1slh2l54cke0opau2p8g8ci0',
	}

	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
		'DNT': '1',
		'Connection': 'keep-alive',
		'Upgrade-Insecure-Requests': '1',
		'Pragma': 'no-cache',
		'Cache-Control': 'no-cache',
	}

	params1 = (
		('query', query),
		('sort', 'seeders'),
		('page', '1'),
	)

	params2 = (
		('query', query),
		('sort', 'seeders'),
		('page', '2'),
	)

	response = requests.get('https://www.skytorrents.lol/', headers=headers, params=params1, cookies=cookies)
	html=sin_tildes(response.text)
	response = requests.get('https://www.skytorrents.lol/', headers=headers, params=params2, cookies=cookies)
	html+=sin_tildes(response.text)	
	return sin_tildes(html)

def buscar_magnets(set_query):
	html=get_html(set_query.replace(' ','+'))
	regex = r"break-word;\"> <a href=\"[\w\W]+?\">(.+?)</a>[\w\W]+?<a href=\"(.+?)\" rel=\"nofollow\"><img alt=\"[\w\W]+?href=\"(.+?)\" rel=\"nofollow\"[\w\W]+?\"label label-[\w\W]+?\">(.+?)</a>[\w\W]+?<td class=\"is-hidden-touch\">(.+?)</td>[\w\W]+?green;\">(.+?)<\/td>[\w\W]+?red;\">(.+?)</td>"
	matches=re.finditer(regex, html)
	array=[[],[],[],[],[]]
	for match in matches:
		title=match.group(1)
		magnet=match.group(3)+'.torrent'
		try:
			size=match.group(5)	
		except:
			size=''

		try:
			seeder=match.group(6)	
		except:
			seeder='0'

		try:
			leecher=match.group(7)	
		except:
			leecher='0'
				
		if int(seeder)>0:				
			array[0].append(title)
			array[1].append(magnet)
			array[2].append(size)
			array[3].append('Seeders: '+str(seeder))
			array[4].append('Leecher: '+str(leecher))
	return array

def inline(bot, update):	

	contenidos=buscar_magnets(update.inline_query.query)
	resultados=[]
	try:		
		if len(contenidos[0])>0:
			for e,contenido in enumerate(contenidos[0]):
				salida=''
				salida+=('<b>'+contenidos[0][e]+'</b>\n\n')
				salida+=('<b>'+contenidos[1][e]+'</b>\n\n')
				salida+=('<b>'+contenidos[2][e]+'</b>\n')
				salida+=('<b>'+contenidos[3][e]+'</b>\n')
				salida+=('<b>'+contenidos[4][e]+'</b>\n')							
				desc=contenidos[3][e]+'\n'+contenidos[4][e]
				resultados.append(InlineQueryResultArticle(id=uuid4(), title=str(contenidos[0][e]), input_message_content=InputTextMessageContent(salida, parse_mode="HTML"), reply_markup=None, description=desc))
				salida=''
		else:
			resultados.append(InlineQueryResultArticle(id=uuid4(), title='Busca por otro nombre', input_message_content=InputTextMessageContent('Busca por otro nombre', parse_mode="HTML"), reply_markup=None))

		update.inline_query.answer(resultados, cache_time=1)			
	except Exception as e:
		bot.send_message(update.inline_query.from_user.id, 'Falló, vuelva a buscar')

def main():
	updater = Updater("ESCRIBE AQUÍ TU TOKEN")
	dp = updater.dispatcher                
	dp.add_handler(InlineQueryHandler(inline))
	dp.add_error_handler(error)
	updater.start_polling(clean=True)
	updater.idle()

if __name__ == '__main__':
	main()
