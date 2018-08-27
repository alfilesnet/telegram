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

#------------------------------------------------
# Requisitos
#------------------------------------------------
# pip install telegram --upgrade
# pip install python-telegram-bot --upgrade

# Instalar la librería para poder controlar 
# el enchufe:
# https://github.com/GadgetReactor/pyHS100
#------------------------------------------------

try:
	from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler, InlineQueryHandler, CallbackQueryHandler)
	from telegram import (InlineQueryResultArticle, ParseMode, InputTextMessageContent, MessageEntity, InlineKeyboardButton, InlineKeyboardMarkup)
	import telegram
	#----------------------------------------------
	# Libería para ejectar comandos de linux en 
	# python 🔽
	#----------------------------------------------
	from subprocess import check_output, call

	#----------------------------------------------
	# Libería para ejectar expresiones regulares
	# (regex) 🔽
	#----------------------------------------------
	import re
	
	#----------------------------------------------
  	# Función para crear los botones
  	#----------------------------------------------
	def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
		menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
		if header_buttons:
			menu.insert(0, header_buttons)
		if footer_buttons:
			menu.append(footer_buttons)
		return menu

	#----------------------------------------------
  	# Comprueba el estado actual del botón
  	#----------------------------------------------
	def estado():
		try:
			estado=str(check_output(['pyhs100', '--host', 'IP_DEL_ENCHUFE',  'state']))
			regex = r"Device state: (.+?)\\"
			status=re.search(regex, estado)
			return status.group(1)	
		except:
			return 'OFF'

	#==============================================
  	# Función que muestra el botón
  	#==============================================
	def enchufe(bot, update):
	    
		m=update.message
		status=0
		if estado()=='ON':
			plug='🔘 '
			status=1
		else:
			plug='⚪️ '
			status=0

		keyboard=[]
		keyboard.append(InlineKeyboardButton(plug+'Enchufe-Dormitorio', callback_data=status))
		reply_markup = InlineKeyboardMarkup(build_menu(keyboard, 1))   
		bot.send_message(m.chat.id, 'Dispositivos', parse_mode="HTML", reply_markup=reply_markup) 

	#==============================================
  	# Función que gestiona el botón a través el bot
  	#==============================================
	def button(bot, update):
		try:
			contenido=update.callback_query.data            
			cid=update.callback_query.message.chat.id
			mid=update.callback_query.message.message_id

			if contenido=='1':
				plug='⚪️ '
				status='0'
			else:
				plug='🔘 '
				status='1'

			keyboard=[]
			keyboard.append(InlineKeyboardButton(plug+'Enchufe-Dormitorio', callback_data=status))
			reply_markup = InlineKeyboardMarkup(build_menu(keyboard, 1))

			if contenido=='0':
				estado=call(['pyhs100', '--host', 'IP_DEL_ENCHUFE',  'on'])
				bot.edit_message_text(chat_id=cid, message_id=mid, text='Dispositivos', reply_markup=reply_markup)  

			if contenido=='1':
				try:
					estado=call(['pyhs100', '--host', 'IP_DEL_ENCHUFE',  'off'])
					bot.edit_message_text(chat_id=cid, message_id=mid, text='Dispositivos', reply_markup=reply_markup)  
				except Exception as e:
					print (e)

		except Exception as e:
			print (e)
	 
	def main():
		# Create the EventHandler and pass it your bot's token.

		updater = Updater("INTRODUCE AQUÍ EL TOKEN DE TU BOT")
		dp = updater.dispatcher

		dp.add_handler(CallbackQueryHandler(button))
		dp.add_handler(CommandHandler("enchufe", enchufe))  
    
		# Start the Bot
		updater.start_polling(clean=True)

		# Run the bot until you press Ctrl-C or the process receives SIGINT,
		# SIGTERM or SIGABRT. This should be used most of the time, since
		# start_polling() is non-blocking and will stop the bot gracefully.
		updater.idle()
	 
	 
	if __name__ == '__main__':
		main()
		
except Exception as e:
	print (e)
