#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import datetime
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

TITOLO, AUTORE, ISBN, TEXT, COVER, FOTO, IG, MAIL = range(8)

def start(update, context):
    user = update.message.from_user
    if(user.username is None):
        update.message.reply_text(
            'Ciao '+update.message.from_user.name+', ho bisogno del tuo username per far si che tu possa essere contattato dal compratore... Impostalo e poi riavviami con /new o /start.'
        )
        return ConversationHandler.END
    else:
        if str(user.id) not in list(os.environ['CREATORS_VCL'].split(",")):
            context.user_data['tg'] = user.username
        context.user_data['numero_photo'] = 0
        update.message.reply_text(
            'Ciao! Sono il bot incaricato di ricevere le infomazioni riguardo al libro che vuoi vendere.'
            '\nUsa /cancel per interrompere l\'operazione in qualunque momento.'
        )
        update.message.reply_text(
            'Inserisci il titolo del libro:'
        )
        if(not os.path.isdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), str(user.id)))):
            os.mkdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), str(user.id)))
        return TITOLO

def titolo(update, context):
    user = update.message.from_user
    context.user_data['titolo'] = update.message.text
    update.message.reply_text(
        'Ok, inserisci l\'autore:'
    )
    return AUTORE

def autore(update, context):
    user = update.message.from_user
    context.user_data['autore'] = update.message.text
    update.message.reply_text(
        'Ok, inserisci l\'isbn (attenzione al formato, es. 978-3-16-148410-0):'
    )
    return ISBN

def isbn(update, context):
    user = update.message.from_user
    context.user_data['isbn'] = update.message.text
    update.message.reply_text(
        'Ok, inserisci le informazioni aggiuntive elencate sul sito:'
        '\n- Stato (es. nuovo, usato ecc.)'
        '\n- Come è stato tenuto (es. sottolineature, danni nelle pagine ecc.)'
        '\n\nPer saltare il passaggio usa /skip'
    )
    return TEXT

def text(update, context):
    user = update.message.from_user
    context.user_data['text'] = update.message.text
    update.message.reply_text(
        'Ok, inserisci la foto mostrata come cover sul sito (quella nella ricerca):'
        '\n\nPer saltare il passaggio usa /skip'
    )
    return COVER

def skip_text(update, context):
    update.message.reply_text(
        'Ok, inserisci la foto mostrata come cover sul sito (quella mostrata nella ricerca):'
        '\n\nPer saltare il passaggio usa /skip'
    )
    return COVER

def cover(update, context):
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    filename = 'cover_'+str(datetime.now().strftime('%d%m%Y-%H%M%S_%f'))+'.jpg'
    photo_file.download(os.path.join(os.path.dirname(os.path.abspath(__file__)), str(user.id), filename))
    context.user_data['cover'] = filename
    update.message.reply_text(
        'Ok, inserisci le foto extra (max 8):'
        '\n\nPer saltare il passaggio usa /skip'
    )
    return FOTO

def skip_cover(update, context):
    update.message.reply_text(
        'Ok, inserisci le foto extra (max 8):'
        '\n\nPer saltare il passaggio usa /skip'
    )
    return FOTO

def photos(update, context):
    user = update.message.from_user
    context.user_data['numero_photo'] += 1
    photo_file = update.message.photo[-1].get_file()
    filename = 'foto'+str(context.user_data['numero_photo'])+'_'+str(datetime.now().strftime('%d%m%Y-%H%M%S_%f'))+'.jpg'
    photo_file.download(os.path.join(os.path.dirname(os.path.abspath(__file__)), str(user.id), filename))
    context.user_data['foto'+str(context.user_data['numero_photo'])] = filename
    if(context.user_data['numero_photo'] < 8):
        update.message.reply_text(
            'Ok, passiamo alla prossima foto:'
            '\n\nPer interrompere l\'invio delle foto usa /stop'
        )
        return FOTO
    else:
        update.message.reply_text(
            'Ok, passiamo ai contatti. Inserisci il tuo username instagram:'
            '\n\nPer saltare il passaggio usa /skip'
        )
        return IG

