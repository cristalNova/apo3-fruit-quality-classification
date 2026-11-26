"""Segmenta una foto y devuelve la calidad (CNN y SVM) y el tamaño de la fruta para la aplicación."""

import json
from functools import lru_cache

import cv2
import joblib
import keras
import numpy as np

from src.data.segmentacion import recortar_fruta, segmentar_frutas
from src.features.caracteristicas import caracteristicas
from src.features.tamano import RUTA_UMBRALES, categoria
from src.models.cnn import CLASES

LADO = 64
BRILLO_FONDO_CLARO = 180


def brillo_minimo(rgb):
    """Devuelve 0 (sin filtro de brillo) si el borde de la foto es claro y 90 en caso contrario."""
    borde = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
    return 0.0 if borde.max(axis=1).mean() >= BRILLO_FONDO_CLARO else 90.0


def segmentar(rgb):
    """Devuelve el diámetro normalizado y la segmentación de la fruta más grande, o (None, None) si no hay."""
    frutas = segmentar_frutas(rgb, descartar_borde=False, area_maxima=0.98, brillo_minimo=brillo_minimo(rgb))
    if not frutas:
        return None, None
    fruta = max(frutas, key=lambda f: f.area_fraccion)
    area = float((fruta.mascara > 0).sum())
    return float(np.sqrt(4 * area / np.pi) / min(rgb.shape[:2])), fruta


@lru_cache(maxsize=1)
def cargar_modelos():
    """Carga la CNN y la SVM guardadas."""
    return keras.models.load_model("experiments/checkpoints/cnn.keras"), joblib.load("experiments/checkpoints/svm.joblib")


def analizar(rgb, fruta):
    """Segmenta la fruta y estima su calidad con la CNN y la SVM y su tamaño con los umbrales de la fruta."""
    d_norm, segmentada = segmentar(rgb)
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
