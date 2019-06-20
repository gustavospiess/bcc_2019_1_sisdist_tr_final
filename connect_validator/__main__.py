from external_server import ExternalServer
from server_config import ServerConfig
from server_config import ServerSignature
from server import Server

import time

ip = ''

def main():

    a_sig = ServerSignature('localhost', 17692)
    a_server = Server(a_sig)

    a_s_config = ServerConfig(a_sig)
    a_ext_server = ExternalServer(a_s_config)

    b_sig = ServerSignature('localhost', 17692+5)
    b_server = Server(b_sig, a_ext_server)

    time.sleep(1)

    c_sig = ServerSignature('localhost', 17692+10)
    c_server = Server(c_sig, a_ext_server)

    time.sleep(1)

    print('----------------')
    print(a_sig)
    print(a_server.server_array())
    print(b_sig)
    print(b_server.server_array())
    print(c_sig)
    print(c_server.server_array())
    print('----------------')

    time.sleep(1)

    a_server.send_token('https://github.com/gustavospiess/bcc_2019_1_sisdist_tr_final/tree/refactor')# TODO: Normalizar url
    
    time.sleep(12)

    a_server.halt()
    b_server.halt()
    c_server.halt()

if __name__ == '__main__':
    main()
