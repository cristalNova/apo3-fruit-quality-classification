"""Descarga el conjunto de Kaggle Fruit Quality Classification en data/raw."""

import os
from pathlib import Path

os.environ["KAGGLEHUB_CACHE"] = str(Path(__file__).resolve().parents[2] / "data" / "raw")

import kagglehub

ruta = kagglehub.dataset_download("ryandpark/fruit-quality-classification/versions/1")
print(ruta)
