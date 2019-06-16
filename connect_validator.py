import socket
import threading
from abc import ABC, abstractmethod #abc é Abstract Base Class...

import time

class ServerSignature():
    def __init__(self, ip, port):
        self.receive = (ip, port)
        self.send = (ip, port + 1)

class ServerConfig():
    def __init__(self, dest_sig, charset='utf-8'):
        self.signature = dest_sig
        self.charset = charset

    def _client_socket(self, orig):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(('', orig.send[1]))
        print('iniciado socket de envio em: ' + str(orig.send))
        return udp_socket

    def _server_socket(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(self.signature.receive)
        print('iniciado socket de recebimento em: ' + str(self.signature.receive))
        return udp_socket
    
    @staticmethod
    def _loop(server_config, call_back):
        with server_config._server_socket() as udp_socket:
            while True:
                print('esperando mensagem em: ' + str(server_config.signature.receive))
                msg = udp_socket.recvfrom(1024)
                print('recebida mensagm (' + str(msg) + ') em: ' + str(server_config.signature.receive))
                if not call_back(msg):
                    print('callback retornou falso, halt')
                    break;

    def _get_thread(self, target, args):
        thr = threading.Thread(target=target,args=args)
        return thr
    
    def server_thread(self, call_back):
        args = (self, call_back)
        thr = self._get_thread(self._loop, args)
        return thr

    def encode(self, input_str, charset=None):
        encoding = charset or self.charset or 'utf-8'
        input_bts = input_str.encode(encoding=encoding, errors='strict')
        return input_bts

    def decode(self, input_bts, charset=None):
        encoding = charset or self.charset or 'utf-8'
        input_str = input_bts.decode(encoding=encoding, errors='strict')
        return input_str

    def send(self, orig, message):
        with self._client_socket(orig) as udp:
            udp.sendto (self.encode(message), self.signature.receive)
            print('enviada mensagem (' + str(message) + ') para: ' + str(self.signature.receive))

class ExternalServer():
    def __init__(self, server_config):
        self.server_config = server_config

    def get_server_list(self, orig):
        """Requisita o servidor externo dos servidores por ele conhecidos e retorna a lista"""
        self.server_config.send(orig, 'get_server_list')

    def say_hello(self, orig):
        self.server_config.send(orig, 'hello')

class Work(ABC):
    @abstractmethod
    def do(self, message, orig):
        pass

    def __call__(self, args):
        (input_bts, orig) = args
        return self.do(input_bts, orig)

class ServerWork(Work):
    def __init__(self, server):
        self.server = server

class set_server_list_work(ServerWork):
    def do(self, message, orig):
        str_msg = self.server.server_config.decode(message)
        tuple_list = eval(str_msg) #TODO: utilizar algum padrão melhor que evaluation
        for (ip, port) in tuple_list:
            sig = ServerSignature(ip, port)
            server_config = ServerConfig(sig)
            ext_server = ExternalServer(server_config)
            self.server.append_server(ext_server)
        self.server.say_hello()
        return True

class default_server_work(ServerWork):
    def do(self, message, orig):
        str_msg = self.server.server_config.decode(message)

        sig = ServerSignature(orig[0], orig[1] - 1)
        conf = ServerConfig(sig)

        if str_msg == 'get_server_list':
            conf.send(self.server.signature, str(self.server.server_array()))
            return True

        if str_msg == 'hello':
            ext_server = ExternalServer(conf)
            self.server.append_server(ext_server)
            return True

class halt_work(ServerWork):
    def do(self, message, orig):
        return False


class Server():
    def __init__(self, signature, start_server=None):
        self.signature = signature
        self.server_config = ServerConfig(signature)

        self._server_list = []

        self._work_stack = []
        self._default_work = default_server_work(self)

        thr = self.server_config.server_thread(self._msg_recv)
        thr.start()
        self.server_thread = thr
        
        if start_server:
            self._append_work(set_server_list_work(self))
            start_server.get_server_list(self.signature)

    def append_server(self, server):
        self._server_list.append(server)

    def say_hello(self):
        for server in self._server_list:
            server.say_hello(self.signature)

    def server_array(self):
        server_array = []
        for serv in self._server_list:
            server_array.append(serv.server_config.signature.receive)

        server_array.append(self.signature.receive)

        return server_array

    def _append_work(self, work):
        self._work_stack.append(work)

    def _get_work(self):
        if self._work_stack:
            return self._work_stack.pop()
        return self._default_work

    def _msg_recv(self, msg):
        work = self._get_work()
        return work(msg)
    
    def halt(self):
        self._append_work(halt_work(self))
        self.server_config.send(self.signature, 'halt')

def main():

    a_sig = ServerSignature('192.168.15.6', 17692)
    a_server = Server(a_sig)

    a_s_config = ServerConfig(a_sig)
    a_ext_server = ExternalServer(a_s_config)

    b_sig = ServerSignature('192.168.15.6', 17692+5)
    b_server = Server(b_sig, a_ext_server)

    time.sleep(1)

    print(a_server.server_array())
    print(b_server.server_array())

    a_server.halt()
    b_server.halt()

if __name__ == '__main__':
    main()
