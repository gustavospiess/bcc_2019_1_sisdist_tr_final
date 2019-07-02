# Trabalho final
## Sistemas Distribuídos
#### BCC 2019/1
- Francisco Lucas Sens
- Gustavo Henrique Spiess
- José Wollinger

### Introdução
Este é um software puramente distribuído cuja função é verificar se determinada URL é alcançável por diversos lugares e conexões diferentes. O problema se dá no universo de diferentes clientes, aonde é desejável saber se a partir de uma determinada conexão é possível atingir um determinado recurso, indiferente de sua localização, identificado pela sua URL. O software foi desenvolido na linguagem Python em sua terceira versão. Foi utilizado o protocolo de conexão UDP para as mensagens entre os servidores. 

### Descrição

O objetivo do trabalho é o desenvolvimento de um sistema distribuído para a validação de acesso à uma URL determinada a partir de cada servidor conectado.
A proposta é de que o sistema seja executado de forma completamente decentralizada, isso é, sem a figura de um processo coordenador.
Uma vez que o programa seja executado, iniciando um novo servidor, e tenha sido informado um IP e porta validos de outro servidor executando, é iniciado um processo de apresentação.
A qualquer momento, um servidor pode iniciar a validação de acesso dos demais servidores a uma determinada URL, ele faz isso por meio da geração de um token e o envio do mesmo para um o servidor com id diretamente maior que o seu.

- Apresentação dos servidores:
  - O servidor recentemente aberto (`A`) solicita os dados dos demais servidores para o servidor conhecido (`B`).
  - O servidor `B` responde com a listagem de todos os servidores conhecidos.
  - O servidor `A` envia uma mensagem de aceno para cada servidor recebido na listagem (`C1`, `C2` ... `Cn`).
- Requisição de validação de acesso:
  - O servidor de origem (`A`) gera um token com a URL que se deseja acessar:
    1. Enfileira seu próprio ID no token
    2. Enviando o token para o próximo servidor conhecido (ordenado por id, se `A` for o maior, envia para o menor id conhecido).
  - O servidor `B` recebe o token gerado em `A`:
    0. Verifica se já não está presente.
    2. Valida se possui acesso à URL presente no token.
    3. Enfileira seu ID (e se possui acesso) e encaminha para o próximo servidor do ciclo.
  - O servidor `Cn` repete o processo até que a mensagem retorne a `A`.
  - O servidor `A` desenfileira os dados do token e apresenta-o para o usuário.
  - Se o servidor `A` não receber novamente o token em um tempo determinado (uma constante configurável multiplicada pela quantidade de servidores conhecidos), informa ao usuário que houve um erro (timeout) e questiona se deseja executar novamente o processo.

### Demo
![alt text](https://i.ibb.co/mz8WB42/img.png)

### Executando
Para rodar utilize:
```bash
python3 connect_validator 
```

###Parametros:
Para maiores informações quanto à parametrização possível execute:
```bash

$ python connect_validator --help

> Options:
>   -d, --debug                  Show UDP message log.
>   -s, --server IP:PORT NUMBER  ip:port of an existing server. If ommited a new
>                                net will be started.
>   -p, --port PORT NUMBER       port for in witch you want your server. This
>                                will be used as receive port and this +1 as
>                                sending port.
>   -t, --timeout INTEGER
>   --help                       Show this message and exit.
```

### Trechos de código

Inicialização de socket de envio:
```python
    def _client_socket(self, orig):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(('', orig.send[1]))
        return udp_socket
```

Inicialização de socket de recebimento:
```python
    def _server_socket(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(self.signature.receive)
        return udp_socket
```

Manutenção do loop de recebimento de mensagens.
```python    
    def _loop(self, call_back):
        with self._server_socket() as udp_socket:
            while True:
                msg = udp_socket.recvfrom(1024)
                (bts_msg, orig) = msg
                if not call_back(bts_msg, orig):
                    break
```

Requisição do servidor externo dos servidores por ele conhecidos e retorna a lista
```python
    def get_server_list(self, orig):
        self.server_config.send(orig, 'get_server_list')
```

Requisição do servidor externo avisando que está connectado à rede estabelecida
```python
    def say_hello(self, orig):
        self.server_config.send(orig, 'hello')
```

Realiza um envio UDP/IP para a assinatura configurada.
Necessário informar a origem para que seja realizado o bind do mesmo no envio.
É esperado que a mensagem seja uma string
```python
    def send(self, orig, message):
        with self._client_socket(orig) as udp:
            udp.sendto (self.encode(message), self.signature.receive)
```