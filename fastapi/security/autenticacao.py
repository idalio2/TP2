from datetime import datetime, timedelta, timezone
from secrets import compare_digest
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session, select

from models.database import Usuario, get_session


CHAVE_SECRETA = "Projeto-de-Bloco-Análise-e-Segurança-de-Agentes-de-IA"
ALGORITMO = "HS256"
MINUTOS_EXPIRACAO = 30


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def autenticar_usuario(
        username: str,
        password: str,
        session: Session,
) -> Usuario | None:

    statement = select(Usuario).where(Usuario.username == username)

    usuario = session.exec(statement).first()

    if usuario is None:
        return None

    if not compare_digest(password, usuario.password):
        return None

    return usuario


def criar_token(usuario: Usuario) -> str:
    expiracao = datetime.now(timezone.utc) + timedelta(
        minutes=MINUTOS_EXPIRACAO
    )

    dados_token = {
        "sub": usuario.username,
        "user_id": usuario.id,
        "exp": expiracao,
    }

    return jwt.encode(
        dados_token,
        CHAVE_SECRETA,
        algorithm=ALGORITMO,
    )


def validar_token(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: Annotated[Session, Depends(get_session)],
) -> Usuario:

    erro_credenciais = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        dados_token = jwt.decode(
            token,
            CHAVE_SECRETA,
            algorithms=[ALGORITMO],
            options={"require": ["sub", "exp"]},
        )

    except InvalidTokenError as erro:
        raise erro_credenciais from erro

    username = dados_token.get("sub")

    if username is None:
        raise erro_credenciais

    statement = select(Usuario).where(
        Usuario.username == username
    )

    usuario = session.exec(statement).first()

    if usuario is None:
        raise erro_credenciais

    return usuario