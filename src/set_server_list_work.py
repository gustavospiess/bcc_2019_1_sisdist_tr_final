from server_signature import ServerSignature
from server_config import ServerConfig
from external_server import ExternalServer
from server_work import ServerWork

class SetServerListWork(ServerWork):
    def do(self, message, orig):
        str_msg = self.server.server_config.decode(message)
        # TODO: utilizar algum padrão melhor que evaluation
        tuple_list = eval(str_msg)
        for (ip, port) in tuple_list:
            sig = ServerSignature(ip, port)
            server_config = ServerConfig(sig)
            ext_server = ExternalServer(server_config)
            self.server.append_server(ext_server)
        self.server.say_hello()
        return True
