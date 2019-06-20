from server_config import ServerConfig
from server_config import ServerSignature
from external_server import ExternalServer

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
        
        self.expecting = False
        if start_server:
            self.expecting = 'serverList'
            start_server.get_server_list(self.signature)

    def _append_server(self, server):
        """método interno para injeção de novos servidores na lista de servidores conhecidos."""
        self._server_list.add(server)

    def _next_server(self):
        """método interno para obténção do próximo servidor conhecido."""
        sort_method = lambda se: hash(se.server_config)
        sorted_list = sorted(self._server_list, key=sort_method)
        for server in sorted_list:
            if hash(server.server_config) > hash(self.server_config):
                return server
        return sorted_list[0]

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
        conf.send(self.signature, str(self.server_array()))
        return True

    def _msg_recv(self, bts_msg, orig_tup):
        """Método interno para recebimento de mensagem, enviado como callback para a thread separada.
        Recebe o byte string da mensagem e a tupla IP porta de quem a mensagem foi recebida.
        Retornar valores valorados como falso implica em para a thread de recebimento de mensagens"""

        str_msg = self.server_config.decode(bts_msg)

        if self.expecting == 'serverList':
            self.expecting = False
            self._recv_server_list(str_msg)

        sig = ServerSignature(*orig_tup, True)
        conf = ServerConfig(sig)

        if str_msg == 'get_server_list':
            return self._recv_server_list_request(conf)
    
        if str_msg == 'hello':
            return self._recv_hello(conf)

        if str_msg == 'halt':
            return False

    def halt(self):
        """Método para finalizar a execução do socket de recebimento."""
        self.server_config.send(self.signature, 'halt')

    def server_array(self):
        """interface para obtenção da lista de tuplas IP e porta de recebimento dos servidores conhecidos."""
        server_array = []
        for serv in self._server_list:
            server_array.append(serv.server_config.signature.receive)

        server_array.append(self.signature.receive)

        return server_array
