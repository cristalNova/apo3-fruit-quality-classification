"""Métricas de clasificación (exactitud, F1 macro, matriz de confusión) por partición y origen, y su guardado en JSON."""

import json
from pathlib import Path

import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

CLASES = ["buena", "regular", "mala"]
ORIGENES_PRUEBA = ("kaggle", "companeros", "drive2")


def resumen(y_real, y_pred):
    """Calcula exactitud, F1 macro, métricas por clase y matriz de confusión."""
    presentes = [c for c in CLASES if c in set(y_real)]
    informe = classification_report(y_real, y_pred, labels=CLASES, output_dict=True, zero_division=0)
    return {
        "n": int(len(y_real)),
        "exactitud": float(accuracy_score(y_real, y_pred)),
        "f1_macro": float(f1_score(y_real, y_pred, labels=presentes, average="macro", zero_division=0)),
        "por_clase": {c: {k: float(informe[c][k]) for k in ("precision", "recall", "f1-score", "support")} for c in CLASES},
        "matriz_confusion": confusion_matrix(y_real, y_pred, labels=CLASES).tolist(),
    }


def evaluar(modelo_predice, X, indice, particiones=("validacion", "prueba", "propias")):
    """Evalúa un modelo en validación, prueba (total y por origen) y fotos propias."""
    resultados = {}
    for particion in particiones:
        mascara = (indice["particion"] == particion).to_numpy()
        y_real = indice.loc[mascara, "calidad"].to_numpy()
        y_pred = modelo_predice(X[mascara])
        resultados[particion] = resumen(y_real, y_pred)
        if particion == "prueba":
            for origen in ORIGENES_PRUEBA:
                sub = (indice.loc[mascara, "origen"] == origen).to_numpy()
                resultados[f"prueba_{origen}"] = resumen(y_real[sub], y_pred[sub])
    return resultados


def guardar(resultados, ruta):
    """Guarda resultados en un archivo JSON."""
    Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    Path(ruta).write_text(json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8")
