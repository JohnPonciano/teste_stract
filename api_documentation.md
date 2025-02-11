
# API de Relatórios Stract

Esta API fornece acesso a dados de plataformas de anúncios, incluindo relatórios e resumos sobre as contas e os insights gerados.

## Endpoints

### `GET /`

Retorna informações gerais sobre o autor da API.

**Resposta Exemplo:**

```json
{
    "name": "Jonathan Ponciano",
    "email": "jonathan.ponciano@icloud.com",
    "linkedin": "https://www.linkedin.com/in/jonathan-ponciano-silva/"
}
```

### `GET /<platform>`

Gera um relatório CSV para a plataforma especificada.

**Parâmetros:**

- `platform`: Nome da plataforma (ex: "meta_ads", "ga4",).

**Resposta Exemplo:**
- Um arquivo CSV será retornado contendo os dados de todas as contas e insights para a plataforma especificada.

### `GET /<platform>/resumo`

Gera um resumo CSV para a plataforma especificada.

**Parâmetros:**

- `platform`: Nome da plataforma (ex: "meta_ads", "ga4").

**Resposta Exemplo:**
- Um arquivo CSV será retornado com um resumo dos dados de todas as contas na plataforma especificada.

### `GET /geral`

Gera um relatório CSV geral, incluindo dados de todas as plataformas disponíveis.

**Resposta Exemplo:**
- Um arquivo CSV será retornado com dados de todas as plataformas.

### `GET /geral/resumo`

Gera um resumo CSV geral, incluindo dados de todas as plataformas.

**Resposta Exemplo:**
- Um arquivo CSV será retornado com um resumo dos dados de todas as plataformas.

## Como rodar os testes

1. Instale as dependências:

   ```bash
   pip install pytest
   ```

2. Execute os testes:

   ```bash
   pytest
   ```

## Como rodar a API

1. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

2. Execute o servidor Flask:

   ```bash
   python app.py
   ```

3. A API estará disponível em `http://127.0.0.1:5000`.
