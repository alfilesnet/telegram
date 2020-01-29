#==============
# Bases de datos
#==============
#--------------
# tabla_a:
#--------------
#
# SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
# SET time_zone = "+00:00";
#
# CREATE TABLE `tabla_a` (
#   `id` int(255) NOT NULL,
#   `user_id` varchar(255) NOT NULL,
#   `first_name` varchar(255) NOT NULL,
#   `hashtag` varchar(255) NOT NULL,
#   `texto` varchar(255) NOT NULL,
#   `datatime` datetime NOT NULL,
#   `activo` int(11) NOT NULL,
#   `cogido_uid` varchar(255) NOT NULL,
#   `cogido_fn` varchar(255) NOT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
#
# ALTER TABLE `tabla_a`
#   ADD PRIMARY KEY (`id`);
#
# ALTER TABLE `tabla_a`
#   MODIFY `id` int(255) NOT NULL AUTO_INCREMENT;

#--------------
# tabla_b:
#--------------
#
# SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
# SET time_zone = "+00:00";
#
# CREATE TABLE `tabla_b` (
#   `msg_id` int(255) NOT NULL,
#   `datetime` datetime NOT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
#
# ALTER TABLE `tabla_b`
#  ADD PRIMARY KEY (`msg_id`);


#==============
# Script python (bot)
#==============

#==========================================
# Importo las librerías necesarias
#==========================================
import re
from datetime import datetime
import json	
import logging
import os
import pymysql
from os import remove
from shutil import move, rmtree
from subprocess import check_output
import requests
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler, InlineQueryHandler, CallbackQueryHandler)
from telegram import (InlineQueryResultArticle, ParseMode, InputTextMessageContent, MessageEntity, InlineKeyboardButton, InlineKeyboardMarkup, Document)
import telegram
import urllib.request

#=====================================================
# Guarda los id de los mensajes a borrar
#=====================================================
def keep_msg_to_delete(msg_id, msg_id_msg):
	u = datetime.now()
	right_now=u.strftime('%Y/%m/%d %H:%M:%S')
	try:
		conexion=conection()
		cursor = conexion.cursor()   
		if int(msg_id)>0:
			cursor.execute("INSERT INTO tabla_b VALUES ('%s', '%s')" % (msg_id, right_now))
			conexion.commit()
		cursor.execute("INSERT INTO tabla_b VALUES ('%s', '%s')" % (msg_id_msg, right_now))
		conexion.commit()   
		cursor.close()
		conexion.close()                            
	except Exception as e:
		print (e)

#=====================================================
# Creo la función para hacer un indexof
#=====================================================
def indexof(haystack, needle, n=1):
	start = haystack.find(needle)
	while start >= 0 and n > 1:
		start = haystack.find(needle, start+len(needle))
		n -= 1
	return start       

#=====================================================
# Creo la función para crear el menu inline
#=====================================================
def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

#=====================================================
# Creo la función para conectarme a la base de datos
#=====================================================
def conection():
	connection = pymysql.connect(host="localhost", user="usuario", passwd="contraseña", db="base_de_datos", charset="utf8")
	return connection

#==========================================
# Avisa cuando hay un error
#==========================================
def error(bot, update, error):
	logger.warn('Update "%s" caused error "%s"' % (update, error))


#==========================================
# Devuelve el texto y el hashtag
#==========================================
def return_hash_text(text):	
	text=text.split(' ')
	t=''
	for a in text[1:]:
		t+=a+' '
	return [text[0],t[:-1], len(text)]


#==========================================
# Defino quienes son los admins
#==========================================
def admins():
	admins=[12345, 67890]
	return admins

