from pickle import TRUE
from urllib import response
from flask import Flask, request, jsonify
from pyngrok import ngrok
from conn import conectar, cerrar
from datetime import datetime
import requests
import sys
import logging
import base64
import json

app = Flask(__name__)


# Replace the values here.
logging.basicConfig(level=logging.DEBUG)

INSTANCE_URL = "https://api.maytapi.com/api"
PRODUCT_ID = "440ec908-2ec1-4043-a26c-75f9ee4d17f4"
PHONE_ID = "39479"
API_TOKEN = "b3caadf1-9ea9-4793-aa34-bf521c5dca29"


@app.route("/")
def hello():
    return app.send_static_file("index.html")


def send_response(body):
    print("Request Body", body, file=sys.stdout, flush=True)
    url = INSTANCE_URL + "/" + PRODUCT_ID + "/" + PHONE_ID + "/sendMessage"
    headers = {
        "Content-Type": "application/json",
        "x-maytapi-key": API_TOKEN,
    }
    response = requests.post(url, json=body, headers=headers)
    print("Response", response.json(), file=sys.stdout, flush=True)
    count_send()
    return


@app.route("/webhook", methods=["POST"])
def webhook():
    json_data = request.get_json()

    wttype = json_data["type"]
    if wttype == "message":
        message = json_data["message"]
        conversation = json_data["conversation"]
        _type = message["type"]
        if message["fromMe"]:
            return
        
        
        if _type == "location":
            fecha_actual = datetime.now()
            pos = conversation.index("@")  # corte de posicipón
            telefonox = conversation[3:pos]
            telefono = int(telefonox)  # telefono como variable
            resp = 0

            cnx = conectar()
            db = cnx.cursor()
            db.execute(
            "SELECT telefono, valor FROM sesion WHERE telefono = %s", (telefono,))
            results = db.fetchall()
            if results:
                for result in results:

                    qvalor = result[1]
                    qtelefono = result[0]

                    if qvalor == "9999" and resp == 0:
                                    body = {
                                    "type": "text",
                                    "message": "Pronto sera atendido. \n Gracias por preferirnos",
                                    }
                                    body.update({"to_number": conversation})
                                    send_response(body)

                                    estado = "10000"
                                    resp = 1
                                    update_sesion(telefono, estado)

        if _type == "text":
            # Handle Messages
            text = message["text"]
            text = text.lower()
            cnx = conectar()
            fecha_actual = datetime.now()

            pos = conversation.index("@")  # corte de posicipón
            telefonox = conversation[3:pos]
            telefono = int(telefonox)  # telefono como variable
            resp = 0                            # variable respuesta
            estado = "0"                          # estado para validar posición


            # pregunta si existe el telefono
            cnx = conectar()
            db = cnx.cursor()
            db.execute(
                "select telefono, TIMESTAMPDIFF(MINUTE,fecha,now()) as minutos from sesion where telefono = %s", (telefono,))
            result = db.fetchone()
            if (result is None):

                db = cnx.cursor()
                query = "INSERT INTO sesion (telefono, valor, fecha) values (%s, %s, %s)"
                data = [(telefono, estado, fecha_actual)]
                db.executemany(query, data)
                cnx.commit()
                cerrar(cnx)
            else:
                print("existe sesion")
                minutos = result[1]
                if minutos > 15:
                    estado = "0"
                    resp = 0
                    update_sesion(telefono,estado)


            cnx = conectar()
            db = cnx.cursor()
            db.execute(
            "SELECT telefono, valor FROM sesion WHERE telefono = %s", (telefono,))
            results = db.fetchall()

            if results:
                for result in results:

                    qvalor = result[1]
                    qtelefono = result[0]

                    if qvalor == "0" and resp == 0:
                        body = {"type": "text", "message": "*Taxistas unidos te da la bienvenida* \n" +
                                "''Te ayudare a escoger el servicio que necesitas'' 🚕😎🚕 \n\n"
                                }
                        body.update({"to_number": conversation})
                        send_response(body)

                        body = {
                            "type": "text",
                            "text": "menu bot",
                            "message": "¿Cuál es su nombre? ",
                        }
                        body.update({"to_number": conversation})
                        send_response(body)

                        estado = "0.1"
                        resp = 1
                        update_sesion(telefono,estado)

                        
                    if qvalor == "0.1" and resp == 0:
                        body = {
                                "type": "text",
                                "message": "Hola "+text+", ¿Cual servicio vas a usar?\n\n"+
                                " *1*. Viaje especial \n *2*. Unidad Conocida \n *3*. Unidad Cercana",
                                }
                        body.update({"to_number": conversation})
                        send_response(body)
                        estado = "0.2"
                        resp = 1
                        update_sesion(telefono,estado)
                    
                    #respuestas para viajes especiales
                    if qvalor == "0.2" and resp == 0:       
                        if text == "1":
                                body = {
                                        "type": "text",
                                        "message": "Escogiste *Viaje especial*",
                                        }
                                body.update({"to_number": conversation})
                                send_response(body)

                                body = {
                                        "type": "text",
                                        "message": "Elija tipo unidad \n *1*.Sedan \n *2*.Pickup",
                                        }
                                body.update({"to_number": conversation})
                                send_response(body)
                                estado = "1.0"
                                resp = 1
                                update_sesion(telefono,estado)
                        
                        else:
                        
                            if text == "2":
                                    body = {
                                            "type": "text",
                                            "message": "Escogiste *Unidad Conocida*",
                                            }
                                    body.update({"to_number": conversation})
                                    send_response(body)

                                    body = {
                                            "type": "text",
                                            "message": "Indique el número de unidad:",
                                            }
                                    body.update({"to_number": conversation})
                                    send_response(body)
                                    estado = "2.0"
                                    resp = 1
                                    update_sesion(telefono,estado)
                            else:

                                if text == "3":
                                        body = {
                                                "type": "text",
                                                "message": "Escogiste *Unidad cercana*",
                                                }
                                        body.update({"to_number": conversation})
                                        send_response(body)

                                        body = {
                                                "type": "text",
                                                "message": "Elija tipo unidad \n *1*.Sedan \n *2*.Pickup",
                                                }
                                        body.update({"to_number": conversation})
                                        send_response(body)
                                        estado = "3.0"
                                        resp = 1
                                        update_sesion(telefono,estado)
                                else:
                                    body = {
                                        "type": "text",
                                        "message": "Hola "+text+", ¿Cual servicio vas a usar? \n\n"+
                                        "*1*. Viaje especial \n *2*.Unidad Conocida \n *3*. Unidad Cercana",
                                        }
                                    body.update({"to_number": conversation})
                                    send_response(body)

                    if qvalor == "1.0" and resp == 0:
                        if text == "1":
                            body = {
                                "type": "text",
                                "message": "seleccionó: *Sedan*",
                                }
                            body.update({"to_number": conversation})
                            send_response(body)

                            body = {
                                "type": "text",
                                "message": "Indique el lugar de origen de la carrera:",
                                }
                            body.update({"to_number": conversation})
                            send_response(body)

                            estado = "1.1"
                            resp = 1
                            update_sesion(telefono, estado)
                        else:

                            if text == "2":
                                body = {
                                    "type": "text",
                                    "message": "seleccionó: *Pickup*",
                                    }
                                body.update({"to_number": conversation})
                                send_response(body)

                                body = {
                                    "type": "text",
                                    "message": "Indique el lugar de origen de la carrera:",
                                    }
                                body.update({"to_number": conversation})
                                send_response(body)

                                estado = "1.1"
                                resp = 1
                                update_sesion(telefono, estado)

                            else:
                                body = {
                                    "type": "text",
                                    "message": "Seleccione un tipo de unidad correcta \n\n Elija tipo unidad \n *1*.Sedan \n *2*.Pickup",
                                    }
                                body.update({"to_number": conversation})
                                send_response(body)
                        

                    if qvalor == "1.1" and resp == 0:
                            body = {
                                "type": "text",
                                "message": "Su lugar de origen es: *"+text+"*",
                                }
                            body.update({"to_number": conversation})
                            send_response(body)

                            body = {
                                "type": "text",
                                "message": "Indique el lugar de llegada de la carrera:",
                                }
                            body.update({"to_number": conversation})
                            send_response(body)

                            estado = "1.2"
                            resp = 1
                            update_sesion(telefono, estado)

                    if qvalor == "1.2" and resp == 0:
                            body = {
                                "type": "text",
                                "message": "Su lugar de llegada es: *"+text+"*",
                                }
                            body.update({"to_number": conversation})
                            send_response(body)

                            body = {
                                "type": "text",
                                "message": "Envie su ubicación",
                                }
                            body.update({"to_number": conversation})
                            send_response(body)

                            estado = "9999"
                            resp = 1
                            update_sesion(telefono, estado)
                    
                    
                    if qvalor == "2.0" and resp == 0:
                            body = {
                                    "type": "text",
                                    "message": "seleccionó: *Unidad "+text+"*",
                                    }
                            body.update({"to_number": conversation})
                            send_response(body)

                            body = {
                                    "type": "text",
                                    "message": "Indique el lugar de origen de la carrera:",
                                    }
                            body.update({"to_number": conversation})
                            send_response(body)

                            estado = "2.1"
                            resp = 1
                            update_sesion(telefono, estado)
                    
                    if qvalor == "2.1" and resp == 0:
                            body = {
                                    "type": "text",
                                    "message": "su carrera sera desde: * "+text+"*",
                                    }
                            body.update({"to_number": conversation})
                            send_response(body)

                            body = {
                                    "type": "text",
                                    "message": "Indique el lugar de destino de la carrera:",
                                    }
                            body.update({"to_number": conversation})
                            send_response(body)

                            estado = "2.2"
                            resp = 1
                            update_sesion(telefono, estado)
                    
                    
                    if qvalor == "2.2" and resp == 0:
                            body = {
                                    "type": "text",
                                    "message": "su carrera sera Hasta: * "+text+"*",
                                    }
                            body.update({"to_number": conversation})
                            send_response(body)

                            body = {
                                    "type": "text",
                                    "message": "Envienos su ubicación",
                                    }
                            body.update({"to_number": conversation})
                            send_response(body)

                            estado = "9999"
                            resp = 1
                            update_sesion(telefono, estado)
                    
                        

                    if qvalor == "3.0" and resp == 0:
                        if text == "1":
                            body = {
                                "type": "text",
                                "message": "seleccionó: *Sedan*",
                                }
                            body.update({"to_number": conversation})
                            send_response(body)

                            body = {
                                "type": "text",
                                "message": "Indique el lugar de origen de la carrera:",
                                }
                            body.update({"to_number": conversation})
                            send_response(body)

                            estado = "3.1"
                            resp = 1
                            update_sesion(telefono, estado)
                        else:

                            if text == "2":
                                body = {
                                    "type": "text",
                                    "message": "seleccionó: *Pickup*",
                                    }
                                body.update({"to_number": conversation})
                                send_response(body)

                                body = {
                                    "type": "text",
                                    "message": "Indique el lugar de origen de la carrera:",
                                    }
                                body.update({"to_number": conversation})
                                send_response(body)

                                estado = "3.1"
                                resp = 1
                                update_sesion(telefono, estado)

                            else:
                                body = {
                                    "type": "text",
                                    "message": "Seleccione un tipo de unidad correcta \n\n Elija tipo unidad \n *1*.Sedan \n *2*.Pickup",
                                    }
                                body.update({"to_number": conversation})
                                send_response(body)
                        

                    if qvalor == "3.1" and resp == 0:
                            body = {
                                "type": "text",
                                "message": "Su lugar de origen es: *"+text+"*",
                                }
                            body.update({"to_number": conversation})
                            send_response(body)

                            body = {
                                "type": "text",
                                "message": "Indique el lugar de llegada de la carrera:",
                                }
                            body.update({"to_number": conversation})
                            send_response(body)

                            estado = "3.2"
                            resp = 1
                            update_sesion(telefono, estado)

                    if qvalor == "3.2" and resp == 0:
                            body = {
                                "type": "text",
                                "message": "Su lugar de llegada es: *"+text+"*",
                                }
                            body.update({"to_number": conversation})
                            send_response(body)

                            body = {
                                "type": "location",
                                "message": "Envie su ubicación",
                                }
                            body.update({"to_number": conversation})
                            send_response(body)

                            estado = "9999"
                            resp = 1
                            update_sesion(telefono, estado)
                    if qvalor == "9999" and resp == 0:
                            body = {
                            "type": "text",
                            "message": "Pronto sera atendido. \n Gracias por preferirnos",
                            }
                            body.update({"to_number": conversation})
                            send_response(body)

                            estado = "10000"
                            resp = 1
                            update_sesion(telefono, estado)
                    
                    


            else:
                print("No se encontraron resultados.")

            cerrar(cnx)
    else:
        print("Unknow Type:", wttype,  file=sys.stdout, flush=True)
    return jsonify({"success": True}), 200


