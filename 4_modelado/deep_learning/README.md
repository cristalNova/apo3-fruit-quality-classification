# Modelado: aprendizaje profundo

La red convolucional se entrena desde cero, sin pesos preentrenados, con imágenes RGB de 64 × 64 píxeles. Su definición está en [`src/models/cnn.py`](../../src/models/cnn.py).

## Arquitectura

Reescalado de los valores a $[0, 1]$; capas de aumento de datos activas solo en entrenamiento (giro horizontal y vertical, rotación de hasta ±36°, brillo de ±40 % y contraste de ±30 %); tres bloques de convolución 3 × 3, normalización por lotes y agrupación máxima, con $f$, $2f$ y $4f$ filtros; agrupación promedio global; dropout; capa densa de 64 unidades; y capa de salida softmax de tres clases. Se minimiza la entropía cruzada ponderada por clase con el optimizador Adam y lotes de 64 imágenes.

## Ajuste de hiperparámetros

Se exploran tres configuraciones, hasta 40 épocas. La detención temprana usa la pérdida de validación con paciencia de 4 épocas, aplicable a partir de la época 12 porque la pérdida de validación es inestable al inicio, y se restauran los pesos de la mejor época. Ninguna configuración alcanzó el máximo: se detuvieron en las épocas 17, 19 y 17. La pérdida de validación oscila entre épocas, de modo que la detención temprana se activa pronto y la red puede quedar poco entrenada (la exactitud de entrenamiento seguía subiendo); una paciencia mayor podría mejorarla y no se probó.

| Filtros base | Dropout | Tasa de aprendizaje | Parámetros | Mejor época | F1 macro en validación |
|---|---|---|---|---|---|
| 16 | 0,3 | $10^{-3}$ | 28.387 | 13 | 0,819 |
| **32** | **0,3** | $\mathbf{10^{-3}}$ | **102.595** | **15** | **0,848** |
| 32 | 0,5 | $3 \times 10^{-4}$ | 102.595 | 13 | 0,817 |

Se selecciona la segunda configuración por el mayor F1 macro de validación. Las curvas de entrenamiento y validación están en [`experiments/results/curvas_cnn.svg`](../../experiments/results/curvas_cnn.svg). La configuración seleccionada supera a las otras dos por 3 puntos de F1 macro de validación; la primera (menos filtros) y la tercera (más dropout y menor tasa de aprendizaje) quedan prácticamente empatadas. Como la validación oscila entre épocas, estas diferencias son pequeñas frente a esa variación.

```bash
python -m src.models.entrenar_cnn 0   # y 1, 2; reanuda si se interrumpe (borrar experiments/logs para empezar de cero)
```
