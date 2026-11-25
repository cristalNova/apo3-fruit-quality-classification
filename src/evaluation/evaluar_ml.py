import json
import sys

import joblib
import pandas as pd

from src.data.preparar import cargar_dataset
from src.evaluation.metricas import evaluar, guardar
from src.features.caracteristicas import caracteristicas

if __name__ == "__main__":
    indice = pd.read_csv("data/processed/dataset.csv")
    X = caracteristicas(cargar_dataset(indice, "data/processed/arreglos_64"))
    for nombre in sys.argv[1:]:
        ruta = f"experiments/results/{nombre}.json"
        previo = json.load(open(ruta, encoding="utf-8"))
        modelo = joblib.load(f"experiments/checkpoints/{nombre}.joblib")
        previo.update(evaluar(modelo.predict, X, indice))
        guardar(previo, ruta)
