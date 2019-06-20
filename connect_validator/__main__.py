from external_server import ExternalServer
from server_config import ServerConfig
from server import Server
from server_config import ServerSignature

import ipaddress
import time
import os

import click # TODO: manual de instalação (pip install click)

def menu(server, debug):
    while True:
        if not debug:
            os.system('cls' if os.name == 'nt' else 'clear')
        print('--------------------------------------------------------------------------------')   
        print('You are runnig in '+str(server.signature))
        print('Type exit/Ctrl-C/Ctrl-D to finish')   
        print('Type an URL to validate it')
        print('Known servers:')
        for tup in server.server_array():
            sig = ServerSignature(*tup)
            print(' - ' + str(sig))
        print('--------------------------------------------------------------------------------')   

        inp = 'exit'
        try:
            inp = input()
        except:
            pass
        if inp == 'exit':
            break
        server.send_token(inp)

    server.halt()

def validate(ip, port):
    ipaddress.ip_address(ip)

    if int(port) <= 5000:
        raise Exception()

    sig = ServerSignature(ip, int(port))
    return sig

class SignatureArgument(click.ParamType):
    name = 'ip:port number'
    def convert(self, value, param, ctx):
        try:
            (ip, port) = value.split(':')
            return validate(ip, port)
        except:
            self.fail('Not a valid ip or port (port must be bigger than 5000)', param, ctx)

class PortArgument(click.ParamType):
    name = 'port number' 
    def convert(self, value, param, ctx):
        try:
            return validate('127.0.0.1', value)
        except:
            self.fail('Not a valid port (port must be bigger than 5000).', param, ctx)

@click.command()
@click.option('--debug', '-d', 'debug', help='Show UDP message log.', is_flag=True)
@click.option('--server', '-s', 'server', type=SignatureArgument(), help='ip:port of an existing server. If ommited a new net will be started.')
@click.option('--port', '-p', 'port', type=PortArgument(), default='5050', help='port for in witch you want your server. This will be used as receive port and this +1 as sending port.')
@click.option('--timeout', '-t', 'timeout_limit', type=int, default=2)
def cli(debug, port, server, timeout_limit):
    ext = None
    if port == server:
        print('You cant connect to yourself in the same port.')
        return
    if server and port.receive[0] == server.receive[0] and abs(port.receive[1] - server.receive[1]) == 1:
        print(port.receive[1])
        print(server.receive[1])
        print(abs(port.receive[1] - server.receive[1]))
        print('A server use Two ports, the onde informed and the one informed + 1, please, select another port.')
        return
    if server:
        conf = ServerConfig(server)
        ext = ExternalServer(conf)
    local_server = Server(port, ext, timeout_limit, debug)

    if debug:
        time.sleep(timeout_limit or 2)
    menu(local_server, debug)

if __name__ == '__main__':
    cli()
