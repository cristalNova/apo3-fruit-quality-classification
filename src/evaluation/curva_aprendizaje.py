"""Curva de aprendizaje de la SVM: F1 macro en prueba y en fotos propias según el tamaño del entrenamiento."""

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from src.data.preparar import cargar_dataset
from src.evaluation.metricas import resumen
from src.features.caracteristicas import caracteristicas

FRACCIONES = [0.05, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0]
REPETICIONES = 5
SALIDA = "experiments/results/curva_aprendizaje"


if __name__ == "__main__":
    indice = pd.read_csv("data/processed/dataset.csv")
    X = caracteristicas(cargar_dataset(indice, "data/processed/arreglos_64"))
    y = indice["calidad"].to_numpy()
    estrato = (indice["fruta"] + "_" + indice["calidad"]).to_numpy()
    mejores = json.load(open("experiments/results/svm.json", encoding="utf-8"))["mejores_hiperparametros"]
    C, gamma = float(mejores["svc__C"]), float(mejores["svc__gamma"])

    entrenamiento = (indice["particion"] == "entrenamiento").to_numpy().nonzero()[0]
    evaluacion = {p: (indice["particion"] == p).to_numpy() for p in ("validacion", "prueba", "propias")}

    filas = []
    for fraccion in FRACCIONES:
        for semilla in range(REPETICIONES if fraccion < 1 else 1):
            if fraccion < 1:
                elegidas = train_test_split(entrenamiento, train_size=fraccion, stratify=estrato[entrenamiento], random_state=semilla)[0]
            else:
                elegidas = entrenamiento
            modelo = make_pipeline(StandardScaler(), SVC(C=C, gamma=gamma, class_weight="balanced"))
            modelo.fit(X[elegidas], y[elegidas])
            fila = {"fraccion": fraccion, "n": len(elegidas), "semilla": semilla}
            for nombre, mascara in evaluacion.items():
                r = resumen(y[mascara], modelo.predict(X[mascara]))
                fila[f"{nombre}_f1"], fila[f"{nombre}_exactitud"] = r["f1_macro"], r["exactitud"]
            filas.append(fila)
    curva = pd.DataFrame(filas)
    curva.to_csv(f"{SALIDA}.csv", index=False)

    resumen_n = curva.groupby("n").agg(
        prueba=("prueba_f1", "mean"), prueba_sd=("prueba_f1", "std"),
        propias=("propias_f1", "mean"), propias_sd=("propias_f1", "std"),
    ).reset_index()
    fig, ax = plt.subplots(figsize=(6.6, 3.6))
    ax.errorbar(resumen_n["n"], resumen_n["prueba"], yerr=resumen_n["prueba_sd"], marker="o", capsize=2, color="#4C78A8", label="Prueba (misma distribución)")
    ax.errorbar(resumen_n["n"], resumen_n["propias"], yerr=resumen_n["propias_sd"], marker="s", capsize=2, color="#E15759", label="Fotos propias (externo)")
    ax.axvline(len(entrenamiento), ls="--", lw=1, color="#999")
    ax.text(len(entrenamiento) - 100, 0.08, f"entrenamiento actual ({len(entrenamiento):,})".replace(",", "."), fontsize=7, color="#666", ha="right")
    ax.set(xlabel="Imágenes de entrenamiento", ylabel="F1 macro (SVM)", ylim=(0, 1.02))
    ax.legend(frameon=False, fontsize=8, loc="center", bbox_to_anchor=(0.55, 0.68))
    ax.spines[["top", "right"]].set_visible(False)
    for extension in ("svg", "pdf"):
        fig.savefig(f"{SALIDA}.{extension}", bbox_inches="tight")

    print(resumen_n.round(3).to_string(index=False))
