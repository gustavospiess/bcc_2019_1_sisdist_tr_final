class ExternalServer():
    """Imagem de um servidor externo, fornece as interfaces para envio de mensagens."""
    def __init__(self, server_config):
        """Inicialização de servidor externo, recebe uma instancia de ServerConfig"""
        self.server_config = server_config

    def get_server_list(self, orig):
        """Requisita o servidor externo dos servidores por ele conhecidos e retorna a lista"""
        self.server_config.send(orig, 'get_server_list')

    def say_hello(self, orig):
        """Requisita o servidor externo avisando que está connectado à rede estabelecida"""
        self.server_config.send(orig, 'hello')
