from flask import Flask, Response, jsonify
import requests
import csv

app = Flask(__name__)

API_BASE_TOKEN = "https://sidebar.stract.to"
API_TOKEN = "ProcessoSeletivoStract2025"

def fetch_data(endpoint, params=None):
    """Faz uma requisição à API externa e retorna os dados."""
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    response = requests.get(f"{API_BASE_TOKEN}{endpoint}", headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao acessar {endpoint}: {response.status_code}")
        return None

def generate_csv_response(data, field_names):
    """Gera um CSV como resposta HTTP."""
    field_names = ["Platform", "Account Name",] + list(field_names)
    response = Response(content_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=report.csv"
    writer = csv.DictWriter(response.stream, fieldnames=field_names)
    writer.writeheader()
    for row in data:
        # Garante que todos os campos estejam presentes em cada linha
        for field in field_names:
            row.setdefault(field, "")
        writer.writerow(row)
    return response

@app.route('/')
def index():
    return jsonify({
        "name": "Jonathan Ponciano",
        "email": "jonathan.ponciano@icloud.com",
        "linkedin": "https://www.linkedin.com/in/jonathan-ponciano-silva/"
    })

@app.route("/<platform>")
def platform_report(platform):
    # Recupera dados da plataforma e conta
    accounts = fetch_data(f"/api/accounts?platform={platform}")
    fields = fetch_data(f"/api/fields?platform={platform}")

    platform_name = None
    
    if platform == 'meta_ads':
        platform_name = 'Facebook'
    elif platform == 'ga4':
        platform_name = 'Google Analytics'
    elif platform == 'tiktok_insights':
        platform_name = 'TikTok'

    
    if not accounts or 'accounts' not in accounts:
        return "Nenhuma conta encontrada para a plataforma", 404
    if not fields or 'fields' not in fields:
        return "Nenhum campo encontrado para a plataforma", 404

    # Extraímos apenas os valores de 'value' dos campos
    field_names = [field['value'] for field in fields['fields']]
    rows = []
    
    for account in accounts['accounts']:
        account_name = account["name"]
        account_id = account["id"]
        account_token = account["token"]
        
        # Verifique se o token está presente
        if not account_token:
            print(f"Erro: Token faltando para a conta {account_id}")
            continue

        # Recupera insights de cada conta
        insights = fetch_data("/api/insights", {
            "platform": platform, "account": account_id, 
            "token": account_token, "fields": ",".join(field_names)
        })

        if not insights or 'insights' not in insights:
            print(f"Erro: Não foi possível obter insights para a conta {account_id}.")
            continue
        
        # Para cada anúncio, extraímos os dados de insights
        for ad in insights['insights']:
            
            if isinstance(ad, dict):
                row = {"Platform": platform_name, "Account Name": account_name}
                # Preenche as colunas com os campos de insights
                for field in field_names:
                    row[field] = ad.get(field, "")  # Valor vazio se o campo não existir
                rows.append(row)

    # Caso não haja dados, retorna erro
    if not rows:
        return "Nenhum dado encontrado para gerar o relatório.", 404

    # Retorna os dados em formato CSV
    return generate_csv_response(rows, field_names)



@app.route("/<platform>/resumo")
def platform_summary(platform):
    accounts = fetch_data(f"/api/accounts?platform={platform}")
    fields = fetch_data(f"/api/fields?platform={platform}")
    
    platform_name = None
    
    if platform == 'meta_ads':
        platform_name = 'Facebook'
    elif platform == 'ga4':
        platform_name = 'Google Analytics'
    elif platform == 'tiktok_insights':
        platform_name = 'TikTok'

    if not accounts or 'accounts' not in accounts:
        return "Nenhuma conta encontrada para a plataforma", 404
    if not fields or 'fields' not in fields:
        return "Nenhum campo encontrado para a plataforma", 404

    field_names = [] + [field['value'] for field in fields['fields']]
    summary = {}

    for account in accounts['accounts']:
        account_name = account["name"]
        account_id = account["id"]
        account_token = account["token"]
        
        if not account_token:
            print(f"Erro: Token faltando para a conta {account_id}")
            continue

        insights = fetch_data("/api/insights", {
            "platform": platform, "account": account_id,
            "token": account_token, "fields": ",".join(field_names)
        })

        if not insights or 'insights' not in insights:
            print(f"Erro: Não foi possível obter insights para a conta {account_id}.")
            continue
        
        # Inicializa a conta no resumo, se ainda não estiver lá
        if account_id not in summary:
            summary[account_id] = {"Platform": platform_name, "Account Name": account_name}
        
        # Para cada anúncio, soma os valores de campos numéricos
        for ad in insights['insights']:
            for field, value in ad.items():
                if field in field_names:  # Verifica se o campo está na lista de field_names
                    if isinstance(value, (int, float)):
                        summary[account_id][field] = summary[account_id].get(field, 0) + value
                    else:
                        summary[account_id][field] = value

    # Gera a lista de linhas agregadas
    aggregated_rows = list(summary.values())

    # Retorna os dados agregados em formato CSV
    return generate_csv_response(aggregated_rows, field_names)


@app.route("/geral")
def general_report():
    platforms = fetch_data("/api/platforms")
    all_rows = []
    field_names = set()
    
    # Iterando sobre todas as plataformas
    for platform in platforms['platforms']:
        accounts = fetch_data(f"/api/accounts?platform={platform['value']}")
        
        if not accounts:
            continue  # Pula se não houver contas para a plataforma

        for account in accounts['accounts']:
            account_name = account["name"]
            account_id = account["id"]
            fields = fetch_data(f"/api/fields?platform={platform['value']}")
            platform_field_names = [field['value'] for field in fields['fields']]
            
            # Atualiza o conjunto de todos os campos
            field_names.update(platform_field_names)
            
            # Coleta os insights para a conta na plataforma
            insights = fetch_data("/api/insights", {
                "platform": platform['value'], 
                "account": account_id, 
                "token": account['token'], 
                "fields": ",".join(platform_field_names)
            })
            
            # Iterando sobre os insights de cada anúncio
            for ad in insights['insights']:
                if isinstance(ad, dict):
                    row = {"Platform": platform['text'], "Account Name": account_name}
                    
                    # Preenchendo os campos com os valores dos insights
                    for field in platform_field_names:
                        if field in ad:
                            row[field] = ad[field]
                        else:
                            row[field] = ""  # Deixa vazio se o campo não existir para este anúncio
                    
                    # Calculando "Cost per Click estimated" se a plataforma não oferecer esse campo
                    if "Cost per Click estimated estimated" not in row and "spend" in row and "clicks" in row:
                        try:
                            row["Cost per Click estimated estimated"] = row["spend"] / row["clicks"] if row["clicks"] != 0 else 0
                            field_names.add("Cost per Click estimated estimated")  # Adiciona "Cost per Click estimated" ao field_names
                        except ZeroDivisionError:
                            row["Cost per Click estimated estimated"] = 0
                            field_names.add("Cost per Click estimated estimated")  # Adiciona "Cost per Click estimated" ao field_names
                    
                    all_rows.append(row)

    # Retorna os dados como CSV
    return generate_csv_response(all_rows, list(field_names))


@app.route("/geral/resumo")
def general_summary():
    platforms = fetch_data("/api/platforms")
    summary = {}
    field_names = set()

    for platform in platforms['platforms']:
        platform_name = platform['text']
        platform_id = platform['value']
        accounts = fetch_data(f"/api/accounts?platform={platform_id}")
        fields = fetch_data(f"/api/fields?platform={platform_id}")
        platform_field_names = [field['value'] for field in fields['fields']]

        # Atualiza o conjunto de todos os campos possíveis
        field_names.update(platform_field_names)

        # Inicializa a linha da plataforma no sumário
        if platform_id not in summary:
            summary[platform_id] = {"Platform": platform_name}

        # Define os campos como 0 para números e "" para texto
        for field in platform_field_names:
            summary[platform_id].setdefault(field, 0 if field not in ["Platform"] else "")

        for account in accounts.get('accounts', []):
            account_id = account["id"]
            insights = fetch_data("/api/insights", {
                "platform": platform_id, 
                "account": account_id, 
                "token": account['token'], 
                "fields": ",".join(platform_field_names)
            })

            # Processa os insights retornados
            for ad in insights.get('insights', []):
                for field, value in ad.items():
                    if field in field_names:  # Verifica se o campo está na lista de field_names
                        if isinstance(value, (int, float)):
                            summary[platform_id][field] = summary[platform_id].get(field, 0) + value
                        else:
                            summary[platform_id][field] = value

        # Calculando "Cost per Click estimated" se a plataforma não tiver esse campo
        if "Cost per Click estimated" not in summary[platform_id] and "spend" in summary[platform_id] and "clicks" in summary[platform_id]:
            clicks = summary[platform_id]["clicks"]
            spend = summary[platform_id]["spend"]
            summary[platform_id]["Cost per Click estimated"] = spend / clicks if clicks != 0 else 0
            field_names.add("Cost per Click estimated")

    for row in summary.values():
        row.pop("id", None)

    # Garante que todos os campos estejam presentes em todas as linhas
    for row in summary.values():
        for field in field_names:
            row.setdefault(field, "")
            

    return generate_csv_response(list(summary.values()), list(field_names))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    app.debug = True
