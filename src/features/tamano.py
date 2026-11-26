"""Estima el tamaño relativo de la fruta (pequeño, mediano, grande) con el diámetro normalizado de su máscara."""

import json
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

from src.data.segmentacion import cargar_imagen, segmentar_frutas

CATEGORIAS = ["pequeño", "mediano", "grande"]
RUTA_UMBRALES = Path("experiments/results/umbrales_tamano.json")


def diametro_normalizado(rgb):
    """Devuelve el diámetro normalizado de la fruta más grande (√(4A/π) sobre el lado menor) y su segmentación."""
    frutas = segmentar_frutas(rgb, descartar_borde=False, area_maxima=0.98)
    if not frutas:
        return None, None
    fruta = max(frutas, key=lambda f: f.area_fraccion)
    area = float((fruta.mascara > 0).sum())
    return float(np.sqrt(4 * area / np.pi) / min(rgb.shape[:2])), fruta


def categoria(d_norm, umbrales):
    """Devuelve la categoría de tamaño de un diámetro normalizado según los umbrales de la fruta."""
    return CATEGORIAS[int(np.searchsorted(umbrales, d_norm, side="right"))]


def _medir_archivo(ruta):
    d, _ = diametro_normalizado(cargar_cache(ruta))
    return d


def cargar_cache(ruta):
    """Lee una imagen del disco en RGB."""
    return cargar_imagen(Path(ruta))


def calcular_umbrales(indice, por_fruta=60, semilla=0):
    """Calcula por fruta los terciles del diámetro normalizado en entrenamiento y los guarda en JSON."""
    base = indice[indice["particion"] == "entrenamiento"]
    muestra = pd.concat(
        g.sample(min(len(g), por_fruta), random_state=semilla) for _, g in base.groupby("fruta")
    )
    with Pool(2) as pool:
        muestra = muestra.assign(d_norm=pool.map(_medir_archivo, muestra["ruta_absoluta"], chunksize=8))
    muestra = muestra.dropna(subset=["d_norm"])
    umbrales = {f: [float(q) for q in g["d_norm"].quantile([1 / 3, 2 / 3])] for f, g in muestra.groupby("fruta")}
    RUTA_UMBRALES.write_text(json.dumps({"umbrales": umbrales, "n": muestra.groupby("fruta").size().to_dict()}, indent=2))
    return muestra


if __name__ == "__main__":
    import time
    inicio = time.time()
    m = calcular_umbrales(pd.read_csv("data/processed/dataset.csv"), por_fruta=40)
    print(m.groupby("fruta")["d_norm"].describe().round(3), f"{time.time() - inicio:.0f}s")
