from server_config import ServerConfig
from default_server_work import DefaultServerWork
from set_server_list_work import SetServerListWork
from halt_work import HaltWork

class Server():
    def __init__(self, signature, start_server=None):
        self.signature = signature
        self.server_config = ServerConfig(signature)

        self._server_list = []

        self._work_stack = []
        self._default_work = DefaultServerWork(self)

        thr = self.server_config.server_thread(self._msg_recv)
        thr.start()
        self.server_thread = thr
        
        if start_server:
            self._append_work(SetServerListWork(self))
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
        self._append_work(HaltWork(self))
        self.server_config.send(self.signature, 'halt')