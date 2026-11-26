# Modelado: aprendizaje automático tradicional

Los modelos operan sobre las 55 características de color y textura descritas en [`3_preparacion_datos/`](../../3_preparacion_datos). Se entrenan con la partición de entrenamiento (5.833 imágenes), se ajustan con validación cruzada estratificada de 5 particiones y la métrica de selección es el F1 macro, que pondera por igual las tres clases. La SVM, el Random Forest y la regresión logística usan ponderación de clases balanceada.

| Modelo | Justificación | Espacio de búsqueda | Mejor configuración | F1 macro en validación cruzada |
|---|---|---|---|---|
| SVM con kernel RBF y estandarización | Adecuado para pocas variables continuas y fronteras no lineales entre clases vecinas | $C \in \{1, 10, 100\}$, $\gamma \in \{\text{scale}, 0{,}01, 0{,}03\}$ (9 combinaciones) | $C = 100$, $\gamma = 0{,}03$ | 0,940 |
| Random Forest | Robusto al ruido y sin necesidad de escalar las variables | árboles $\in \{200, 400\}$, profundidad $\in \{\text{ilimitada}, 20\}$, hojas mínimas $\in \{1, 3\}$ (8 combinaciones) | 400 árboles, profundidad 20, 1 hoja mínima | 0,927 |
| Regresión logística (alternativa lineal) | Referencia lineal más simple: si queda cerca de la SVM, el kernel RBF no se justifica | $C \in \{0{,}01; 0{,}1; 1; 10; 100; 1000\}$ (6 combinaciones) | $C = 100$ | 0,727 |
| KNN (alternativa por similitud) | Referencia basada en vecindad, sin entrenamiento explícito | $k \in \{1, 3, 5, 11, 21\}$, pesos $\in \{\text{uniformes}, \text{distancia}\}$ (10 combinaciones) | $k = 1$, pesos uniformes | 0,932 |

La regresión logística y KNN usan las mismas características, estandarización y validación cruzada. Ayudan a justificar la elección: la regresión logística queda muy por debajo de la SVM (F1 macro de 0,73 frente a 0,95 en prueba), lo que indica que la frontera no es lineal en estas características. KNN con $k = 1$ iguala a los modelos clásicos en la prueba (0,94), pero acierta solo el 47 % de las fotos propias frente al 81 % de la SVM. La mejor $k$ de KNN es el extremo inferior de la rejilla.

El SVM es sensible a sus hiperparámetros (F1 entre 0,860 y 0,940 en la rejilla), mientras que el Random Forest casi no varía (entre 0,911 y 0,927). La mejor $C$ del SVM es el extremo superior de la rejilla, de modo que un valor mayor podría rendir algo más; no se exploró. Los resultados completos de la rejilla están en [`experiments/results/svm.json`](../../experiments/results/svm.json) y [`experiments/results/random_forest.json`](../../experiments/results/random_forest.json); los de las alternativas, en `regresion_logistica.json` y `knn.json` de la misma carpeta.

El SVM es determinista, pero el Random Forest puede dar resultados ligeramente distintos entre entornos con versiones diferentes de scikit-learn, aun con semilla fija.

```bash
python -m src.models.entrenar_ml
python -m src.models.entrenar_alternativas
```
