""" Schemas para la predicción """

from enum import Enum

from pydantic import BaseModel


class Programa(str, Enum):
    CIVIL = "Civil"
    ELECTRICA = "Electrica"
    INDUSTRIAL = "Industrial"
    SISTEMAS = "Sistemas"

class PredictRequest(BaseModel):
    programa: Programa
    edad: int
    estrato: int
    promedio_anterior: float
    horas_estudio_semana: int
    asistencia_pct: int
    trabaja: bool

class PredictResponse(BaseModel):
    nota_final: float