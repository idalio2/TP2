from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def obter_token(username: str, password: str) -> str:
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