#==========================================
# Guardo los datos en la DB
#==========================================
def guardar_en_db(uid, first_name, hashtag, texto):
	i = datetime.now()
	ahora=i.strftime('%Y/%m/%d %H:%M:%S')
	conexion=conection()
	cursor = conexion.cursor()
	cursor.execute("INSERT INTO tabla_a VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % ('0', uid, first_name, hashtag, texto, ahora, '1', '',''))
	conexion.commit()
	cursor.close()
	conexion.close()


#==========================================
# BORRAR UNA ENTRADA
#==========================================
def delete_entry(number):
	conexion=conection()
	cursor = conexion.cursor()

	try:
		cursor.execute("SELECT texto FROM tabla_a where id='%s' and activo!='0'" % (str(number)))
		salida=str('<i>'+cursor.fetchone()[0])+'</i> se ha solucionado con éxito'

		cursor.execute("UPDATE tabla_a SET activo='0' WHERE id='%s'" % (str(number)))
		conexion.commit()
	except:
		salida='No existe esa entrada'
	
	cursor.close()
	conexion.close()
	return salida

#==========================================
# MARCAR UNA ENTRADA
#==========================================
def mark_entry(number):
	conexion=conection()
	cursor = conexion.cursor()

	try:
		cursor.execute("SELECT texto FROM tabla_a where id='%s' and activo='1'" % (str(number)))
		salida=str('<i>'+cursor.fetchone()[0])+'</i> se ha marcado con éxito'

		cursor.execute("UPDATE tabla_a SET activo='2' WHERE id='%s'" % (str(number)))
		conexion.commit()
	except:
		salida='No existe la entrada o ya está marcada'
	
	cursor.close()
	conexion.close()
	return salida	

#==========================================
# COGER UNA ENTRADA POR UN ADMIN 
#==========================================
def cojo_entry(uid, fn, number):	
	conexion=conection()
	cursor = conexion.cursor()

	try:
		cursor.execute("SELECT texto FROM texto_a where id='%s' and activo!='0'" % (str(number)))
		salida=str('<i>'+cursor.fetchone()[0])+'</i> lo ha cogido '+str(fn)

		cursor.execute("UPDATE texto_a SET cogido_uid='%s',cogido_fn='%s' WHERE id='%s'" % (str(uid), str(fn), str(number)))
		conexion.commit()
	except:
		salida='No existe la entrada o ya está marcada'
	
	cursor.close()
	conexion.close()
	return salida	


#==========================================
# Captura los enlaces que se escriben en 
# telegram
#==========================================

def captura_enlaces(bot, update):
	try:
		m=update.message		
		texto=m.text					
		texto = str(texto).strip()
		uid=m.from_user.id			
		fn=m.from_user.first_name
		#----------------------------------------
		# Si el texto empieza con #
		#----------------------------------------
		if texto.startswith('#'):		
			#----------------------------------------
			# Devuelve el hashtag, el texto y cuantas
			# palabras tiene el texto
			#----------------------------------------		
			ht=return_hash_text(texto)

			try:
				
				#·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-
				# Si tiene más de 1 palabra, incluyendo 
				# el hashtag...
				#·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-			
				if ht[2]>1:
					hash_p=ht[0].lower()
					texto_p=ht[1]			
					len_p=ht[2]
					#········································
					# Guardo el contenido en la DB
					#········································
					guardar_en_db(uid, fn, hash_p, texto_p)
					id_help_message=bot.send_message(m.chat.id, 'La entrada se ha añadido correctamente')											
				#·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-
				# Si no...		
				#·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-·-				
				else:
					print ('No se ha escrito #algo')

			except Exception as e:
				print (e) 				
	except Exception as e:
		print (e)


#=====================================================
# Creo la función para crear la lista de peticiones
# errores, etc... de forma dinámica
#=====================================================

def get_content():
	try:
		conexion=conection()
		cursor = conexion.cursor()
		
		cursor.execute("SELECT hashtag FROM tabla_a where activo!='0' GROUP BY hashtag order by 1")
		hashs = cursor.fetchall()

		salida=''

		for h in hashs:		
			salida+=h[0]
			cursor.execute("SELECT * FROM tabla_a where hashtag='%s' and activo!='0' order by 1 desc limit 20" % (h))
			datos = cursor.fetchall()
			for d in datos:

				if d[8]!='':
					cogido='[🕺🏻 '+str(d[8])+'] '
				else:
					cogido=''

				if d[6]==1:
					salida+='\n'+str(d[0])+') '+cogido+d[4]
				elif d[6]==2:
					salida+='\n<pre>'+str(d[0])+') ✅'+cogido+d[4]+'</pre>'
			salida+='\n\n'
		cursor.close()
		conexion.close()	

		return salida
	except Exception as e:
		print (e)
	

def button(bot, update):
	
	try:
		contenido=update.callback_query.data
		cid=update.callback_query.message.chat.id	
		uid=update.callback_query.message.from_user.id
		mid=update.callback_query.message.message_id
		data=re.search(r"(.+?)_(.+?)_(.+)", contenido)
		seccion=data.group(1)
		item=data.group(2)
		from_user=data.group(3)
		if seccion=='0':			
			boton=[]
			boton.append(InlineKeyboardButton('Refrescar', callback_data='0_0_'+str(uid)))		
			reply_markup=InlineKeyboardMarkup(build_menu(boton, 2))		
			bot.answer_callback_query(update.callback_query.id, text="Lista refrescada")			
			bot.edit_message_text(chat_id=cid, message_id=mid, text=get_content(), reply_markup=reply_markup, parse_mode="HTML", disable_web_page_preview="True")					


	except Exception as e:
		bot.answer_callback_query(update.callback_query.id, text="No ha habido cambios")
		print (e)

def lista(bot, update):
	m=update.message	
	uid=m.from_user.id
	boton=[]
	try:
		boton.append(InlineKeyboardButton('Refrescar', callback_data='0_0_'+str(uid)))		
		reply_markup=InlineKeyboardMarkup(build_menu(boton, 2))
		id_help_message=bot.send_message(m.chat.id, get_content(), parse_mode="HTML", reply_markup=reply_markup, disable_web_page_preview="True")
	except Exception as e:
		print (e)

def rm(bot, update):
	m=update.message
	texto=m.text
	texto = str(texto).strip()[4:]

	if m.from_user.id in admins():

		try:
			texto=int(texto)
			id_help_message=bot.send_message(m.chat.id, delete_entry(texto), parse_mode="HTML")
			keep_msg_to_delete(m.message_id, id_help_message.message_id)	
		except Exception as e:
			print (e)
			id_help_message=bot.send_message(m.chat.id, 'Debes escribir el número de entrada')
			keep_msg_to_delete(m.message_id, id_help_message.message_id)	

	else:
		id_help_message=bot.send_message(m.chat.id, 'No tienes permisos para ejecutar este comando')
		keep_msg_to_delete(m.message_id, id_help_message.message_id)	


def marcar(bot, update):
	m=update.message
	texto=m.text
	texto = str(texto).strip()[8:] 

	try:
		texto=int(texto)
		id_help_message=bot.send_message(m.chat.id, mark_entry(texto), parse_mode="HTML")
		keep_msg_to_delete(m.message_id, id_help_message.message_id)	
	except Exception as e:
		print (e)
		id_help_message=bot.send_message(m.chat.id, 'Debes escribir el número de entrada')
		keep_msg_to_delete(m.message_id, id_help_message.message_id)	


def cojo(bot, update):
	m=update.message
	texto=m.text
	texto = str(texto).strip()[6:] 
	uid = m.from_user.id
	fn=m.from_user.first_name

	if m.from_user.id in admins():
		try:
			texto=int(texto)
			id_help_message=bot.send_message(m.chat.id, cojo_entry(uid, fn, texto), parse_mode="HTML")
		except Exception as e:			
			id_help_message=bot.send_message(m.chat.id, 'Debes escribir el número de entrada')
			keep_msg_to_delete(m.message_id, id_help_message.message_id)	

def ayuda(bot, update):
	m=update.message
	texto="""Para reportar un error o hacer una petición hay que escribir #error o #petición y seguidamente el mensaje, si es un error poner en qué carpeta está para encontrarlo rápidamente.

Para marcar una petición (o error) como solucionado hay que escribir /marcar y el número asociado a la petición o error.

Solo admins) Para marcar una cosa que vais a solucionar y no ponerse a hacer lo mismo a la vez escribir /cojo y el número.

Solo admins) Para borrar una entrada escribir /rm y el número."""
	bot.send_message(m.chat.id, texto, parse_mode="HTML")


#==========================================
# Se inicializa el bot
#==========================================

def main():
	updater = Updater("BOT_TOKEN")
	dp = updater.dispatcher	
	dp.add_handler(MessageHandler(Filters.text, captura_enlaces))
	dp.add_handler(CallbackQueryHandler(button))
	dp.add_handler(CommandHandler("ayuda", ayuda))
	dp.add_handler(CommandHandler("cojo", cojo))
	dp.add_handler(CommandHandler("lista", lista))
	dp.add_handler(CommandHandler("marcar", marcar))
	dp.add_handler(CommandHandler("rm", rm))
	
	
	dp.add_error_handler(error)
	updater.start_polling(clean=True)
	updater.idle()


if __name__ == '__main__':
	main()
