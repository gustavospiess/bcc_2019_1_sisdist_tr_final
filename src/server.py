from server_config import ServerConfig
from server_config import ServerSignature
from external_server import ExternalServer

class Server():
    def __init__(self, signature, start_server=None):
        self.signature = signature
        self.server_config = ServerConfig(signature)

        self._server_list = []

        thr = self.server_config.server_thread(self._msg_recv)
        thr.start()
        self.server_thread = thr
        
        self.expecting = False
        if start_server:
            self.expecting = 'serverList'
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

    def _msg_recv(self, msg):

        (bts_msg, orig) = msg

        str_msg = self.server_config.decode(bts_msg) #TODO break in method call
        sig = ServerSignature(orig[0], orig[1] - 1)
        conf = ServerConfig(sig)

        if self.expecting == 'serverList': # TODO: Separa em métodos
            self.expecting = False

            # TODO: utilizar algum padrão melhor que evaluation
            tuple_list = eval(str_msg)

            for (ip, port) in tuple_list:
                server_sig = ServerSignature(ip, port) # TODO: rename
                server_config = ServerConfig(server_sig) # TODO: rename
                ext_server = ExternalServer(server_config)
                self.append_server(ext_server)

            self.say_hello()
            return True

        if str_msg == 'get_server_list':
            conf.send(self.signature, str(self.server_array()))
            return True
    
        if str_msg == 'hello':
            ext_server = ExternalServer(conf)
            self.append_server(ext_server)
            return True

        if str_msg == 'halt':
            return False

    def halt(self):
        self.server_config.send(self.signature, 'halt')
