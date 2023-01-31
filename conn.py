import mysql.connector

def conectar():
    cnx = mysql.connector.connect(user='root', password='', host='XXXXXX', database='wbot')
    return cnx


def cerrar(cnx):
    cnx.close()
