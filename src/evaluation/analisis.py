"""Genera predicciones, tabla resumen y figuras de comparación de modelos a partir de los resultados guardados."""

import json
from pathlib import Path

import joblib
import keras
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

from src.data.preparar import cargar_dataset
from src.features.caracteristicas import caracteristicas
from src.models.cnn import CLASES

RESULTADOS = Path("experiments/results")
NOMBRES = {"linea_base": "Línea base", "svm": "SVM", "random_forest": "Random Forest", "cnn": "CNN"}
COLORES = {"linea_base": "#B9B9B9", "svm": "#4C78A8", "random_forest": "#59A14F", "cnn": "#E15759"}
PARTICIONES = [("prueba", "Prueba"), ("prueba_kaggle", "Prueba Kaggle"), ("prueba_companeros", "Prueba compañeros"), ("prueba_drive2", "Prueba fotos adicionales"), ("propias", "Fotos propias")]


def resultados_modelo(modelo):
    """Lee el JSON de resultados de un modelo."""
    return json.loads((RESULTADOS / f"{modelo}.json").read_text())


def guardar(fig, nombre):
    """Guarda la figura en SVG y PDF."""
    for ext in ("svg", "pdf"):
        fig.savefig(RESULTADOS / f"{nombre}.{ext}", bbox_inches="tight")
    plt.close(fig)


def predicciones(indice):
    """Predice la calidad de cada imagen del índice con la SVM, el Random Forest, la CNN y la línea base."""
    imagenes = cargar_dataset(indice, "data/processed/arreglos_64")
    X = caracteristicas(imagenes)
    salida = indice[["origen", "fruta", "calidad", "particion", "archivo"]].copy()
    for nombre in ("svm", "random_forest"):
        salida[nombre] = joblib.load(f"experiments/checkpoints/{nombre}.joblib").predict(X)
    cnn = keras.models.load_model("experiments/checkpoints/cnn.keras")
    salida["cnn"] = np.array(CLASES)[cnn.predict(imagenes, verbose=0).argmax(1)]
    salida["linea_base"] = "buena"
    return salida


