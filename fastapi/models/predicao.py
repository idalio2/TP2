from pydantic import BaseModel, ConfigDict, Field


class EntradaPredicao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    texto: str = Field(min_length=1)


class SaidaPredicao(BaseModel):
    id: int
    intencao: str


class PredictionPublica(BaseModel):
    id: int
    texto: str
    intencao: str