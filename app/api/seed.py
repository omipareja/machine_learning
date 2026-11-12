from fastapi import APIRouter, Request, Response
from app.utils.train_model import load_data, preprocess_data, save_params
import os

router = APIRouter()

@router.post('/train')
def create_seed(request: Request):
    """ Crea el modelo de regresión 
    """
    # Si el modelo ya existe, no se crea de nuevo
    if os.path.exists('app/models/modelo.pkl'):
        return {'message': 'Seed already created'}

    datos = load_data()
    modelo = preprocess_data(datos)
    save_params(modelo)
    return {'message': 'Seed created successfully'}






