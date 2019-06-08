import socket
import threading
import sys
import json
import mysql.connector

class Server():
    def __init__(self):
        #CREACION DE SOCKET
        self.socket = socket.socket()
        self.socket.bind(("localhost", 9993))
        self.socket.listen(10)
        self.socket.setblocking(False)

        #ARRAY DE CLIENTES
        self.clientes = []
        self.clientesEnLinea = []

        #CONEXION A LA BASE DE DATOS
        self.conexionBD = mysql.connector.connect(user="root", password="1112771855", host="localhost", database="chat")
        self.cursor = self.conexionBD.cursor()

        #CREACION DE HILOS
        self.aceptarConexion = threading.Thread(target=self.aceptarConexiones)
        self.aceptarConexion.daemon = True
        self.aceptarConexion.start()

        self.procesarConexion = threading.Thread(target=self.procesarConexiones)
        self.procesarConexion.daemon = True
        self.procesarConexion.start()

        self.mensajeCliente = threading.Thread(target=self.mensajeClientes)
        self.mensajeCliente.daemon = True
        self.mensajeCliente.start()

        while True:
            try:
                self.opcion = input(" >> ")
                if self.opcion == "salir":
                    self.socket.close()
                    sys.exit()
            except:
                self.socket.close()
                sys.exit()

    def mensajeTodos(self, mensaje, cliente):
        for c in self.clientes:
            try:
                if c != cliente:
                    c.send(mensaje)
            except:
                self.clientes.remove(c)

    def aceptarConexiones(self):
        while True:
            try:
                self.conexion, self.direccion = self.socket.accept()
                self.conexion.setblocking(False)
            except:
                pass

    def mensajeClientes(self):
        while True:
            try:
                self.msj = json.loads(self.conexion.recv(1024).decode())
                if isinstance(self.msj, list):
                    if len(self.msj) == 2:
                        self.conexion.send(self.validarLogin().encode())
                    if len(self.msj) == 3:
                        self.conexion.send(self.registrarUsuario().encode())
                else:
                    if self.msj == 1:
                        self.conexion.send(json.dumps(self.clientesEnLinea).encode())

            except:
                pass

    def procesarConexiones(self):
        print("Procesar conexión")
        while True:
            if len(self.clientes) > 0:
                for c in self.clientes:
                    try:
                        self.datos = c.recv(1024).decode()
                        if self.datos:
                            print(self.datos)
                            self.mensajeTodos(self.datos, c)
                    except:
                        pass

    def validarLogin(self):
        self.consulta = "SELECT id, nombre FROM usuarios WHERE correo = %s AND contrasena = %s"
        self.cursor.execute(self.consulta, (self.msj[0], self.msj[1]))
        self.respuesta = self.cursor.fetchone()

        if self.respuesta != None:
            self.clienteEnLinea = [self.respuesta[0], self.respuesta[1]]
            self.clientesEnLinea.append(self.clienteEnLinea)


            #self.cliente = [self.conexion, self.respuesta[0], self.respuesta[1]]
            #self.clientes.append(self.cliente)
            self.clientes.append(self.conexion)
            self.respuesta = '1'
        else:
            self.respuesta = '0'

        return self.respuesta

    def registrarUsuario(self):
        self.consulta = "INSERT INTO usuarios(nombre, correo, contrasena) VALUES(%s, %s, %s)"
        self.cursor.execute(self.consulta, (self.msj[0], self.msj[1], self.msj[2]))
        self.conexionBD.commit()

        if self.cursor.rowcount != 0:
            self.resultado = "1"
        else:
            self.resultado = "0"

        return self.resultado

server = Server()