import dryscrape
from time import sleep
import sys
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler, InlineQueryHandler, CallbackQueryHandler)
from telegram import (ChatAction, InlineQueryResultArticle, ParseMode, InputTextMessageContent, MessageEntity, InlineKeyboardButton, InlineKeyboardMarkup, Document)
import telegram
import logging

def error(bot, update, error):
	logger.warn('Update "%s" caused error "%s"' % (update, error))

def postear_en_twitter(mensaje):

	#===================================================
	# PARTE 1: PREPARATIVOS
	#===================================================

	#----------------------------------------------------
	# Si se ejecuta en linux, debemos ejecutar la 
	# función start_xvfb()
	#----------------------------------------------------
	if 'linux' in sys.platform:
		dryscrape.start_xvfb()
	
	#----------------------------------------------------
	# Le decimos a que página queremos entrar
	#----------------------------------------------------
	sess = dryscrape.Session(base_url = 'https://www.twitter.com')
	#----------------------------------------------------
	# Se añade la cabecera que estamos usando un  
	# navegador, sino entrarás en twitter como un bot y 
	# seguramente no puedas acceder a él
	#----------------------------------------------------
	sess.set_header("User-Agent", "Mozilla/5.0 (Windows NT 5.1; rv:41.0) Gecko/20100101 Firefox/41.0")
	#----------------------------------------------------
	# Ajusta si quieres que extraiga las imágenes al 
	# scrappear el contenido o no.
	#
	# Para este bot no hace falta, porque lo que va a 
	# hacer es enviar un mensaje
	#----------------------------------------------------
	# True = muestra imágenes
	# False = oculta las imágenes
	sess.set_attribute('auto_load_images', False)

	#----------------------------------------------------
	# Escribe las credenciales para entrar a tu cuenta
	# de Twitter
	#----------------------------------------------------
	email='Escribe tu correo de twitter'           # Debes dejar las comillas
	password='Escribe tu contraseña de twitter'    # Debes dejar las comillas

	try:		
		#===================================================
		# PARTE 2: LOGUEO
		#===================================================
		#----------------------------------------------------
		# Visito https://www.twitter.com
		#----------------------------------------------------
		sess.visit('/')
		#----------------------------------------------------
		# Me voy a la caja de texto de usuario
		#----------------------------------------------------
		q = sess.at_xpath('//*[@id="doc"]/div/div[1]/div[1]/div[1]/form/div[1]/input')
		#----------------------------------------------------
		# Le digo que escriba el email que le he dicho antes
		#----------------------------------------------------
		q.set(email)
		#----------------------------------------------------
		# Me voy a la caja de texto de contraseña
		#----------------------------------------------------
		q = sess.at_xpath('//*[@id="doc"]/div/div[1]/div[1]/div[1]/form/div[2]/input')
		#----------------------------------------------------
		# Le digo que escriba el pass que le he dicho antes
		#----------------------------------------------------
		q.set(password)
		#----------------------------------------------------
		# Le digo que clickee en el botón de Iniciar sesión
		#----------------------------------------------------
		q.form().submit()	

		#===================================================
		# PARTE 3: ESCRIBIR MENSAJE
		#===================================================
		#----------------------------------------------------
		# Le digo que clickee en la caja de texto para 
		# escribir el mensaje
		#----------------------------------------------------
		q=sess.at_xpath('//*[@id="tweet-box-home-timeline"]')
		q.click()
		#----------------------------------------------------
		# Le digo que escriba el mensaje que le paso a la
		# función
		#----------------------------------------------------
		q=sess.at_xpath('/html/body/div[2]/div[3]/div/div[2]/div[2]/div/form/div[2]/textarea')
		q.set(mensaje)	
		#----------------------------------------------------
		# Clickeo en el botón de Twittear
		#----------------------------------------------------
		q = sess.at_xpath('//*[@id="timeline"]/div[2]/div/form/div[3]/div[2]/button')		
		q.click()
		#----------------------------------------------------
		# Hago una pausa de un segundo antes de salir de la
		# función
		#----------------------------------------------------
		sleep(1)
		# sess.render('twitter.png')
	except Exception as e:
		print (e)

def procesar_texto(bot, update):
	m=update.message
	#----------------------------------------------------
	# Extraigo el id de donde estoy hablando 
	# (privado/grupo)
	#----------------------------------------------------
	cid=m.chat.id
	#----------------------------------------------------
	# Extraigo el texto que he escrito 	
	#----------------------------------------------------
	texto=m.text
	#----------------------------------------------------
	# El bot escribe un mensaje tranquilizador al usuario
	#----------------------------------------------------
	bot.send_message(cid, 'El mensaje se está enviando, espera unos segundos')
	#----------------------------------------------------
	# Se ejecuta la función con el parámetro "texto" que
	# es el texto escrito por el usuario
	#----------------------------------------------------	
	postear_en_twitter(texto)
	#----------------------------------------------------
	# El bot escribe un mensaje al usuario de que ya está
	# publicado en Twitter
	#----------------------------------------------------	
	bot.send_message(cid, 'Tu mensaje:\n\n<b>'+texto+'</b>\n\n se ha publicado en Telegram correctamente', parse_mode="HTML")


def main():
	try:        	
		updater = Updater("Escribe aquí tu token")
		dp = updater.dispatcher     
		dp.add_handler(MessageHandler(Filters.text, procesar_texto))
		# dp.add_handler(CommandHandler("start", start))
		# dp.add_handler(InlineQueryHandler(inline))    
		# dp.add_handler(CallbackQueryHandler(button))
		dp.add_error_handler(error)
		updater.start_polling(clean=True)
		updater.idle()
	except Exception as e:
		print (e)

if __name__ == '__main__':
    main()
