# telegram
Pondré ejemplos de diferentes bots

Para usar estos scripts deberás crearte un bot, uno por cada script que tengas.

Aquí tienes las instrucciones para crearlos:
https://telegra.ph/C%C3%B3mo-crear-un-bot-con-botfather-09-26

A continuación haré un pequeño resumen de los scripts subidos


AddToQbitTorrent.py:
Cuando añades un .torrent/magnet/.txt con magnets/.zip con torrents añade el contenido a qbittorrent. 
En el último caso, descomprime el .zip y añade los torrents.
Todos los archivos añadidos a telegram en cualquier modalidad se borran al añadirse a qbittorrent.

AddToQbitTorrentFolder.py:
Cuando añades un .torrent/.zip con .torrrent en su interior, estos se guardan localmente en una carpeta para que pueda ser leida por un programa, por ejemplo el DownloadStation.

BuscaTorrentsInline.py:
Busca contenido en https://www.skytorrents.lol/ y muestra los resultados de la búsqueda en el bot de forma inline. Mostrará primero el que más semillas (seeders) tenga. Le he añadido que busque en las dos primeras páginas y que si el magnet no tiene semillas, que no lo muestre en el inline.

smartplug.py:
El bot crea un botón con el que puedes controlar el estado del enfuche con wifi TP-Link HS100, en otras palabras, podrás encenderlo y apagarlo desde telegram.

Telegram2Twitter.py:
Envía el mensaje que le escribas al bot a tu cuenta de Twitter.

tts_descargas.py:
Este bot tiene 2 funciones:
/audio texto, convierte el texto que le hayas escrito en un audiomensaje que luego envía a telegram.
/descargar enlace, descarga el enlace de forma local, lo comprime en partes de 45mb. y las envía a telegram, perfecto cuando estás en la calle con datos y quieres ir bajándote algo.

Youtube2Mp3Telegram.py:
Una vez introducido un enlace de youtube, el bot descargará video, extraerá el audio en 192khz y lo enviará a telegram, borrando después el vídeo.

Youtube2Mp3InlineTelegram.py:
Igual que el anterior más un buscador inline de youtube


Si quieres apoyar para que siga desarrollando, te dejo mi paypal: 
alfiles@gmail.com
