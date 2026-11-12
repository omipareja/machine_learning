
import pickle

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import GridSearchCV, KFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

SEMILLA = 83


def load_data():
    """ Carga los datos desde un archivo CSV """
    df = pd.read_csv('app/data/rendimiento-estudiantes.csv')
    return df


def crear_pipeline(regresor=None, numericas=None, categoricas=None):
    """Preprocesamiento dentro del Pipeline: mediana, escalado y one-hot.

    El regresor entra como argumento para reutilizar el mismo preprocesamiento
    en la regresión múltiple y en Ridge. Cada llamada arma un Pipeline nuevo.
    """

    if regresor is None:
        regresor = LinearRegression()

    preprocesador = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline([
                    ("imputar", SimpleImputer(strategy="median")),
                    ("escalar", StandardScaler()),
                ]),
                numericas,
            ),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", drop="first"),
                categoricas,
            ),
        ]
    )
    return Pipeline([("preprocesar", preprocesador), ("regresor", regresor)])


def preprocess_data(datos):


    numericas = [
        "edad", "estrato", "promedio_anterior", "horas_estudio_semana",
        "asistencia_pct", "trabaja"
    ]
    categoricas = ["programa"]

    X = datos[numericas + categoricas]
    y = datos["nota_final"]

    X_train, _, y_train, _ = train_test_split(
        X, y, test_size=0.2, random_state=SEMILLA
    )

    modelo = crear_pipeline(numericas=numericas, categoricas=categoricas)
    modelo.fit(X_train, y_train)

    return modelo


def save_params(modelo):
    """ Guarda los parámetros del modelo en un archivo Pickle """
    with open('app/models/modelo.pkl', 'wb') as f:
        pickle.dump(modelo, f)



def load_model():
    """ Carga los parámetros del modelo desde un archivo Pickle """
    with open('app/models/modelo.pkl', 'rb') as f:
        modelo = pickle.load(f)
    return modelo
