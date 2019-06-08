import socket
import threading
import sys
import json
import os
import crypt
import getpass

class Client():

    sock = socket.socket()
    sock.connect(("localhost", 9993))

    def __init__(self):
        self.borrarPantalla()
        print(self.imprimirMenu())
        self.opcion = input(">> ")
        self.opciones()

    def mensajeServer(self):
        while True:
            try:
                """self.datos = self.sock.recv(1024)
                if self.datos:
                    print(self.datos.decode())"""
                self.datos = json.loads(self.sock.recv(1024).decode())
                if isinstance(self.datos, list):
                    self.borrarPantalla()
                    print("Clientes en linea:\n")
                    for c in self.datos:
                        print("* id:",c[0],c[1],"\n")

                    print(self.imprimirMenuUsuario())
                else:
                    if self.datos:
                        print(self.datos)
            except:
                pass

    def enviarMensaje(self, mensaje):
        self.sock.send(mensaje.encode())

    def imprimirMenu(self):
        self.menu = "\n..:: Menu ::...\n\n" \
                    "1) Iniciar sesion.\n" \
                    "2) Registrar usuarios.\n" \
                    "0) Salir.\n"

        return self.menu

    def imprimirMenuUsuario(self):
        self.menuUsuario = "1) Lista de usuarios conectados.\n" \
                           "2) Chat grupal.\n" \
                           "3) Chat individual.\n" \
                           "0) Cerrar sesion.\n"

        return self.menuUsuario

    def opciones(self):
        if self.opcion == "1":
            self.borrarPantalla()
            self.iniciarSesion()
        if self.opcion == "2":
            self.borrarPantalla()
            self.registrarUsuario()

    def borrarPantalla(self):
        if os.name == ("ce", "nt", "dos"):
            os.system("cls")
        else:
            os.system("clear")

    def iniciarSesion(self):
        self.login = []

        self.login.append(input("Correo: >> "))
        self.login.append(crypt.crypt(getpass.getpass("Contrasena: >> "), 'salt'))

        self.sock.send(json.dumps(self.login).encode())
        self.respuesta = self.sock.recv(1024).decode()

        if self.respuesta == '0':
            self.borrarPantalla()
            print("Usuario y/o contrasena incorrecta.")
        else:
            self.borrarPantalla()
            print("\nBienvenido.\n")
            print(self.imprimirMenuUsuario())

            self.mensaje = input(">> ")

            if self.mensaje == "0":
                self.borrarPantalla()
                print("Hasta pronto.\n")
                self.sock.close()
                sys.exit()

            if self.mensaje == "1":
                self.enviarMensaje("1")



            # CREACION DE HILO
            self.msgServer = threading.Thread(target=self.mensajeServer)
            self.msgServer.daemon = True
            self.msgServer.start()

            while True:
                self.mensaje = input(">> ")
                if self.mensaje != "salir":
                    self.enviarMensaje(self.mensaje)

                else:
                    self.sock.close()
                    sys.exit()

    def registrarUsuario(self):
        self.datos = []

        self.datos.append(input("Nombre: >> "))
        self.datos.append(input("Correo: >> "))
        self.datos.append(crypt.crypt(getpass.getpass("Contrasena: >> "), 'salt'))

        self.sock.send(json.dumps(self.datos).encode())
        self.respuesta = self.sock.recv(1024).decode()

        if self.respuesta == "1":
            self.borrarPantalla()
            print("Usuario registrado correctamente.")

        else:
            self.borrarPantalla()
            print("Error al intentar registrar el usuario.")

        print(self.imprimirMenu())
        self.opcion = input(">> ")
        self.opciones()

client = Client()