from fastapi.testclient import TestClient

from main import app
from security.rate_limit import limiter
from sqlite_database import criar_banco


# Garante que o banco e os dados de teste existam
criar_banco()

client = TestClient(app)


def resetar_rate_limit():
    limiter.reset()


def obter_token(username: str, password: str) -> str:
    resetar_rate_limit()

    resposta = client.post(
        "/auth/token",
        data={
            "username": username,
            "password": password,
        },
    )

    assert resposta.status_code == 200

    return resposta.json()["access_token"]


def test_acesso_sem_token():
    resposta = client.post(
        "/predict",
        json={
            "texto": "Quero um reembolso"
        },
    )

    assert resposta.status_code == 401


def test_login_com_credenciais_validas():
    resetar_rate_limit()

    resposta = client.post(
        "/auth/token",
        data={
            "username": "admin",
            "password": "infnet",
        },
    )

    assert resposta.status_code == 200
    assert "access_token" in resposta.json()
    assert resposta.json()["token_type"] == "bearer"


def test_login_com_senha_invalida():
    resetar_rate_limit()

    resposta = client.post(
        "/auth/token",
        data={
            "username": "admin",
            "password": "senha_errada",
        },
    )

    assert resposta.status_code == 401


def test_usuario_nao_acessa_recurso_de_outro_usuario():
    token = obter_token(
        "usuario2",
        "teste123",
    )

    resposta = client.get(
        "/predictions/1",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert resposta.status_code == 404


def test_campo_extra_e_rejeitado():
    token = obter_token(
        "admin",
        "infnet",
    )

    resposta = client.post(
        "/predict",
        json={
            "texto": "Quero um reembolso",
            "campo_extra": "valor não permitido",
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert resposta.status_code == 422


def test_rate_limit_no_login():
    resetar_rate_limit()

    # As 10 primeiras requisições devem ser permitidas
    for _ in range(10):
        resposta = client.post(
            "/auth/token",
            data={
                "username": "admin",
                "password": "infnet",
            },
        )

        assert resposta.status_code == 200

    # A 11ª requisição deve ser bloqueada
    resposta = client.post(
        "/auth/token",
        data={
            "username": "admin",
            "password": "infnet",
        },
    )

    assert resposta.status_code == 429