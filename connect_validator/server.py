from server_config import ServerConfig
from server_config import ServerSignature
from external_server import ExternalServer
from token_ring import Token

import time
import threading

import requests # TODO: manual de isntalalção (pip install requests)

class Server():
    def __init__(self, signature, start_server=None, timeout_limit = 2, debug_mode = False):
        """Inicialização do servidor, necessita o recebimento da assinatura do
        servidor (instancia de ServerSignature).  Opcionalmente também pode ser
        receber uma instancia de external server para se conectar a rede da
        qual ele faz parte.  Não sendo informado um servidor, será inicializado
        uma nova rede.  Outro parâmetro opcinal é o timeout_limit, default 2,
        que é a quantidade em segundos que o servidor deve esperar uma
        requisição antes de considerar que o servidor para quem foi enviada não
        está no ar."""

        self.signature = signature
        self.server_config = ServerConfig(signature, debug_mode = debug_mode)

        self.timeout_limit = timeout_limit

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
        """método interno para injeção de novos servidores na lista de
        servidores conhecidos."""
        if (self.signature == server.server_config.signature):
            return
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
        # TODO: docstring
        exteral_server_list = eval(str_msg)
        for server in exteral_server_list:
            self._append_server(server)

        self._say_hello()
        return True

    def _recv_hello(self, conf):
        """Método interno para recebimento de aceno de um servidor."""
        ext_server = ExternalServer(conf)
        self._append_server(ext_server)
        return True

    def _recv_server_list_request(self, conf):
        """Envia para o solicitante a lista dos servidores conhecidos"""
        conf.send(self.signature, repr(self.server_array()))
        return True
    
    def _conclude_token(self, token):
        # TODO: docstring
        # TODO: implement
        print('confirmado_token')
        print(repr(token))
        return True
    
    def _request_url(self, url):
        """Realiza a requisição para a URL e retona:
            - O código de status (200, 400, 404, 500).
            - Error, invalid url (se a url não for válida)"""
        try:
            response = requests.get(url)
            return response.status_code
        except:
            return "Error, invalid url"
    
    def _proccess_token(self, token):
        """Realiza o processamento do token, utilizando o método _request_url
        para verificar o acesso local e atualiza o token"""

        url = token.url
        response = self._request_url(url)
        
        token.append_server(str(self.signature), str(response))

    def _wait(self, validation=None, limit=None):
        """Implementação local para sleep. É possível informar o campo
        validation, como um método para ser chamado a fim de parar o sleep se
        retornar true. É tamém possível informar um limite em segundo, como
        default será o limite informado na instância."""
        if not limit:
            limit = self.timeout_limit
        if not validation:
            validation = lambda: False
        for step in range(100000):
            time.sleep(self.timeout_limit/100000)
            if validation():
                break
    
    def _send_token(self, token):
        """Realiza o envio do token para o proximo servidor, validando a
        resposta e buscando os proximos caso um pare de responder. É realizada
        a espera pelo tempo de timeout configurado."""

        ignore = []
        for server in self._server_list:
            if server.server_config.signature in token.server_stack:
                ignore.append(server)
        while True:
            server = self._next_server(ignore)
            if not server:
                return self._conclude_token(token)
            self.expecting = 'confirm_token'
            server.send_token(self.signature, token)
            self._wait(lambda: self.expecting != 'confirm_token' or not self.timeout_limit)
            if self.expecting == 'confirm_token':
                ignore.append(server)
                token.append_server(str(server.server_config.signature), 'Error, server not responding')
                continue
            break

    def _recv_token(self, conf, token):
        """Tratamento do recebimento do token. Envia a confirmação para a
        origem da mensagem, valida se não está na stack do token. Se já
        estiver, é concluido o token.  Se não estiver, é realizada a
        verificação localmente, e o token é encaminhado para o proximo.
        Esse processo é realizado com uso de uma thread separada, para
        desocupar o socket de recebimento, e possibilitar receber a
        confiramação de que o proximo servidor recebeu o token"""

        conf.send(self.signature, 'confirm_token')

        if str(self.signature) in token.server_stack:
            return self._conclude_token(token)

        self._proccess_token(token)
        thr = threading.Thread(target=self._send_token,args=[token])
        thr.start()
        self.token_thread_list.append(thr)
        return True

    def _recv_confirm_token(self):
        """Tratamento da confirmação de recebimendo do token. Apenas limpa o
        campo de respostas esperadas."""
        self.expecting = False
        return True

    def _msg_recv(self, bts_msg, orig_tup):
        """Método interno para recebimento de mensagem, enviado como callback
        para a thread separada.  Recebe o byte string da mensagem e a tupla IP
        porta de quem a mensagem foi recebida.  Retornar valores valorados como
        falso implica em para a thread de recebimento de mensagens. Trata mensagens:
            - get_server_list
            - hello
            - halt
            - confirm_token (se estiver aguardado a confirmação)
            - server_list (se estiver aguardado a lista)
            - token (se o valor não foi processado em nenhuma opção anterior e
              a evaluação da mensagem é um token, o token é processado.)"""

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
            if self.expecting == 'confirm_token':
                return self._recv_confirm_token()

        if self.expecting == 'serverList':
            try:
                result = self._recv_server_list(str_msg)
                self.expecting = False
                return result
            except:
                pass

        try:
            token = eval(str_msg)
            if isinstance(token, Token):
                return self._recv_token(conf, token)
        except:
            return True

    def send_token(self, url):
        """Iinicailiza um token a partir da URL recebida, valida o mesmo
        localmente e envia para o próximo servidor"""
        token = Token(url)
        self._proccess_token(token)
        return self._send_token(token)

    def halt(self):
        """Método para finalizar a execução do socket de recebimento."""
        self.server_config.send(self.signature, 'halt')
        self.timeout_limit = 0

    def server_array(self):
        """interface para obtenção da lista de tuplas IP e porta de recebimento
        dos servidores conhecidos."""
        external_self = ExternalServer(self.server_config)
        return self._server_list | {external_self}
