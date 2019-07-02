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

