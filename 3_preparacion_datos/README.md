# 3. Preparación de los datos

Esta fase transforma el inventario de imágenes en los conjuntos de entrenamiento, validación y prueba que usan los modelos. El código se encuentra en [`src/data/preparar.py`](../src/data/preparar.py), [`src/data/segmentacion.py`](../src/data/segmentacion.py), [`src/features/caracteristicas.py`](../src/features/caracteristicas.py) y [`src/features/tamano.py`](../src/features/tamano.py). Ninguna imagen original se modifica: todas las transformaciones se calculan en memoria o se guardan como arreglos derivados en `data/processed/`.

## Reglas de selección

A partir del inventario de la fase 2 se conservan las imágenes que cumplen todas las condiciones siguientes:

| Regla | Justificación |
|---|---|
| Solo imágenes originales: se excluyen las capturas de pantalla y las imágenes aumentadas | Las aumentadas repiten el contenido de otras imágenes y generan fuga entre particiones; las capturas son otro dominio |
| Sin duplicados exactos (hash MD5) | Evita contar dos veces la misma imagen |
| Sin grupos de archivos idénticos con etiquetas distintas | Se descartan 3 grupos contradictorios entre las carpetas Bad y Regular |
| Lado mayor de al menos 128 px (solo para entrenamiento) | Por debajo de ese tamaño el detalle de la piel no es recuperable |
| Se descarta la carpeta Mixed de Kaggle y las fotos propias con varias frutas | Requieren segmentación individual y etiquetado por recorte |

## Conjuntos

Se toman hasta 400 imágenes por combinación de fuente, fruta y calidad, con semilla fija, y se reparten en entrenamiento, validación y prueba en proporción 70/15/15, estratificada por fruta y calidad. Las fotografías propias del grupo no se usan para entrenar: forman un conjunto de prueba externo que representa las condiciones reales de uso. Las fotografías adicionales (tercera fuente, `drive2`) sí entran en el reparto.

| Partición | Buena | Regular | Mala | Total |
|---|---|---|---|---|
| Entrenamiento | 2.992 | 637 | 2.204 | 5.833 |
| Validación | 642 | 136 | 472 | 1.250 |
| Prueba | 641 | 137 | 472 | 1.250 |
| Fotos propias (externo) | 96 | 10 | 0 | 106 |

