class Token():
    def __init__(self, url, server_stack=[], response_stack=[]):
        """Inicializa o token com uma url, e opcionalmente recebendo a pilha de
        servidores e de respostas"""
        self.url = url
        self.stack = dict()
        for server, response in zip(server_stack, response_stack):
            self.stack[server] = response

    @property
    def server_stack(self):
        # TODO: docstring
        return sorted(self.stack.keys())

    @property
    def response_stack(self):
        # TODO: docstring
        return [self.stack[server] for server in self.server_stack]

    def append_server(self, server, response):
        """Adiciona o servidor e a resposta à pilha do token"""
        self.stack[server] = response

    def __repr__(self):
        """Cria uma expressão valorável do token para enviálo"""
        url = repr(self.url)
        server = repr(self.server_stack)
        response = repr(self.response_stack)
        format_parm = (url, server, response)
        return "Token(%s,%s,%s)" % format_parm
