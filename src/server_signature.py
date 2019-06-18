class ServerSignature():
    def __init__(self, ip, port):
        self.receive = (ip, port)
        self.send = (ip, port + 1)