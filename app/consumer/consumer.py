#!/usr/bin/env python
import pika
import sys
import time
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure,BulkWriteError,DuplicateKeyError
import json
import socket
from unicodedata import normalize
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from datetime import timedelta

# arquivo com algumas configurações
with open('config.json', 'r') as f:
    config = json.load(f)

consumer_hostname = socket.gethostname() # apenas para mostrar o hostname nos logs

FORMATTER = logging.Formatter('{"asctime":"%(asctime)s","backend":"%(name)s","level":"%(levelname)s","mensagem":"%(message)s"}')
FORMATTER2 = logging.Formatter("%(asctime)s — %(name)s — [%(levelname)s] — %(message)s")
LOG_FILE = "consumer.log"


logger = logging.getLogger(consumer_hostname)
logger.setLevel(logging.DEBUG)
# cria um arquivo de log (DEBUG level)
fh = logging.FileHandler('consumer.log')
fh.setLevel(logging.DEBUG)
# cria um log no console
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(FORMATTER)
fh.setFormatter(FORMATTER)
logger.addHandler(ch)
logger.addHandler(fh)

# espera alguns segundos - tempo para subir rabbitmq e mongodb
sleepTime = 10 
logger.debug('[*] Sleeping for  %s seconds.', sleepTime)
time.sleep(sleepTime)

# MONGO CONNECTION
logger.debug('starting mongoDB connection')
try:
    client = MongoClient(host=config["MONGO"]["HOST"],
        port=int(config["MONGO"]["PORT"]),
        username=config["MONGO"]["USERNAME"],
        password=config["MONGO"]["PASSWORD"]
    )
    database = config["MONGO"]["DATABASE"]
    db = client[database]
    logger.debug("mongoDB connected")
except: # MELHORAR TRATAMENTO DE EXCECOES
    logger.error("mongoDB server not available")



# total = db.votacao.aggregate([{
#     "$group":{ 
#     "_id": { "year":"$y","month":"$m","day":"$d","hour":"$h"},
#     'count':{"$sum":1} 
#     }
# }])

# TODO: 
## TRATAR EXCEPTION QUANDO O BANCO ESTÁ VAZIO...
#db.votacao.insert_one({'_id':1,'voto_1':0})
#db.votacao.insert_one({'_id':2,'voto_2':0})

#print(db.votacao.find_one({"_id":1}))
#print(db.votacao.find_one({"_id":2}))


# rabbitmq CONNECTION
logger.debug('[*] starting rabbitmq connection ...')
fila = config["RABBITMQ"]["FILA"]
try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    # conecta em N filas
    #filas = ['votacao']
    #for fila in filas:
    channel.queue_declare(queue=fila, durable=True)
    logger.debug('rabbitmq connected')
    logger.debug("%s [*] Waiting for messages.", fila)
except:
    logger.error("rabbitmq server not available")

def votacao(body):

    collection = config["MONGO"]["COLLECTION"]
    # if body == b'1':
    #     qtd_votos = db.votacao.find_one({"_id":1})["voto_1"]
    #     qtd_votos += 1
    #     db.votacao.update_one({'_id':1},{'$set': {'voto_1':qtd_votos}})
    #     logger.info("%s - %s [*] voto computado: total voto_1: %s" % (consumer_hostname,fila, qtd_votos))
    # if body == b'2':
    #     qtd_votos = db.votacao.find_one({"_id":2})["voto_2"]
    #     qtd_votos += 1
    #     db.votacao.update_one({'_id':2},{'$set': {'voto_2':qtd_votos}})
    #     logger.info("%s - %s [*] voto computado: total voto_2: %s" % (consumer_hostname,fila, qtd_votos))
    if body == b'1':
        db[collection].insert_one({"id_votacao":"votacao_01","voto_1":1,"voto_2":0,"data":datetime.today().replace(microsecond=0)})
        logger.info("[*] voto computado: voto_1")
    elif body == b'2':
        db[collection].insert_one({"id_votacao":"votacao_01","voto_1":0,"voto_2":1,"data":datetime.today().replace(microsecond=0)})
        logger.info("[*] voto computado: voto_2")
    else:
        logger.error("NÚMERO DE VOTO INVÁLIDO")

def callback(ch, method, properties, body):
    """
    computa os votos
    """
    logger.debug("[x] Received data -> FILA %s", method.routing_key)
    
    if method.routing_key == fila:
        votacao(body)
    #else return algum erro
    
    logger.debug("[x] DONE")
    ch.basic_ack(delivery_tag=method.delivery_tag) 

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=fila, on_message_callback=callback)
channel.start_consuming()