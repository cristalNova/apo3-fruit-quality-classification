"""Entrena una configuración de la CNN con punto de control y detención temprana, la evalúa y conserva la mejor."""

import json
import shutil
import sys
import time
from pathlib import Path

import keras
import numpy as np
import pandas as pd
from sklearn.utils.class_weight import compute_class_weight

from src.data.preparar import cargar_dataset
from src.evaluation.metricas import evaluar, guardar
from src.models.cnn import CLASES, construir_cnn

CONFIGURACIONES = [
    {"filtros": 16, "dropout": 0.3, "lr": 1e-3},
    {"filtros": 32, "dropout": 0.3, "lr": 1e-3},
    {"filtros": 32, "dropout": 0.5, "lr": 3e-4},
]
SEMILLA = 0
PACIENCIA = 8
EPOCAS_MINIMAS = 12


class PuntoDeControl(keras.callbacks.Callback):
    """Callback que guarda la historia y el estado en cada época y detiene el entrenamiento por paciencia o por tiempo."""

    def __init__(self, historia, ruta_historia, ruta_estado, ruta_mejor, segundos):
        super().__init__()
        self.historia, self.ruta_historia, self.ruta_estado, self.ruta_mejor = historia, ruta_historia, ruta_estado, ruta_mejor
        self.limite = time.time() + segundos
        self.paciencia_agotada = False

    def on_epoch_end(self, epoch, logs=None):
        for k, v in logs.items():
            self.historia.setdefault(k, []).append(float(v))
        perdidas = self.historia["val_loss"]
        if perdidas[-1] <= min(perdidas):
            self.model.save_weights(self.ruta_mejor)
        self.model.save(self.ruta_estado)
        self.ruta_historia.write_text(json.dumps(self.historia))
        sin_mejora = len(perdidas) - 1 - int(np.argmin(perdidas))
        self.paciencia_agotada = len(perdidas) >= EPOCAS_MINIMAS and sin_mejora >= PACIENCIA
        if self.paciencia_agotada or time.time() > self.limite:
            self.model.stop_training = True


def predecir_etiquetas(modelo):
    """Devuelve una función que predice las etiquetas de calidad con el modelo."""
    return lambda X: np.array(CLASES)[modelo.predict(X, verbose=0).argmax(1)]


if __name__ == "__main__":
    i = int(sys.argv[1])
    epocas = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    segundos = int(sys.argv[3]) if len(sys.argv) > 3 else 100000
    config = CONFIGURACIONES[i]
    keras.utils.set_random_seed(SEMILLA)

    logs = Path("experiments/logs")
    logs.mkdir(parents=True, exist_ok=True)
    ruta_historia, ruta_estado, ruta_mejor = logs / f"cnn_{i}_historia.json", logs / f"cnn_{i}_estado.keras", logs / f"cnn_{i}_mejor.weights.h5"

    indice = pd.read_csv("data/processed/dataset.csv")
    X = cargar_dataset(indice, "data/processed/arreglos_64")
    y = indice["calidad"].map(CLASES.index).to_numpy()
    entrenamiento = (indice["particion"] == "entrenamiento").to_numpy()
    validacion = (indice["particion"] == "validacion").to_numpy()
    pesos = compute_class_weight("balanced", classes=np.arange(3), y=y[entrenamiento])

    reiniciar = len(sys.argv) > 4 and sys.argv[4] == "reiniciar"
    if ruta_estado.exists() and not reiniciar:
        modelo = keras.models.load_model(ruta_estado)
        historia = json.loads(ruta_historia.read_text())
    else:
        modelo = construir_cnn(config["filtros"], config["dropout"])
        modelo.compile(keras.optimizers.Adam(config["lr"]), "sparse_categorical_crossentropy", metrics=["accuracy"])
        historia = {}

    hechas = len(historia.get("loss", []))
    punto = PuntoDeControl(historia, ruta_historia, ruta_estado, ruta_mejor, segundos)
    if hechas < epocas:
        modelo.fit(
            X[entrenamiento], y[entrenamiento], validation_data=(X[validacion], y[validacion]),
            initial_epoch=hechas, epochs=epocas, batch_size=64, class_weight=dict(enumerate(pesos)),
            verbose=2, callbacks=[punto],
        )
    terminado = punto.paciencia_agotada or len(historia["loss"]) >= epocas or hechas >= epocas
    if not terminado:
        print("config", i, "epocas hechas:", len(historia["loss"]), "-> continuar")
        sys.exit(0)

    modelo.load_weights(ruta_mejor)
    resultados = evaluar(predecir_etiquetas(modelo), X, indice)
    resultados.update(
        configuracion=config, epocas=len(historia["loss"]), historia=historia, parametros=int(modelo.count_params()),
        mejor_epoca=int(np.argmin(historia["val_loss"])) + 1,
    )
    guardar(resultados, f"experiments/results/cnn_{i}.json")
    modelo.save(f"experiments/checkpoints/cnn_{i}.keras")

    mejor = Path("experiments/results/cnn.json")
    if not mejor.exists() or json.loads(mejor.read_text())["validacion"]["f1_macro"] < resultados["validacion"]["f1_macro"]:
        shutil.copy(f"experiments/results/cnn_{i}.json", mejor)
        shutil.copy(f"experiments/checkpoints/cnn_{i}.keras", "experiments/checkpoints/cnn.keras")
    print("config", i, "TERMINADA val f1", round(resultados["validacion"]["f1_macro"], 3),
          "prueba f1", round(resultados["prueba"]["f1_macro"], 3), "propias acc", round(resultados["propias"]["exactitud"], 3))
