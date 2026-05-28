# Mundo Invest Backend - Client Management & Pipefy Integration

Este projeto é um esqueleto de sistema interno desenvolvido para o **Mundo Invest**, com o objetivo de gerenciar clientes, seus patrimônios e integrar esses processos com o **Pipefy** através de sua API GraphQL.

## 🚀 Tecnologias Utilizadas

- **Linguagem:** Python 3.12+
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Gerenciador de Dependências:** [uv](https://github.com/astral-sh/uv)
- **Banco de Dados:** PostgreSQL (via Docker)
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Testes:** Pytest

## 🏗️ Arquitetura

O projeto segue uma arquitetura em camadas para garantir a separação de responsabilidades e facilidade de manutenção:

- **API Routes (`app/api/`):** Controladores que recebem as requisições HTTP.
- **Services (`app/services/`):** Orquestração dos fluxos de negócio e integrações.
- **Domain (`app/domain/`):** Regras de negócio puras, enums e exceções customizadas.
- **Repositories (`app/repositories/`):** Camada de persistência e consultas ao banco de dados.
- **Integrations (`app/integrations/`):** Cliente Pipefy responsável por construir os payloads GraphQL.
- **Models/Schemas:** Definições de tabelas SQL e modelos Pydantic para validação.

## 🛠️ Como Executar o Projeto Localmente

### Pré-requisitos
- [uv](https://github.com/astral-sh/uv) instalado.
- Docker e Docker Compose.

### Passo a Passo

1. **Clonar o repositório:**
   ```bash
   git clone <url-do-repositorio>
   cd client-management-pipefy
   ```

2. **Configurar o ambiente:**
   ```bash
   cp .env.example .env
   # As configurações padrão no .env.example já funcionam com o Docker Compose
   ```

3. **Instalar dependências:**
   ```bash
   uv sync
   ```

4. **Subir o banco de dados:**
   ```bash
   docker-compose up -d
   ```

5. **Executar migrações do banco:**
   ```bash
   uv run alembic upgrade head
   ```

6. **Iniciar a aplicação:**
   ```bash
   uv run uvicorn app.main:app --reload
   ```
   A API estará disponível em `http://localhost:8000`. Acesse `/docs` para a documentação interativa.

## 🧪 Executando os Testes

Os testes automatizados utilizam um banco de dados SQLite em memória para isolamento e performance.

Para rodar todos os testes:
```bash
uv run pytest
```

Para rodar com cobertura:
```bash
uv run pytest --cov
```

## 📡 Endpoints da API

### 1. Criação de Cliente
**Endpoint:** `POST /clientes`

**Payload Exemplo:**
```bash
curl -X 'POST' \
  'http://localhost:8000/clientes' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "cliente_nome": "João Silva",
    "cliente_email": "joao.silva@example.com",
    "tipo_solicitacao": "Atualização cadastral",
    "valor_patrimonio": 250000
  }'
```

### 2. Webhook Pipefy (Atualização de Card)
**Endpoint:** `POST /webhooks/pipefy/card-updated`

**Payload Exemplo:**
```bash
curl -X 'POST' \
  'http://localhost:8000/webhooks/pipefy/card-updated' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "event_id": "evt_123",
    "card_id": "card_456",
    "cliente_email": "joao.silva@example.com",
    "timestamp": "2026-05-18T12:00:00Z"
  }'
```

## 🔗 Integração Pipefy (GraphQL)

Embora a aplicação salve os dados localmente, ela está preparada para a integração real com o Pipefy. Os payloads das mutations GraphQL seguem a documentação:

- **Criação de Card:** Localizado em `app/integrations/pipefy_client.py`, utiliza a mutation `createCard` para espelhar o cliente no Pipefy.
- **Atualização de Campos:** Utiliza a mutation `updateCardField` para sincronizar o status `"Processado"` e a **prioridade calculada** (Alta para patrimônio >= 200k, Normal caso contrário).

## ☁️ Visão de Produção na AWS

Em um ambiente de produção na AWS, essa aplicação poderia ser evoluída para uma arquitetura mais escalável.

Uma possibilidade seria expor os endpoints da API por meio do **Amazon API Gateway**, responsável por receber as requisições HTTP, aplicar políticas de controle de acesso, rate limiting e encaminhar as chamadas para a camada de processamento.

A camada de aplicação poderia ser executada de duas formas principais:

1. **AWS Lambda**, em uma abordagem serverless, principalmente se o volume de requisições for variável e o objetivo for reduzir a necessidade de gerenciar servidores.
2. **Amazon ECS com Fargate**, caso a aplicação FastAPI seja mantida como um serviço web tradicional, rodando em container, com maior controle sobre tempo de execução, conexão persistente e configuração do ambiente.

Para a persistência dos dados, o banco PostgreSQL local utilizado neste desafio poderia ser substituído por um **Amazon RDS for PostgreSQL**, mantendo o modelo relacional da aplicação.

O processamento dos webhooks poderia ser desacoplado usando **Amazon SQS**. Nesse cenário, o endpoint de webhook receberia o evento do Pipefy, faria uma validação inicial e publicaria a mensagem em uma fila. Uma função Lambda ou worker consumiria essa fila de forma assíncrona para processar a regra de prioridade, atualizar o banco e simular/enviar a atualização para o Pipefy. Essa abordagem melhora a resiliência, pois evita perda de eventos em caso de instabilidade temporária e permite controlar retentativas.

Para eventos que falharem repetidamente, seria possível configurar uma **Dead Letter Queue (DLQ)**, permitindo investigar mensagens que não puderam ser processadas com sucesso após determinado número de tentativas.

A idempotência continuaria sendo essencial em produção. O `event_id` recebido no webhook deveria permanecer com restrição de unicidade no banco ou em uma tabela específica de eventos processados. Assim, mesmo que o Pipefy envie o mesmo webhook mais de uma vez, o sistema evita reprocessamento duplicado.

As credenciais e configurações sensíveis, como URL do banco, usuário, senha e token de integração com o Pipefy, não ficariam em arquivos `.env` dentro do servidor. Elas seriam armazenadas no **AWS Secrets Manager** ou no **AWS Systems Manager Parameter Store**, sendo acessadas pela aplicação em tempo de execução com permissões controladas por IAM.

Para observabilidade, a aplicação usaria **Amazon CloudWatch** para centralizar logs, métricas e alarmes. Seria possível monitorar erros nos endpoints, falhas no processamento de webhooks, quantidade de mensagens na fila e tempo médio de resposta da API.
