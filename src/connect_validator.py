import socket
import threading
from abc import ABC, abstractmethod #abc é Abstract Base Class...
from external_server import ExternalServer
from server_config import ServerConfig
from server_signature import ServerSignature
from work import Work
from server import Server
import time

ip = ''

def main():

    global ip
    print('Digite o ip: ', end="")
    ip = input()

    a_sig = ServerSignature(ip, 17692)
    a_server = Server(a_sig)

    a_s_config = ServerConfig(a_sig)
    a_ext_server = ExternalServer(a_s_config)

    b_sig = ServerSignature(ip, 17692+5)
    b_server = Server(b_sig, a_ext_server)

    time.sleep(1)

    print(a_server.server_array())
    print(b_server.server_array())

    a_server.halt()
    b_server.halt()

if __name__ == '__main__':
    main()
