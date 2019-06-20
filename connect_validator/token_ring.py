class Token():
    def __init__(self, url, server_stack=[], response_stack=[]):
        # TODO: docstring
        self.url = url
        self.server_stack = server_stack
        self.response_stack = response_stack

    def append_server(self, server, response):
        self.server_stack.append(server)
        self.response_stack.append(response)

    def __repr__(self):
        # TODO: docstring
        url = repr(self.url)
        server = repr(self.server_stack)
        response = repr(self.response_stack)
        format_parm = (url, server, response)
        return "Token(%s,%s,%s)" % format_parm
