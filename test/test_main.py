from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_delete_user():
    response = client.delete("/delete_user/42")
    assert response.status_code == 303


def test_handle_sign_up_form():
    response = client.post(
        "/cadastrando",
        data={
            "nome": "teste",
            "email": "teste@email",
            "senha": "teste_senha",
            "cep": "01001000",
            "rua": "Rua dos Bobos",
            "pais": "Brasil",
            "bairro": "Jardim Paulista",
            "cidade": "São Paulo",
            "estado": "SP",
            "numero": 123,
            "complemento": "Casa",
            "cpf": "12345678901",
            "pis": "12345678901",
        },
    )
    assert response.status_code == 303
