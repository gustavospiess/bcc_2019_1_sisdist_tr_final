import socket
import threading

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
                    break

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