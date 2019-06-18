class ExternalServer():
    def __init__(self, server_config):
        self.server_config = server_config

    def get_server_list(self, orig):
        """Requisita o servidor externo dos servidores por ele conhecidos e retorna a lista"""
        self.server_config.send(orig, 'get_server_list')

    def say_hello(self, orig):
        self.server_config.send(orig, 'hello')