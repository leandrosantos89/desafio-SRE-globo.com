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
from flasgger import Swagger

app = Flask(__name__)

template = {
  "swagger": "2.0",
  "info": {
    "title": "API do PAREDÃO do BBB",
    "description": "Flask API desenvolvida para o desafio de SRE da globo.com",
    "version": "1.0",
    "contact": {
      "name": "Leandro",
      "url": "https://github.com/leandrosantos89",
    }
  }
}

app.config['SWAGGER'] = {
    'title': 'API - PAREDAO BBB',
    'uiversion': 3,
    "specs_route": "/swagger/"
}
swagger = Swagger(app, template=template)

with open('config.json', 'r') as f:
    config = json.load(f)

api_hostname = socket.gethostname() # apenas para mostrar o hostname nos logs

#.set_format().set_fileHandler().set_consoleHandler()

FORMATTER = logging.Formatter('{"asctime":"%(asctime)s","backend":"%(name)s","level":"%(levelname)s","mensagem":"%(message)s"}')

logger = logging.getLogger(api_hostname)
level = logging.getLevelName(logging.DEBUG)
logger.setLevel(level)
# cria um arquivo de log (DEBUG level)
fh = logging.FileHandler('api.log')
fh.setLevel(level)
# cria um log no console com um nível mais alto
ch = logging.StreamHandler()
ch.setLevel(level)
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
    client = MongoClient(host=config["MONGO"]["HOST"],
        port = int(config["MONGO"]["PORT"]),
        username = config["MONGO"]["USERNAME"],
        password = config["MONGO"]["PASSWORD"]
    )
    db = client.paredao
    logger.debug("mongoDB connected")
except: # MELHORAR TRATAMENTO DE EXCECOES
    logger.error("mongoDB server not available")

logger.debug("READY")

@app.route('/')
def index():
    """Test endpoint
        ---      
        tags:
            - API - Paredao do BBB
        summary: Retorna status 200 e uma mensagem OK 
        responses:
            200:
                description: Successfully hit the api        
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
@app.route('/votar', methods = ['POST'])
def votacao():
    """Voting Endpoint
    ---  
      tags:
        - API - Paredao do BBB
      summary: PAREDAO - um participante tem que sair da casa
      description: Vote em um participante para sair da casa
      parameters:
        - name: voto
          in: body
          description: ID do participante
          required: True
          schema:
            type: object
            properties:
              voto:
                type: integer
                description: ID do participante
      responses:
        200:
          description: Voto computado com sucesso
          schema:
            properties:
              voto:
                type: integer
                description: ID do participante
    """
    
    voto = request.json["voto"]
    voto = str(voto)
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
    )
    response.headers.add("Access-Control-Allow-Origin", "*")
    logger.info("HIT /votar")
    return response
    #return return_message

@app.route('/total', methods = ['GET'])
def total_votos():
    """Total de votos Endpoint
      ---      
      tags:
        - API - Paredao do BBB
      responses:
        200:
          description: Total de votos
          body: OK
    """
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
