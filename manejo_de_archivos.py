import os
import binascii
from io import StringIO
import telebot
import file
import requests

token = os.environ["BOT_TELEGRAM_FILE_HANDLER"]

bot = telebot.TeleBot(token , parse_mode=None) # You can set parse_mode by default. HTML or MARKDOWN
save_command_received = ""

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome = """
    Hola, este bot te permite trabajar tus archivos como:
    - /base64 encode: Transformar archivos a base64
    - /base64 decode: Transforma base 64 a un archivo
    - /pdf merge: Junta distintos pdf a un solo pdf 
    - /pdf split: corta un pdf .... buscar cual metodo
    - /pdf unlock: desbloquea un pdf
    - /pdf lock: Protege un pdf
    - /pdf añadir marca de agua
    - /pdf extrae texto y fotos, rotar pdf, 
    - /convertir imagenes a pdf, png, ico, svg, ......
    - 
    """
    bot.reply_to(message, welcome)


@bot.message_handler(commands=['base64'])
def base64_handler(message):
    global save_command_received
    text = message.text         #obtiene el texto del mensaje
    if "encode" in text:
        save_command_received = "encode"
        bot.send_message(message.chat.id, "Envia el archivo que quieres convertir a base64")  #reply_to responde el mensaje y send_message envia un mensaje nuevo
        

    if "decode" in text:
        save_command_received = "decode"
        bot.send_message(message.chat.id, "Envía tu archivo txt con el código en base64")
    

@bot.message_handler(content_types=['document', 'photo']) 
def file_sent(message):
    global save_command_received
    document = message.document
    if document is None:
        document = message.photo[-1]
        
    file_info = bot.get_file(document.file_id)   #obtiene la info del documento subido
    file_read = bot.download_file(file_info.file_path) #obtiene el documento (hago un get a la api) el doc esta en memoria

    if save_command_received == "encode":
        encode_check = file.codificar(file_read=file_read)
        if len(encode_check) > 4095:
            file_like_io = StringIO(encode_check)
            bot.send_document(message.chat.id, file_like_io, visible_file_name="encode.txt")
        else:
            bot.reply_to(message, encode_check)
    
    if save_command_received == "decode":
        try:
            decode_check= file.decodificar(file_read)
            bot.send_photo(message.chat.id, decode_check)
        except binascii.Error:
            bot.send_message(message.chat.id, "Lo que enviaste no es un base64 valido")


            

@bot.message_handler(content_types=['text']) 
def text_send(message):
    global save_command_received
    text = message.text
    if save_command_received == "decode":
        try:
            decode_check= file.decodificar(text)
            bot.send_photo(message.chat.id, decode_check)
        except binascii.Error:
            bot.send_message(message.chat.id, "Lo que enviaste no es un base64 valido")
        except: 
            pass

    

bot.infinity_polling()