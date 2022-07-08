from email.policy import default
from enum import unique
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = {"mysql_engine": "InnoDB"}
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(128), index=True)
    email = Column(String(128), unique=True, index=True)
    hashed_password = Column(String(128))

    enderecos = relationship("Endereco", back_populates="owner_endereco")
    documentos = relationship("Documento", back_populates="owner_documento")


class Endereco(Base):
    __tablename__ = "enderecos"
    __table_args__ = {"mysql_engine": "InnoDB"}
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(
        Integer, ForeignKey("usuarios.id", onupdate="CASCADE", ondelete="CASCADE")
    )
    pais = Column(String(40))
    cep = Column(String(20))
    estado = Column(String(60))
    cidade = Column(String(60))
    rua = Column(String(60))
    bairro = Column(String(50))
    numero = Column(Integer)
    complemento = Column(String(30))

    owner_endereco = relationship("Usuario", back_populates="enderecos")


class Documento(Base):
    __tablename__ = "documentos"
    __table_args__ = {"mysql_engine": "InnoDB"}
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(
        Integer, ForeignKey("usuarios.id", onupdate="CASCADE", ondelete="CASCADE")
    )
    cpf = Column(String(20), unique=True, index=True)
    pis = Column(String(20), unique=True, index=True)

    owner_documento = relationship("Usuario", back_populates="documentos")
