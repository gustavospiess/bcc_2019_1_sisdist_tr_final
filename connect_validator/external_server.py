class ExternalServer():
    """Imagem de um servidor externo, fornece as interfaces para envio de mensagens."""
    def __init__(self, server_config):
        """Inicialização de servidor externo, recebe uma instancia de ServerConfig"""
        self.server_config = server_config

    @property
    def signature(self):
        return self.server_config.signature

    def get_server_list(self, orig):
        """Requisita o servidor externo dos servidores por ele conhecidos e retorna a lista"""
        self.server_config.send(orig, 'get_server_list')

    def say_hello(self, orig):
        """Requisita o servidor externo avisando que está connectado à rede estabelecida"""
        self.server_config.send(orig, 'hello')

    def send_token(self, orig, token):
        """Requisita o servidor externo enviando o token com a representação valorável."""
        self.server_config.send(orig, repr(token))

    def __str__(self):
        """implementação da conversão para string:
        "ExternalServer for {str(self.server_config.signature)}"."""
        return "ExternalServer for " + str(self.server_config.signature)
    
    def __repr__(self):
        # TODO: docstring
        return "ExternalServer(%s)" % (repr(self.server_config))

    def __hash__(self):
        """Calcula um hash para o servidor exerno, levando em consideração a configuração do mesmo"""
        return hash(self.server_config)*31-1
    
    def __eq__(self, other):
        """Valida a igualdade dos objetos por meio da classe e do hash.
        Não sendo o 'other' uma instância de ExternalServer, é retornado NotImplemented.
        Se não, é retornada a comparação dos hash's."""
        if not isinstance(other, ExternalServer):
            return NotImplemented
        return hash(self) == hash(other)