El reparto 70/15/15 es habitual en conjuntos de este tamaño ([AWS Prescriptive Guidance, *Splits and data leakage*](https://docs.aws.amazon.com/prescriptive-guidance/latest/ml-operations-planning/splits-leakage.html), consultado el 25/11/2026) y deja 1.250 imágenes en validación y en prueba. No existe una regla general: Hastie, Tibshirani y Friedman (*The Elements of Statistical Learning*, 2.ª ed., 2009, cap. 7) mencionan como ejemplo 50/25/25. Se usa estratificación por fruta y calidad porque la clase Regular es minoritaria.

Por fuente, Kaggle aporta 2.400 imágenes buenas y 2.400 malas (no contiene la clase Regular), las imágenes de otros grupos aportan 1.474 buenas, 750 regulares y 676 malas, y las fotografías adicionales aportan 401 buenas, 160 regulares y 72 malas. La clase Regular es la minoritaria, con el 10,9 % del entrenamiento; se compensa con ponderación de clases inversamente proporcional a su frecuencia. El aumento de datos (giros, rotación, brillo y contraste) se aplica solo en el entrenamiento de la red convolucional.

## Justificación del tamaño del conjunto

El tope de 400 imágenes por fuente, fruta y calidad es una decisión de balance entre fuentes, no un tamaño de muestra calculado. Tras los filtros hay 23.848 imágenes elegibles y se usan 8.333. El tope solo recorta a Kaggle y a las imágenes de otros grupos; las fotografías adicionales entran completas.

| Fuente y calidad | Disponibles | Usadas |
|---|---|---|
| Kaggle buena | 11.664 | 2.400 |
| Kaggle mala | 6.788 | 2.400 |
| Otros grupos buena | 2.629 | 1.474 |
| Otros grupos regular | 849 | 750 |
| Otros grupos mala | 1.285 | 676 |
| Fotografías adicionales (las tres clases) | 633 | 633 |

Sin el tope, Kaggle pasaría de ser el 58 % de las imágenes usadas al 77 %, y la clase Regular, que Kaggle no contiene, caería del 10,9 % al 4,2 % del total, porque solo ganaría 99 imágenes (de 910 a 1.009). Eso reforzaría la confusión entre fuente y etiqueta detectada en la comprensión de los datos. Por eso el tope se fija para evitar que Kaggle domine, y no para ahorrar cómputo.

Para comprobar que el tamaño actual no es el factor limitante se calculó una curva de aprendizaje con el SVM (hiperparámetros fijos de [`svm.json`](../experiments/results/svm.json)), entrenado con fracciones del conjunto de entrenamiento (cinco muestras estratificadas por fracción) y evaluado siempre sobre las mismas particiones:

| Imágenes de entrenamiento | F1 macro en prueba | F1 macro en fotos propias |
|---|---|---|
| 291 | 0,777 ± 0,022 | 0,484 ± 0,072 |
| 1.166 | 0,880 ± 0,004 | 0,429 ± 0,049 |
| 2.916 | 0,929 ± 0,006 | 0,436 ± 0,018 |
| 4.374 | 0,939 ± 0,003 | 0,449 ± 0,010 |
| 5.833 (actual) | 0,949 | 0,450 |

(Media ± desviación entre las cinco muestras; la tabla completa está en [`curva_aprendizaje.csv`](../experiments/results/curva_aprendizaje.csv) y la figura en [`curva_aprendizaje.svg`](../experiments/results/curva_aprendizaje.svg).)

- **En distribución, más imágenes mejora el desempeño con rendimientos decrecientes:** pasar de 4.374 a 5.833 imágenes aporta +0,010 de F1 macro, y la variación entre muestras baja de 0,022 a 0,003.
- **En las fotografías propias el desempeño no depende del tamaño** (F1 macro entre 0,43 y 0,48 en todos los tamaños). El cuello de botella es el cambio de dominio, no la cantidad de datos.
- **El tamaño de las particiones fija la precisión de las métricas.** Con 1.250 imágenes de prueba, la exactitud del SVM (0,958) tiene un intervalo de confianza de Wilson del 95 % de [0,946; 0,968]. Para la clase Regular (137 imágenes de prueba), el recall del SVM tiene intervalo [0,84; 0,94]; con las 106 fotos propias, la exactitud tiene [0,73; 0,87]; y con las 10 imágenes malas de las fotografías adicionales, el recall tiene [0,40; 0,89]. La incertidumbre mayor está en las clases y fuentes pequeñas, no en el total.

Limitaciones: los hiperparámetros provienen de la búsqueda con el conjunto completo, lo que favorece ligeramente a los tamaños pequeños; la curva solo cubre el SVM y no la red convolucional; y no puede mostrar qué ocurriría con más imágenes de las que hay en el entrenamiento actual. Una extrapolación aproximada sugiere una mejora de unos 0,02 de F1 en distribución si se usaran todas las imágenes elegibles, sin efecto esperado en las fotos propias.

```bash
python -m src.evaluation.curva_aprendizaje
```

## Fotografías adicionales

Un tercer conjunto, `drive2`, reúne fotografías de banano, guayaba, limón, manzana y naranja organizadas por calidad. Se añade al inventario con `python -m src.data.inventario --agregar`, que conserva las filas existentes y marca como duplicados exactos los archivos ya presentes en otras fuentes. Se aplican las mismas reglas que a las demás fuentes (originales, sin duplicados exactos, sin archivos repetidos con etiquetas contradictorias y con al menos 128 px de lado mayor; se excluyó un archivo contradictorio). Quedan 633 imágenes (401 buenas, 160 regulares y 72 malas), con menos de 400 por combinación de fruta y calidad, de modo que entran todas: 428 en entrenamiento, 99 en validación y 106 en prueba. Se redimensionan completas, igual que Kaggle y las imágenes de otros grupos. Muchas están en formato HEIC, que se abre con `pillow-heif`.

## Preprocesamiento

- **Redimensionado:** todas las imágenes se llevan a 64 × 64 píxeles en RGB y se almacenan en bloques de 500 imágenes (`data/processed/arreglos_64/`).
- **Fotos propias:** se segmenta la fruta con [`segmentacion.py`](../src/data/segmentacion.py) y se recorta antes de redimensionar. La segmentación encontró fruta en el 91 % de las fotografías; en el resto se usa la imagen completa.
- **Características para el aprendizaje automático tradicional (55 variables):** histogramas de matiz (18 intervalos), saturación (8) y valor (8); media y desviación de seis canales (RGB y HSV); media HSV de la región central; y seis medidas de textura y color (magnitud media y desviación del gradiente de Sobel, varianza del laplaciano, fracción de píxeles oscuros, fracción de píxeles poco saturados y fracción de píxeles de tono cálido y saturados).
- **Tamaño:** el diámetro normalizado se calcula como $d_{norm} = \sqrt{4A/\pi} \,/\, \min(H, W)$ con $A$ el área de la máscara de la fruta. Los umbrales por fruta son los terciles de $d_{norm}$ en una muestra de 40 imágenes de entrenamiento por fruta y se guardan en [`experiments/results/umbrales_tamano.json`](../experiments/results/umbrales_tamano.json).

## Reproducción

```bash
python -m src.data.inventario --agregar data/processed/inventario.csv \
  --fuente "drive2=<carpeta de malas>" --fuente "drive2=<carpeta de regulares>" --fuente "drive2=<carpeta de buenas>" \
  --salida data/processed/inventario.csv
python -m src.data.preparar --reconstruir-indice
```

El comando de `inventario` se ejecuta una sola vez: cada ejecución añade las filas de las fotografías adicionales al inventario existente. Si cambia el índice, hay que borrar o renombrar `data/processed/arreglos_64/`, porque los bloques se identifican por posición.

## Limitaciones

- La división es aleatoria por archivo: no hay un identificador de ejemplar, por lo que fotografías distintas de una misma fruta pueden quedar en particiones diferentes. Los casi duplicados no se detectaron, de modo que las métricas sobre la prueba regular pueden ser optimistas.
- El conjunto externo de fotos propias es pequeño y no contiene frutas malas.
- Las fotografías adicionales toman la clase del nombre de la carpeta, incluyen varias fotos de una misma fruta (que la partición aleatoria puede repartir entre entrenamiento y prueba, lo que infla las métricas de ese origen) y tienen cobertura desigual: el limón solo tiene buenas, la guayaba no tiene malas y la manzana tiene 5 regulares.
- El tamaño es relativo al encuadre porque las imágenes carecen de escala física.
