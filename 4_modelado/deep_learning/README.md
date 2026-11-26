# Modelado: aprendizaje profundo

La red convolucional se entrena desde cero, sin pesos preentrenados, con imágenes RGB de 64 × 64 píxeles. Su definición está en [`src/models/cnn.py`](../../src/models/cnn.py).

## Arquitectura

Reescalado de los valores a $[0, 1]$; capas de aumento de datos activas solo en entrenamiento (giro horizontal y vertical, rotación de hasta ±36°, brillo de ±40 % y contraste de ±30 %); tres bloques de convolución 3 × 3, normalización por lotes y agrupación máxima, con $f$, $2f$ y $4f$ filtros; agrupación promedio global; dropout; capa densa de 64 unidades; y capa de salida softmax de tres clases. Se minimiza la entropía cruzada ponderada por clase con el optimizador Adam y lotes de 64 imágenes.

## Ajuste de hiperparámetros

Se exploran tres configuraciones, hasta 80 épocas. La detención temprana usa la pérdida de validación con paciencia de 8 épocas, aplicable a partir de la época 12 porque la pérdida de validación es inestable al inicio, y se restauran los pesos de la mejor época. Ninguna configuración llegó al máximo: se detuvieron en las épocas 41, 48 y 21. Una primera ejecución con paciencia de 4 épocas y tope de 40 las paraba en las épocas 17, 19 y 17 con la exactitud de entrenamiento todavía subiendo, por lo que se repitió con paciencia de 8 (comparación más abajo).

| Filtros base | Dropout | Tasa de aprendizaje | Parámetros | Mejor época | F1 macro en validación |
|---|---|---|---|---|---|
| 16 | 0,3 | $10^{-3}$ | 28.387 | 33 | 0,892 |
| **32** | **0,3** | $\mathbf{10^{-3}}$ | **102.595** | **40** | **0,912** |
| 32 | 0,5 | $3 \times 10^{-4}$ | 102.595 | 13 | 0,817 |

Se selecciona la segunda configuración por el mayor F1 macro de validación. Las curvas de entrenamiento y validación están en [`experiments/results/curvas_cnn.svg`](../../experiments/results/curvas_cnn.svg). La configuración seleccionada supera por 2 puntos de F1 macro de validación a la de 16 filtros y por 9,5 a la de más dropout y menor tasa de aprendizaje, que se detiene en la época 21 con su mejor época en la 13. En la mejor época de la seleccionada la exactitud es de 0,919 en entrenamiento y 0,932 en validación, de modo que no hay sobreajuste (el aumento de datos y el dropout actúan solo en entrenamiento).

## Comparación de la paciencia

| Configuración | Paciencia 4: parada / F1 validación / F1 prueba | Paciencia 8: parada / F1 validación / F1 prueba |
|---|---|---|
| 16 filtros, dropout 0,3, $10^{-3}$ | 17 / 0,819 / 0,815 | 41 / 0,892 / 0,887 |
| 32 filtros, dropout 0,3, $10^{-3}$ | 19 / 0,848 / 0,829 | 48 / 0,912 / 0,910 |
| 32 filtros, dropout 0,5, $3 \times 10^{-4}$ | 17 / 0,817 / 0,836 | 21 / 0,817 / 0,836 |

Con paciencia de 8, las dos primeras configuraciones mejoran entre 6 y 7 puntos de F1 macro en validación y entre 7 y 8 en prueba, y la tercera no cambia porque su mejor época sigue siendo la 13. La configuración seleccionada es la misma en ambos casos. En cambio, la exactitud en las fotos propias no mejora: pasa de 0,43, 0,70 y 0,61 a 0,65, 0,58 y 0,61 (la seleccionada baja de 0,70 a 0,58 y su F1 macro de 0,57 a 0,37), de modo que entrenar más mejora el desempeño en distribución sin trasladarlo a fotos de otra fuente; con 106 imágenes esas diferencias son pequeñas frente a la variación entre configuraciones. Subir el tope de 40 a 80 épocas no cambia las métricas. Los resultados de cada ejecución están en `experiments/results/paciencia_4_tope_40/` y `experiments/results/paciencia_8_tope_80/`.

```bash
python -m src.models.entrenar_cnn 0 80   # y 1, 2; reanuda si se interrumpe (borrar experiments/logs para empezar de cero)
```
