import pytest
import json
from main import app  # Supondo que o seu arquivo Flask se chame main.py


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_index(client):
    """Teste do endpoint de index."""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["name"] == "Jonathan Ponciano"
    assert data["email"] == "jonathan.ponciano@icloud.com"
    assert data["linkedin"] == "https://www.linkedin.com/in/jonathan-ponciano-silva/"


@pytest.mark.parametrize("platform", ["meta_ads", "ga4", "tiktok_insights"])
def test_platform_report(client, platform):
    """Teste do endpoint de geração de relatório por plataforma."""
    response = client.get(f'/{platform}')
    assert response.status_code in [200, 404]  # 404 caso não haja dados para a plataforma
    assert response.content_type == "text/csv" if response.status_code == 200 else "text/html"


@pytest.mark.parametrize("platform", ["meta_ads", "ga4", "tiktok_insights"])
def test_platform_summary(client, platform):
    """Teste do endpoint de resumo por plataforma."""
    response = client.get(f'/{platform}/resumo')
    assert response.status_code in [200, 404]
    assert response.content_type == "text/csv" if response.status_code == 200 else "text/html"


def test_general_report(client):
    """Teste do endpoint de relatório geral."""
    response = client.get('/geral')
    assert response.status_code in [200, 404]
    assert response.content_type == "text/csv" if response.status_code == 200 else "text/html"


def test_general_summary(client):
    """Teste do endpoint de resumo geral."""
    response = client.get('/geral/resumo')
    assert response.status_code in [200, 404]
    assert response.content_type == "text/csv" if response.status_code == 200 else "text/html"
