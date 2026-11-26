# 4. Modelado

Esta fase entrena, ajusta y selecciona los modelos de clasificación de calidad. Se desarrollan dos modelos de aprendizaje automático tradicional sobre las características extraídas (SVM y Random Forest) y una red neuronal convolucional entrenada desde cero. Todos reciben las mismas particiones y se comparan con una línea base que predice siempre la clase mayoritaria.

| Carpeta | Contenido |
|---|---|
| [`ml_tradicional/`](ml_tradicional) | SVM y Random Forest con búsqueda en rejilla y validación cruzada, más regresión logística y KNN como alternativas simples |
| [`deep_learning/`](deep_learning) | Red convolucional pequeña, ajuste de hiperparámetros y curvas de entrenamiento |

El código se encuentra en [`src/models`](../src/models). Los modelos finales se guardan en `experiments/checkpoints/` y las métricas en `experiments/results/`.

## Resumen de resultados

| Modelo | F1 macro en validación | F1 macro en prueba | Exactitud en fotos propias | F1 macro en fotos propias |
|---|---|---|---|---|
| Línea base (clase mayoritaria) | 0,23 | 0,23 | 0,91 | 0,48 |
| SVM (kernel RBF) | 0,95 | 0,95 | 0,81 | 0,45 |
| Random Forest | 0,94 | 0,94 | 0,64 | 0,39 |
| KNN (k = 1) | 0,95 | 0,94 | 0,47 | 0,40 |
| Regresión logística | 0,72 | 0,73 | 0,48 | 0,37 |
| CNN | 0,91 | 0,91 | 0,58 | 0,37 |

El análisis completo está en [`5_evaluacion/`](../5_evaluacion).
