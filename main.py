import json
from operator import or_
from typing import Union

from database import SessionLocal, engine
from fastapi import (
    FastAPI,
    HTTPException,
    Request,
    Form,
    Depends,
    Response,
    Cookie,
    Header,
)
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_
from starlette.responses import RedirectResponse
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware import Middleware
from pprint import pprint
from uuid import uuid4
import schema
import model
import bcrypt
import re

app = FastAPI()

model.Base.metadata.create_all(bind=engine)

app.mount("/public", StaticFiles(directory="public"), name="public")

templates = Jinja2Templates(directory="public/views")


def get_database_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def read_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/cadastro", response_class=HTMLResponse)
def read_sign_page(request: Request, response: Response):
    return templates.TemplateResponse(
        "cadastro.html", {"request": request, "reponse": response._headers}
    )


@app.get("/error", response_class=HTMLResponse)
def read_error(request: Request):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "message": "Usuário ou senha inválidos",
            "status_code": 401,
        },
        status_code=401,
    )


@app.post("/login")
async def handle_login_form(
    response: Response,
    request: Request,
    db: Session = Depends(get_database_session),
    login: str = Form(...),
    senha: str = Form(...),
):
    try:
        login_cpf_pis = int(login)
        user = (
            db.query(model.Documento, model.Usuario)
            .filter(
                or_(
                    model.Documento.cpf == login_cpf_pis,
                    model.Documento.pis == login_cpf_pis,
                )
            )
            .filter(model.Usuario.id == model.Documento.usuario_id)
            .first()
        )
    except Exception:
        login_email = login
        user = (
            db.query(model.Usuario, model.Documento)
            .filter(model.Usuario.email == login_email)
            .filter(model.Usuario.id == model.Documento.usuario_id)
            .first()
        )
    if not user:
        return RedirectResponse("/error", status_code=303)
    if bcrypt.checkpw(
        senha.encode("utf-8"), user.Usuario.hashed_password.encode("utf-8")
    ):
        cookie_token = uuid4()
        response = templates.TemplateResponse(
            "logado.html",
            {
                "user": user.Usuario.nome,
                "email": user.Usuario.email,
                "id": user.Usuario.id,
                "documento": user.Documento,
                "request": request,
            },
            status_code=303,
        )
        response.set_cookie(key="Auth", value=cookie_token)
        return response


@app.get("/logout")
async def logout(request: Request, response: Response):
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie(key="Auth")
    return response


@app.post("/cadastrando")
def handle_sign_form(
    db: Session = Depends(get_database_session),
    nome: schema.Usuario.nome = Form(...),
    email: schema.Usuario.email = Form(...),
    senha: schema.Usuario.hashed_password = Form(...),
    cep: schema.Endereco.cep = Form(...),
    rua: schema.Endereco.rua = Form(...),
    pais: schema.Endereco.pais = Form(...),
    bairro: schema.Endereco.bairro = Form(...),
    cidade: schema.Endereco.cidade = Form(...),
    estado: schema.Endereco.estado = Form(...),
    numero: schema.Endereco.numero = Form(...),
    complemento: schema.Endereco.complemento = Form(default=""),
    cpf: schema.Documento.cpf = Form(...),
    pis: schema.Documento.pis = Form(...),
):
    senha_codificada = senha.encode("utf-8")
    senha_hash = bcrypt.hashpw(senha_codificada, bcrypt.gensalt())

    cpf_numbers = re.sub("[^0-9]", "", cpf)

    pis_numbers = re.sub("[^0-9]", "", pis)

    cep_numbers = re.sub("[^0-9]", "", cep)

    usuario = model.Usuario(nome=nome, email=email, hashed_password=senha_hash)

    db.add(usuario)
    db.flush()

    endereco = model.Endereco(
        cep=cep_numbers,
        pais=pais,
        rua=rua,
        bairro=bairro,
        estado=estado,
        cidade=cidade,
        numero=numero,
        complemento=complemento,
        usuario_id=usuario.id,
    )

    documento = model.Documento(
        cpf=cpf_numbers,
        pis=pis_numbers,
        usuario_id=usuario.id,
    )

    db.add(endereco)
    db.add(documento)
    db.commit()

    return RedirectResponse("/", status_code=303)


@app.post("/cadastro_edit", response_class=HTMLResponse)
def edit_sign(
    request: Request,
    response: Response,
    db: Session = Depends(get_database_session),
    id: schema.Usuario.id = Form(...),
):
    user = (
        db.query(model.Usuario, model.Documento, model.Endereco)
        .filter(model.Usuario.id == id)
        .filter(model.Usuario.id == model.Documento.usuario_id)
        .filter(model.Usuario.id == model.Endereco.usuario_id)
        .first()
    )

    print(user)
    return templates.TemplateResponse(
        "edit_cadastro.html", {"request": request, "user": user}
    )


@app.delete("/delete_user/{id}")
async def delete_user(id: int, db: Session = Depends(get_database_session)):
    user = db.query(model.Usuario).filter(model.Usuario.id == id).first()
    db.delete(user)
    db.commit()
    return RedirectResponse("/logout", status_code=303)


@app.post("/edit_user")
async def edit_user(
    db: Session = Depends(get_database_session),
    id: schema.Usuario.id = Form(...),
    nome: schema.Usuario.nome = Form(...),
    email: schema.Usuario.email = Form(...),
    senha: schema.Usuario.hashed_password = Form(...),
    cep: schema.Endereco.cep = Form(...),
    rua: schema.Endereco.rua = Form(...),
    pais: schema.Endereco.pais = Form(...),
    bairro: schema.Endereco.bairro = Form(...),
    cidade: schema.Endereco.cidade = Form(...),
    estado: schema.Endereco.estado = Form(...),
    numero: schema.Endereco.numero = Form(...),
    complemento: schema.Endereco.complemento = Form(default=""),
    cpf: schema.Documento.cpf = Form(...),
    pis: schema.Documento.pis = Form(...),
):
    usuario = (
        db.query(model.Usuario, model.Documento, model.Endereco)
        .filter(model.Usuario.id == id)
        .filter(model.Usuario.id == model.Documento.usuario_id)
        .filter(model.Usuario.id == model.Endereco.usuario_id)
        .first()
    )
    senha_codificada = senha.encode("utf-8")
    senha_hash = bcrypt.hashpw(senha_codificada, bcrypt.gensalt())

    cpf_numbers = re.sub("[^0-9]", "", cpf)

    pis_numbers = re.sub("[^0-9]", "", pis)

    usuario.Usuario.nome = nome
    usuario.Usuario.email = email
    usuario.Usuario.hashed_password = senha_hash
    usuario.Endereco.cep = cep
    usuario.Endereco.rua = rua
    usuario.Endereco.pais = pais
    usuario.Endereco.bairro = bairro
    usuario.Endereco.estado = estado
    usuario.Endereco.cidade = cidade
    usuario.Endereco.numero = numero
    usuario.Endereco.complemento = complemento
    usuario.Documento.cpf = cpf_numbers
    usuario.Documento.pis = pis_numbers
    db.commit()
    return RedirectResponse("/", status_code=303)
