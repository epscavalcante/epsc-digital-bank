# 🌌 EPSC Digital Bank - Core Banking Engine

O **EPSC Digital Bank** é um motor de transações financeiras (Core Banking) desenvolvido para demonstrar padrões de arquitetura de alta resiliência, consistência transacional e isolamento de domínio.

O projeto foca no desafio de transferências entre contas (P2P), garantindo que o dinheiro nunca seja "perdido" ou "duplicado" em cenários de alta concorrência.

## Ambiente de desenvolvimento

O projeto roda dentro do container `app` definido no `docker compose`. Para facilitar o fluxo do dia a dia, existe um `Makefile` na raiz com os comandos mais usados.

### Comandos principais

```bash
make build   # builda a imagem
make up      # sobe os containers
make shell   # abre shell no container app
make api     # sobe a API FastAPI na porta 8000
make lint    # roda ruff via taskipy
make format  # formata o código via taskipy
make test    # roda os testes via taskipy
make cov     # gera coverage xml via taskipy
make check   # roda lint, mypy e testes
make down    # derruba tudo do compose
```

Por padrão, o `Makefile` usa `sudo docker compose`, já que o ambiente atual depende de permissões elevadas para executar comandos Docker.

## Escopo inicial

Precisa ser pequeno o suficiente para ser implementável, mas robusto o suficiente para não gerar uma arquitetura descartável.

1. Funcionalidades do MVP:
* Cadastro de usuário
* Criação automática de conta financeira
* Consulta de saldo
* Consulta de extrato
* Transferência entre contas internas
* Histórico de transferências
* Idempotência para requisições
* Auditoria de ações críticas
* Observabilidade básica
* Eventos de domínio internos
* Fora do MVP inicialmente

2. Principais regras de negócio

Essas regras precisam estar explícitas logo cedo porque elas afetam domínio, banco, concorrência e testes.

* Uma conta só pode transferir se estiver ativa
* Não pode transferir para si mesmo
* Valor precisa ser maior que zero
* Conta de origem precisa ter saldo suficiente
* Uma transferência deve ser processada uma única vez
* Repetições da mesma requisição com a mesma idempotency key devem retornar o mesmo resultado
* Toda transferência precisa gerar pelo menos dois lançamentos contábeis: ** débito na conta origem**, ** crédito na conta destino**
* O sistema nunca pode permitir que apenas um lado da transação seja persistido
* Saldo disponível nunca deve ser alterado manualmente sem lançamento no ledger
* Toda falha de processamento deve ser auditável
* Toda operação financeira deve possuir rastreabilidade ponta a ponta