def figura_comparacion():
    """F1 macro de cada modelo por conjunto de evaluación."""
    fig, ax = plt.subplots(figsize=(9.5, 3.6))
    ancho = 0.2
    for i, modelo in enumerate(NOMBRES):
        r = resultados_modelo(modelo)
        valores = [r[p]["f1_macro"] for p, _ in PARTICIONES]
        barras = ax.bar(np.arange(len(PARTICIONES)) + (i - 1.5) * ancho, valores, ancho, label=NOMBRES[modelo], color=COLORES[modelo])
        ax.bar_label(barras, fmt="%.2f", fontsize=7, padding=1)
    ax.set_xticks(range(len(PARTICIONES)), [n.replace(" ", "\n", 1) for _, n in PARTICIONES])
    ax.set(ylabel="F1 macro", ylim=(0, 1.12))
    ax.legend(ncol=4, loc="upper center", fontsize=8, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    guardar(fig, "comparacion_modelos")


def figura_confusion(pred):
    """Matrices de confusión de la SVM y la CNN en prueba y en fotos propias."""
    modelos = ["svm", "cnn"]
    fig, ejes = plt.subplots(2, 2, figsize=(7, 6))
    for fila, modelo in enumerate(modelos):
        for col, (particion, titulo) in enumerate([("prueba", "Prueba"), ("propias", "Fotos propias")]):
            sub = pred[pred["particion"] == particion]
            m = confusion_matrix(sub["calidad"], sub[modelo], labels=CLASES)
            normalizada = m / np.maximum(m.sum(1, keepdims=True), 1)
            ax = ejes[fila, col]
            ax.imshow(normalizada, cmap="Blues", vmin=0, vmax=1)
            for i in range(3):
                for j in range(3):
                    ax.text(j, i, m[i, j], ha="center", va="center", color="white" if normalizada[i, j] > 0.5 else "black", fontsize=9)
            ax.set_xticks(range(3), CLASES, fontsize=8)
            ax.set_yticks(range(3), CLASES, fontsize=8)
            ax.set(title=f"{NOMBRES[modelo]} - {titulo}", xlabel="Predicha", ylabel="Real")
    fig.tight_layout()
    guardar(fig, "matrices_confusion")


def figura_curvas_cnn():
    """Curvas de pérdida y exactitud de las tres configuraciones de la CNN."""
    fig, ejes = plt.subplots(1, 2, figsize=(9, 3.4))
    for i in range(3):
        r = json.loads((RESULTADOS / f"cnn_{i}.json").read_text())
        c, h = r["configuracion"], r["historia"]
        etiqueta = f"{c['filtros']} filtros, dropout {c['dropout']}, lr {c['lr']}"
        epocas = range(1, len(h["loss"]) + 1)
        ejes[0].plot(epocas, h["loss"], color=f"C{i}", label=etiqueta)
        ejes[0].plot(epocas, h["val_loss"], color=f"C{i}", ls="--")
        ejes[1].plot(epocas, h["accuracy"], color=f"C{i}")
        ejes[1].plot(epocas, h["val_accuracy"], color=f"C{i}", ls="--")
    ejes[0].set(title="Pérdida (continua: entrenamiento, discontinua: validación)", xlabel="Época", ylim=(0, 1.3))
    ejes[1].set(title="Exactitud", xlabel="Época", ylim=(0.4, 1))
    ejes[0].legend(fontsize=7, frameon=False)
    for ax in ejes:
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    guardar(fig, "curvas_cnn")


def figura_por_fruta(pred):
    """Exactitud por fruta en prueba y en fotos propias."""
    fig, ejes = plt.subplots(1, 2, figsize=(9, 3.4), sharey=True)
    for ax, (particion, titulo) in zip(ejes, [("prueba", "Prueba"), ("propias", "Fotos propias")]):
        sub = pred[pred["particion"] == particion]
        frutas = [f for f in ["manzana", "banano", "guayaba", "limon", "naranja", "granada"] if f in set(sub["fruta"])]
        for i, modelo in enumerate(["svm", "random_forest", "cnn"]):
            exactitud = [(sub.loc[sub["fruta"] == f, modelo] == sub.loc[sub["fruta"] == f, "calidad"]).mean() for f in frutas]
            ax.bar(np.arange(len(frutas)) + (i - 1) * 0.27, exactitud, 0.27, label=NOMBRES[modelo], color=COLORES[modelo])
        ax.set_xticks(range(len(frutas)), frutas, fontsize=8)
        ax.set(title=titulo, ylim=(0, 1.2))
        ax.spines[["top", "right"]].set_visible(False)
    ejes[0].set_ylabel("Exactitud")
    ejes[0].legend(fontsize=8, frameon=False, loc="upper center", ncol=3)
    fig.tight_layout()
    guardar(fig, "exactitud_por_fruta")


def tabla_resumen():
    """Guarda en CSV la exactitud y el F1 macro de cada modelo por conjunto."""
    filas = []
    for modelo in NOMBRES:
        r = resultados_modelo(modelo)
        for p, titulo in PARTICIONES + [("validacion", "Validación")]:
            filas.append({"modelo": NOMBRES[modelo], "conjunto": titulo, "n": r[p]["n"],
                          "exactitud": round(r[p]["exactitud"], 3), "f1_macro": round(r[p]["f1_macro"], 3)})
    pd.DataFrame(filas).to_csv(RESULTADOS / "resumen.csv", index=False)


if __name__ == "__main__":
    indice = pd.read_csv("data/processed/dataset.csv")
    pred = predicciones(indice)
    pred.to_csv(RESULTADOS / "predicciones.csv", index=False)
    tabla_resumen()
    figura_comparacion()
    figura_confusion(pred)
    figura_curvas_cnn()
    figura_por_fruta(pred)
    propias = pred[pred["particion"] == "propias"]
    for modelo in ("svm", "random_forest", "cnn"):
        print(modelo, propias.assign(ok=propias[modelo] == propias["calidad"]).groupby(["fruta", "calidad"])["ok"].agg(["mean", "size"]).round(2).to_dict("index"))