def skip_photos(update, context):
    update.message.reply_text(
        'Ok, passiamo ai contatti. Inserisci il tuo username instagram:'
        '\n\nPer saltare il passaggio usa /skip'
    )
    return IG

def ig(update, context):
    user = update.message.from_user
    context.user_data['ig'] = update.message.text
    update.message.reply_text(
        'Ok, inserisci la tua mail:'
        '\n\nPer saltare il passaggio usa /skip'
    )
    return MAIL

def skip_ig(update, context):
    update.message.reply_text(
        'Ok, inserisci la tua mail:'
        '\n\nPer saltare il passaggio usa /skip'
    )
    return MAIL

def mail(update, context):
    user = update.message.from_user
    context.user_data['mail'] = update.message.text
    update.message.reply_text(
        'Grazie per il tempo dedicato, nel giro di 1-2 giorni vedrai il tuo libro inserito insieme agli altri in vendita sul sito.'
    )
    formatData(update, context, user)
    return ConversationHandler.END

def skip_mail(update, context):
    user = update.message.from_user
    update.message.reply_text(
        'Grazie per il tempo dedicato, nel giro di 1-2 giorni vedrai il tuo libro inserito insieme agli altri in vendita sul sito.'
    )
    formatData(update, context, user)
    return ConversationHandler.END

def cancel(update, context):
    user = update.message.from_user
    update.message.reply_text(
        'Grazie comunque per il tempo dedicato.\nSpero sia solo un arrivederci :(', reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END

def formatData(update, context, user):
    f = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), str(user.id), str(datetime.now().strftime('%Y-%m-%d-%H%M%S_%f'))+'.md'), "w")
    f.write("---\nlayout: post\n")
    if 'cover' in context.user_data.keys():
        f.write("images: [/images/books/"+context.user_data['cover']+",")
    else:
        f.write("images: [")
    for key in context.user_data.keys():
        if "foto" in key:
            f.write("/images/books/"+context.user_data[key]+",")
    f.write("]\n")
    f.write("title: "+context.user_data['titolo']+"\n")
    f.write("author: "+context.user_data['autore']+"\n")
    f.write("isbn: "+context.user_data['isbn']+"\n")
    if 'mail' in context.user_data.keys():
        f.write("mail: "+context.user_data['mail']+"\n")
    if 'ig' in context.user_data.keys():
       f.write("instagram: "+context.user_data['ig']+"\n")
    if 'tg' in context.user_data.keys():
        f.write("telegram: "+context.user_data['tg']+"\n")
    f.write("---\n\n")
    if 'text' in context.user_data.keys():
        f.write(context.user_data['text']+"\n")
    f.close()
    context.user_data.clear()

def main():
    updater = Updater(os.environ['TOKEN_VCL'], use_context=True)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('new', start), CommandHandler('start', start)],
        states={
            TITOLO: [MessageHandler(Filters.text & ~Filters.command, titolo)],
            AUTORE: [MessageHandler(Filters.text & ~Filters.command, autore)],
            ISBN: [MessageHandler(Filters.regex('^(?=(?:\D*\d){10}(?:(?:\D*\d){3})?$)[\d-]+$'), isbn)],
            TEXT: [MessageHandler(Filters.text & ~Filters.command, text), CommandHandler('skip', skip_text)],
            COVER: [MessageHandler(Filters.photo, cover), CommandHandler('skip', skip_cover)],
            FOTO: [MessageHandler(Filters.photo, photos), CommandHandler('stop', skip_photos), CommandHandler('skip', skip_photos)],
            IG: [MessageHandler(Filters.text & ~Filters.command, ig), CommandHandler('skip', skip_ig)],
            MAIL: [MessageHandler(Filters.regex('^[\w\d._%+-]+@[A-Za-z0-9.-]+\.[\w]{2,}$'), mail), CommandHandler('skip', skip_mail)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
