from server_work import ServerWork

class HaltWork(ServerWork):
    def do(self, message, orig):
        return False