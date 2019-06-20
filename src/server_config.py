import socket
import threading

class ServerSignature():
    """Classe de assinatura, descreve assinatura de recebimento e assinatura de envio.
    Opcionalmetne é possível informar o parâmetro sender, que faz com que a inicialiação seja feita
    como se a porta fosse a de envio, não á de recebimento"""
    def __init__(self, ip, port, sender=False):
        if sender:
            self.receive = (ip, port - 1)
            self.send = (ip, port)
            return
        self.receive = (ip, port)
        self.send = (ip, port + 1)

class ServerConfig():
    """Classe de configuração de servidor.
    
    A classe disponibiliza:
        - Interface de envio para (necessário informar de quem parte a mensagem).
        - Interface de recebimento.
        - Encode
        - Decode"""

    def __init__(self, signature, charset='utf-8'):
        """Método de inicialização, recebe a assinatura (ServerSignature) e opcionalmente um charset (default utf-8)."""
        self.signature = signature
        self.charset = charset

    def _client_socket(self, orig):
        """método interno para inicialização de socket de envio."""
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print('iniciado socket de envio em: ' + str(orig.send))
        udp_socket.bind(('', orig.send[1]))
        return udp_socket

    def _server_socket(self):
        """método interno para inicialização de socket de recebimento."""
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(self.signature.receive)
        print('iniciado socket de recebimento em: ' + str(self.signature.receive))
        return udp_socket
    
    def _loop(self, call_back):
        """método interno para manutenção de loop de recebimento de mensagens."""
        with self._server_socket() as udp_socket:
            while True:
                print('esperando mensagem em: ' + str(self.signature.receive))
                msg = udp_socket.recvfrom(1024)
                print('recebida mensagem (' + str(msg) + ') em: ' + str(self.signature.receive))
                (bts_msg, orig) = msg
                if not call_back(bts_msg, orig):
                    print('callback retornou falso, halt')
                    break

    def _get_thread(self, target, args):
        """método interno para inicialização de thread para uso genérico."""
        thr = threading.Thread(target=target,args=args)
        return thr
    
    def server_thread(self, call_back):
        """Inicializa um servidor UDP, recebendo mensagens e processando elas chamando o callback.
        Se o callback retornar um valor falso, é executado o halt da thread inicializada.
        Retorna a thread de execução para manipulação."""
        args = [call_back]
        thr = self._get_thread(self._loop, args)
        return thr

    def encode(self, input_str, charset=None):
        """Recebe uma string, realiza o encode da mesma para o charset:
            - Recebido por parâmetro (opcional). 
            - Configurado para a instância.
            - Default utf-8."""
        encoding = charset or self.charset or 'utf-8'
        input_bts = input_str.encode(encoding=encoding, errors='strict')
        return input_bts

    def decode(self, input_bts, charset=None):
        """Recebe um byte string, realiza o decode da mesma para o charset:
            - Recebido por parâmetro (opcional). 
            - Configurado para a instância.
            - Default utf-8."""
        encoding = charset or self.charset or 'utf-8'
        input_str = input_bts.decode(encoding=encoding, errors='strict')
        return input_str

    def send(self, orig, message):
        """Realiza um envio UDP/IP para a assinatura configurada.
        Necessário informar a origem para que seja realizado o bind do mesmo no envio.
        É esperado que a mensagem seja uma string"""
        with self._client_socket(orig) as udp:
            udp.sendto (self.encode(message), self.signature.receive)
            print('enviada mensagem (' + str(message) + ') para: ' + str(self.signature.receive))
