from server_config import ServerConfig
from server_config import ServerSignature
from external_server import ExternalServer
from token_ring import Token

import time
import threading

class Server():
    def __init__(self, signature, start_server=None):
        """Inicialização do servidor, necessita o recebimento da assinatura do servidor (instancia de ServerSignature).
        Opcionalmente também pode ser receber uma instancia de external server para se conectar a rede da qual ele faz parte.
        Não sendo informado um servidor, será inicializado uma nova rede."""
        self.signature = signature
        self.server_config = ServerConfig(signature)

        self._server_list = set()

        thr = self.server_config.server_thread(self._msg_recv)
        thr.start()
        self.server_thread = thr

        self.token_thread_list = []
        
        self.expecting = False
        if start_server:
            self.expecting = 'serverList'
            start_server.get_server_list(self.signature)

    def _append_server(self, server):
        """método interno para injeção de novos servidores na lista de servidores conhecidos."""
        self._server_list.add(server)

    def _next_server(self, ignore=[]):
        """método interno para obténção do próximo servidor conhecido.
        Opcionalmente é possível enviar uma lista de ignore, para não enviar
        para os servidores que não responderam anteriormente.  Se não houver
        servidor com hash maior que o da instancia e que não esteja na lista de
        ignore, é buscado o menor hash que não está na lista de ignore.  Se não
        houver servidor algum, é retornada False"""
        sort_method = lambda se: hash(se.server_config)
        sorted_list = sorted(self._server_list, key=sort_method)
        for server in sorted_list:
            if server in ignore:
                continue
            if hash(server.server_config) > hash(self.server_config):
                return server
        for server in sorted_list:
            if server in ignore:
                continue
            return sorted_list[0]
        return ExternalServer(self.server_config)

    def _say_hello(self):
        """método interno para disparo das mensagens de aceno para os servidores conhecidos."""
        for server in self._server_list:
            server.say_hello(self.signature)

    def _recv_server_list(self, str_msg):
        """Método interno para recebimento da listagem de servidores.
        É esperado receber uma string que valorada seja um iterável de tuplas de IP porta.
        Ex: "[(\\"localhost\\", 5050)]"."""
        # TODO: utilizar algum padrão melhor que evaluation
        tuple_list = eval(str_msg)


        for (ip, port) in tuple_list:
            signature = ServerSignature(ip, port)
            conf = ServerConfig(signature)
            ext_server = ExternalServer(conf)
            self._append_server(ext_server)

        self._say_hello()
        return True

    def _recv_hello(self, conf):
        """Método interno para recebimento de aceno de um servidor."""
        ext_server = ExternalServer(conf)
        self._append_server(ext_server)
        return True

    def _recv_server_list_request(self, conf):
        # TODO: docstring
        conf.send(self.signature, str(self.server_array()))
        return True
    
    def _conclude_token(self, token):
        # TODO: docstring
        # TODO: implement
        print('confirmado_token')
        print(repr(token))
        return True
    
    def _request_url(self, url):
        # TODO: docstring
        # TODO: implement
        return 404
    
    def _proccess_token(self, token):
        # TODO: docstring

        url = token.url
        response = self._request_url(url)
        
        token.append_server(str(self.signature), str(response))
        return token

    def _send_token(self, token):
        print(str(self.signature) + str(token))
        ignore = []
        while True:
            server = self._next_server(ignore)
            print(1)
            if not server:
                print(2)
                return self._conclude_token(token)
            self.expecting = 'confirm_token'
            server.send_token(self.signature, token)
            print()
            print(str(server.server_config.signature) + ' - ' + str(self.signature))
            print(3)
            for i in range(100000):
                time.sleep(2/100000) # TODO: Add timeout configuration
                if self.expecting != 'confirm_token':
                    break
            print(4)
            if self.expecting == 'confirm_token':
                print(5)
                ignore.append(server)
                # TODO: Add server not responding to token
                continue
            print(6)
            break
        print(7)

    def _recv_token(self, conf, token):
        # TODO: docstring
        
        conf.send(self.signature, 'confirm_token')

        print(10)
        if str(self.signature) in token.server_stack:
            return self._conclude_token(token)

        print(11)
        new_token = self._proccess_token(token)
        print(12)
        thr = threading.Thread(target=self._send_token,args=[new_token])
        thr.start()
        print(13)
        self.token_thread_list.append(thr)
        print(14)
        return True

    def _recv_confirm_token(self):
        self.expecting = False
        return True

    def _msg_recv(self, bts_msg, orig_tup):
        """Método interno para recebimento de mensagem, enviado como callback para a thread separada.
        Recebe o byte string da mensagem e a tupla IP porta de quem a mensagem foi recebida.
        Retornar valores valorados como falso implica em para a thread de recebimento de mensagens"""

        str_msg = self.server_config.decode(bts_msg)

        sig = ServerSignature(*orig_tup, True)
        conf = ServerConfig(sig)

        if str_msg == 'get_server_list':
            return self._recv_server_list_request(conf)
    
        if str_msg == 'hello':
            return self._recv_hello(conf)

        if str_msg == 'halt':
            return False

        if str_msg == 'confirm_token':
            print(8)
            if self.expecting == 'confirm_token':
                return self._recv_confirm_token()

        if self.expecting == 'serverList':
            self.expecting = False
            return self._recv_server_list(str_msg)

        token = eval(str_msg)
        if isinstance(token, Token):
            return self._recv_token(conf, token)

    def send_token(self, url):
        # TODO: docstring
        token = Token(url)
        token = self._proccess_token(token)
        return self._send_token(token)

    def halt(self):
        """Método para finalizar a execução do socket de recebimento."""
        self.server_config.send(self.signature, 'halt')
        # TODO: Validar threads (set timeout zero)

    def server_array(self):
        """interface para obtenção da lista de tuplas IP e porta de recebimento dos servidores conhecidos."""
        server_array = []
        for serv in self._server_list:
            server_array.append(serv.server_config.signature.receive)

        server_array.append(self.signature.receive)

        return server_array
