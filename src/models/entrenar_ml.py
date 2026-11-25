import sys
import time

import joblib
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from src.data.preparar import cargar_dataset
from src.evaluation.metricas import evaluar, guardar
from src.features.caracteristicas import caracteristicas

INDICE = "data/processed/dataset.csv"
CACHE = "data/processed/arreglos_64"
SEMILLA = 0

MODELOS = {
    "svm": (
        make_pipeline(StandardScaler(), SVC(class_weight="balanced", random_state=SEMILLA)),
        {"svc__C": [1, 10, 100], "svc__gamma": ["scale", 0.01, 0.03]},
    ),
    "random_forest": (
        RandomForestClassifier(class_weight="balanced", random_state=SEMILLA, n_jobs=2),
        {"n_estimators": [200, 400], "max_depth": [None, 20], "min_samples_leaf": [1, 3]},
    ),
}


if __name__ == "__main__":
    indice = pd.read_csv(INDICE)
    X = caracteristicas(cargar_dataset(indice, CACHE))
    entrenamiento = (indice["particion"] == "entrenamiento").to_numpy()
    y = indice["calidad"].to_numpy()
    cv = StratifiedKFold(5, shuffle=True, random_state=SEMILLA)

    linea_base = DummyClassifier(strategy="most_frequent").fit(X[entrenamiento], y[entrenamiento])
    guardar(evaluar(linea_base.predict, X, indice), "experiments/results/linea_base.json")

    for nombre in sys.argv[1:] or MODELOS:
        modelo, rejilla = MODELOS[nombre]
        inicio = time.time()
        busqueda = GridSearchCV(modelo, rejilla, scoring="f1_macro", cv=cv, n_jobs=2)
        busqueda.fit(X[entrenamiento], y[entrenamiento])
        resultados = evaluar(busqueda.predict, X, indice)
        resultados["mejores_hiperparametros"] = {k: str(v) for k, v in busqueda.best_params_.items()}
        resultados["f1_macro_cv"] = float(busqueda.best_score_)
        resultados["rejilla"] = [
            {"parametros": {k: str(v) for k, v in p.items()}, "f1_macro_cv": float(m), "desv": float(s)}
            for p, m, s in zip(
                busqueda.cv_results_["params"], busqueda.cv_results_["mean_test_score"], busqueda.cv_results_["std_test_score"]
            )
        ]
        guardar(resultados, f"experiments/results/{nombre}.json")
        joblib.dump(busqueda.best_estimator_, f"experiments/checkpoints/{nombre}.joblib")
        print(nombre, busqueda.best_params_, round(busqueda.best_score_, 3),
              "prueba f1:", round(resultados["prueba"]["f1_macro"], 3),
              "propias acc:", round(resultados["propias"]["exactitud"], 3), f"{time.time() - inicio:.0f}s", flush=True)
