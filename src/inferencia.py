import json
from functools import lru_cache

import cv2
import joblib
import keras
import numpy as np

from src.data.segmentacion import recortar_fruta
from src.features.caracteristicas import caracteristicas
from src.features.tamano import RUTA_UMBRALES, categoria, diametro_normalizado
from src.models.cnn import CLASES

LADO = 64


@lru_cache(maxsize=1)
def cargar_modelos():
    return keras.models.load_model("experiments/checkpoints/cnn.keras"), joblib.load("experiments/checkpoints/svm.joblib")


def analizar(rgb, fruta):
    d_norm, segmentada = diametro_normalizado(rgb)
    recorte = recortar_fruta(rgb, segmentada, lado_max=256) if segmentada else rgb
    entrada = cv2.resize(recorte, (LADO, LADO), interpolation=cv2.INTER_LINEAR)[None]

    cnn, svm = cargar_modelos()
    probabilidades = cnn.predict(entrada, verbose=0)[0]
    umbrales = json.loads(RUTA_UMBRALES.read_text())["umbrales"][fruta]
    return {
        "recorte": recorte,
        "segmentada": segmentada is not None,
        "calidad_cnn": CLASES[int(probabilidades.argmax())],
        "probabilidades": dict(zip(CLASES, probabilidades.astype(float))),
        "calidad_svm": str(svm.predict(caracteristicas(entrada))[0]),
        "diametro_normalizado": d_norm,
        "tamano": categoria(d_norm, umbrales) if d_norm is not None else None,
    }
