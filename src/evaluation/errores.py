"""Dibuja las fotos propias mal clasificadas: las 10 regulares y una muestra de buenas que falla la CNN, con la predicción de la SVM y la CNN."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.data.preparar import cargar_dataset

RESULTADOS = Path("experiments/results")
COLUMNAS = 10


def celda(ax, imagen, fruta, svm, cnn):
    """Dibuja una imagen con su fruta y las predicciones de la SVM y la CNN."""
    ax.imshow(imagen)
    ax.set_title(fruta, fontsize=6, pad=1.5)
    ax.set_xlabel(f"SVM: {svm}\nCNN: {cnn}", fontsize=5.5, labelpad=2)
    ax.set_xticks([])
    ax.set_yticks([])


if __name__ == "__main__":
    indice = pd.read_csv("data/processed/dataset.csv")
    pred = pd.read_csv(RESULTADOS / "predicciones.csv")
    imagenes = cargar_dataset(indice, "data/processed/arreglos_64")
    propias = pred["particion"] == "propias"
    regulares = pred[propias & (pred["calidad"] == "regular")]
    buenas = pred[propias & (pred["calidad"] == "buena") & (pred["cnn"] != "buena")]
    buenas = buenas.sample(COLUMNAS, random_state=0).sort_values("fruta")

    fig, ejes = plt.subplots(2, COLUMNAS, figsize=(7.2, 3.1))
    titulos = []
    for fila, (grupo, titulo) in enumerate([(regulares, f"Regulares ({len(regulares)} de {len(regulares)})"),
                                            (buenas, f"Buenas que falla la CNN ({COLUMNAS} al azar de {(propias & (pred['calidad'] == 'buena') & (pred['cnn'] != 'buena')).sum()})")]):
        for ax, (i, f) in zip(ejes[fila], grupo.iterrows()):
            celda(ax, imagenes[i], f["fruta"], f["svm"], f["cnn"])
        titulos.append(titulo)
    fig.tight_layout(h_pad=2.2, w_pad=0.3, rect=(0, 0, 1, 0.94))
    for fila, titulo in enumerate(titulos):
        caja = ejes[fila, 0].get_position()
        fig.text(caja.x0, caja.y1 + 0.055, titulo, fontsize=7, fontweight="bold")
    for ext in ("svg", "pdf"):
        fig.savefig(RESULTADOS / f"errores_fotos_propias.{ext}", bbox_inches="tight")
