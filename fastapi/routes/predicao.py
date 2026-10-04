from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from models.database import Prediction, Usuario, get_session
from models.predicao import (
    EntradaPredicao,
    PredictionPublica,
    SaidaPredicao,
)
from security.autenticacao import validar_token


router = APIRouter()


@router.post(
    "/predict",
    response_model=SaidaPredicao,
)
def prever_intencao(
        entrada: EntradaPredicao,
        usuario: Annotated[
            Usuario,
            Depends(validar_token)
        ],
        session: Annotated[
            Session,
            Depends(get_session)
        ],
):
    intencao = "Refund request"

    prediction = Prediction(
        texto=entrada.texto,
        intencao=intencao,
        owner_id=usuario.id,
    )

    session.add(prediction)
    session.commit()
    session.refresh(prediction)

    return SaidaPredicao(
        id=prediction.id,
        intencao=prediction.intencao,
    )


@router.get(
    "/predictions/{prediction_id}",
    response_model=PredictionPublica,
)
def obter_prediction(
        prediction_id: int,
        usuario: Annotated[
            Usuario,
            Depends(validar_token)
        ],
        session: Annotated[
            Session,
            Depends(get_session)
        ],
):
    prediction = session.get(
        Prediction,
        prediction_id,
    )

    if prediction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction não encontrada",
        )

    if prediction.owner_id != usuario.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction não encontrada",
        )

    return PredictionPublica(
        id=prediction.id,
        texto=prediction.texto,
        intencao=prediction.intencao,
    )
