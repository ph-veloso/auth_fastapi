from pydantic import BaseModel


class Usuario(BaseModel):
    id = int
    nome = str
    email = str
    hashed_password = str

    class config:
        orm_mode = True


class Endereco(BaseModel):
    id = int
    usuario_id = int
    pais = str
    cep = str
    estado = str
    cidade = str
    rua = str
    bairro = str
    numero = int
    complemento = str

    class config:
        orm_mode = True


class Documento(BaseModel):
    id = int
    usuario_id = int
    cpf = str
    pis = str

    class config:
        orm_mode = True