def setup_webhook():
    if PRODUCT_ID == "" or PHONE_ID == "" or API_TOKEN == "":
        print(
            "You need to change PRODUCT_ID, PHONE_ID and API_TOKEN values in app.py file.", file=sys.stdout, flush=True
        )
        return
    public_url = ngrok.connect(9000)
    url = INSTANCE_URL + "/" + PRODUCT_ID + "/setWebhook"
    print("url", url, file=sys.stdout, flush=True)
    headers = {
        "Content-Type": "application/json",
        "x-maytapi-key": API_TOKEN,
    }
    body = {"webhook": public_url.public_url + "/webhook"}
    response = requests.post(url, json=body, headers=headers)
    print("webhook ", response.json())

def update_sesion(telefono, estado):
    cnx = conectar()
    db = cnx.cursor()
    query = """UPDATE sesion SET valor = %s, fecha = now() WHERE telefono = %s;"""

    try:
        db.execute(query, (estado, telefono))
        cnx.commit()
    except Exception as err:
        print(err)

def count_send():
    cnx = conectar()
    db = cnx.cursor()

    db.execute("select * from count_send")
    result = db.fetchall()
    if result:
        for results in result:
            conteo = results[0]
            if conteo >= 2800:
                body = {
                "type": "text",
                "message": "Limite de mensjaes",
                }
                body.update({"to_number": "50764333125@c.us"})
                send_response(body)
                print("se alcanzo el limite")
            
            else:
                disponible = 3000 - conteo
                print(disponible)
                db.execute("UPDATE count_send SET mensajes = mensajes + 1")
                cnx.commit()
                cerrar(cnx)


    
    

# Do not use this method in your production environment
setup_webhook()

