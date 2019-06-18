from server_signature import ServerSignature
from server_config import ServerConfig
from external_server import ExternalServer
from server_work import ServerWork

class DefaultServerWork(ServerWork):
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
