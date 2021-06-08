#!/usr/bin/env python
from flask import Flask, render_template, request, flash, redirect, url_for
import pika
from flask import json
from flask import Response
from flask import jsonify
import socket
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure,BulkWriteError,DuplicateKeyError
import logging
from logging.handlers import TimedRotatingFileHandler
import time
from datetime import datetime, timedelta
import motor.motor_asyncio

app = Flask(__name__)

with open('config.json', 'r') as f:
    config = json.load(f)

api_hostname = socket.gethostname() # apenas para mostrar o hostname nos logs
FORMATTER = logging.Formatter('{"asctime":"%(asctime)s","backend":"%(name)s","level":"%(levelname)s","mensagem":"%(message)s"}')
FORMATTER2 = logging.Formatter("%(asctime)s — %(name)s — [%(levelname)s] — %(message)s")
LOG_FILE = "api.log"


logger = logging.getLogger(api_hostname)
logger.setLevel(logging.DEBUG)
# cria um arquivo de log (DEBUG level)
fh = logging.FileHandler('api.log')
fh.setLevel(logging.DEBUG)
# cria um log no console com um nível mais alto
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(FORMATTER)
fh.setFormatter(FORMATTER)
logger.addHandler(ch)
logger.addHandler(fh)


# espera alguns segundos - tempo para subir rabbitmq e mongodb e ldap
sleepTime = 10 
logger.debug('[*] Sleeping for  %s seconds.', sleepTime)
time.sleep(sleepTime)


# MONGO CONNECTION
logger.debug('starting mongoDB connection')
try:
    client = motor.motor_asyncio.AsyncIOMotorClient(host=config["MONGO"]["HOST"],
        port = int(config["MONGO"]["PORT"]),
        username = config["MONGO"]["USERNAME"],
        password = config["MONGO"]["PASSWORD"]
    )
    db = client.paredao
    teste = await db.votacao.find_one({'id_votacao':'votacao_01'})

    logger.debug("mongoDB connected")
except: # MELHORAR TRATAMENTO DE EXCECOES
    logger.error("mongoDB server not available")

logger.debug("READY")

@app.route('/')
def index():
    """
    Apenas um index para verificar se a API está acessível
    :return: OK
    """
    response = app.response_class(
        response='OK',
        status=200
        #mimetype='application/json'
    )
    response.headers.add("Access-Control-Allow-Origin", "*")
    logger.info("%s - HIT /", api_hostname)
    return response

# curl -H "Content-type: application/json" -X POST -i localhost:5000/api/v1/<queue_name> -d @pessoa.json
@app.route('/votar/<voto>', methods = ['POST'])
def votacao(voto):
    """
    Recebe os votos(um de cada vez) e publica na fila
    :param voto: 1 ou 2
    :return: retorna apenas uma mensagem com a fila e consumer que receberam o dado
    """
    #message = voto
    return_message = " [x] Sent to queue " + voto + " FROM " + socket.gethostname()
    
    if (voto == '1' or voto == '2'):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
            channel = connection.channel()
            channel.queue_declare(queue='votacao', durable=True) # cada voto vai em uma fila diferente
            channel.basic_publish(
                exchange='',
                routing_key='votacao',
                body=voto,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ))
            connection.close()
            status = 200
            logger.info("%s", return_message)
        except:
            status = 503
            logger.error("RABBITMQ connection failed")

    else:
        # melhorar o status e message
        status = 406
        return_message = "NÚMERO DE VOTO INVÁLIDO"


    response = app.response_class(
        response=return_message,
        status=status
        #mimetype='application/json'
    )
    response.headers.add("Access-Control-Allow-Origin", "*")
    logger.info("HIT /votar")
    return response
    #return return_message

@app.route('/total', methods = ['GET'])
def total_votos():
    #total_voto_1 = db.votacao.find_one({"_id":1})['voto_1']
    #total_voto_2 = db.votacao.find_one({"_id":2})['voto_2']

    data = {"vazio": 0}
    try:
        total = db.votacao.aggregate([{
            "$group": { 
                "_id": "null", 
                "total_1": { 
                    "$sum": "$voto_1"
                },
                "total_2": {
                    "$sum": "$voto_2"
                }
            } 
        }])
        lista = list(total)[0]
        total_voto_1 = lista["total_1"]
        total_voto_2 = lista["total_2"]
        last_hour = (datetime.now() - timedelta(hours = 1)).replace(microsecond=0)
        votos_ultima_hora = db.votacao.count_documents({"data": {"$gt": last_hour}})
        data = {
            "voto_1": total_voto_1,
            "voto_2": total_voto_2,
            "votos_ultima_hora": votos_ultima_hora
        }
        status = 200
    except:
        status = 503
        logger.error("MONGODB não foi possível calcular o total de votos")


    #return "voto_1: " + str(db.votacao.find_one({"_id":1})['voto_1']) + ", voto_2: " + str(db.votacao.find_one({"_id":2})['voto_2'])
    #return Response("{'voto_1':total_voto_1}", status=200, mimetype='application/json')
    #return jsonify(total_voto_1,total_voto_2)

    response = app.response_class(
        response=json.dumps(data),
        status=status,
        mimetype='application/json'
    )
    response.headers.add("Access-Control-Allow-Origin", "*")
    logger.info("HIT /total")
    return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True)
    #app.run(host='0.0.0.0')
