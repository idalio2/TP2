from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from models.autenticacao import Token
from models.database import get_session
from security.autenticacao import autenticar_usuario, criar_token
from security.rate_limit import limiter


router = APIRouter()


@router.post("/auth/token", response_model=Token)
@limiter.limit("10/minute")
def gerar_token(
        request: Request,
        formulario: Annotated[
            OAuth2PasswordRequestForm,
            Depends()
        ],
        session: Annotated[
            Session,
            Depends(get_session)
        ],
):
    usuario = autenticar_usuario(
        formulario.username,
        formulario.password,
        session,
    )

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = criar_token(usuario)

    return Token(
        access_token=token,
        token_type="bearer",
    )