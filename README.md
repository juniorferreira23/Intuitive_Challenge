# Intuitive Challenge

## 📖 Descrição
Este repositório tem como objetivo armazenar os desafios proporcionados pela Intuitive.

---

## 💻 Tecnologias
- **Python**: Versão 3.13
- **Vue.js**: Versão 3.5

## 📚 Bibliotecas
As bibliotecas utilizadas podem ser consultadas no arquivo `pyproject.toml`.

---

## ✨ Funcionalidades
- Web scraping dos documentos governamentais da ANS (Anexos I e II)
- Extração de tabelas dos documentos da ANS
- Web scraping dos documentos referentes às operadoras e suas demonstrações contábeis
- ETL para popular o banco de dados com os dados das operadoras e suas demonstrações contábeis
- Aplicação full stack para criar uma interface de pesquisa com Vue.js e um endpoint com FastAPI

---

## 🛠 Instalação

### ✅ Dependências
1. **Python**: Certifique-se de que o Python está instalado no seu sistema. [Download](https://www.python.org/downloads/)
2. **Git**: Instale o Git para clonar o repositório. [Download](https://git-scm.com/downloads)
3. **UV**: Instalação do gerenciador de pacotes. [Guia de Instalação](https://docs.astral.sh/uv/getting-started/installation/)
4. **Docker**: Gerenciador de contêiner para o banco de dados. [Instalação](https://docs.docker.com/engine/install/)

### 🔄 Clonar o Repositório
Abra seu terminal (Bash, PowerShell ou CMD) e execute o seguinte comando:
```bash
git clone https://github.com/juniorferreira23/Intuitive_Challenge.git
```
Acesse o diretório do projeto:
```bash
cd Intuitive_Challenge
```

### 📦 Criando um Ambiente Virtual e Instalando Dependências
```bash
uv sync
```

### 🗄️ Iniciar o Banco de Dados
1. Preencha as configurações do seu banco de dados no arquivo `docker-compose.yml`.
2. Preencha as constantes do banco de dados no arquivo `example.env` e renomeie-o para `.env`.
3. Acesse o container e o mysql para criar o banco de dados.

Execute o comando:
```bash
docker compose up
```
Se estiver usando Linux, pode ser necessário utilizar `sudo`:
```bash
sudo docker compose up
```
Acessando o container
```bash
docker exec it <nome_do_container> bash
```
Acessando o db mysql
```bash
mysql -u <usuario> -p
```
Coloque a senha e quando acessa o banco de dados, dê o comando
```bash
create database <database_name>;
```

### ▶️ Executando o Código
Para rodar os desafios 1 a 3, utilize o comando:
```bash
uv run main.py
```
Para executar o desafio 4 (aplicação completa):

#### Iniciar o Frontend
```bash
cd app/frontend/
npm run dev
```

#### Iniciar o Backend
```bash
uv run fastapi dev app/backend/main.py
```

### 📜 Documentação dos Endpoints (Swagger)
Acesse o link abaixo para visualizar os endpoints da API:
[http://localhost:8000/docs](http://localhost:8000/docs)

