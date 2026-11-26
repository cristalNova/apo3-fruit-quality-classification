# 2. Comprensión de los datos

Esta fase describe y explora los datos disponibles: el conjunto de referencia *Fruit Quality Classification* (Kaggle) y las imágenes propias recolectadas por el grupo. Las fuentes se detallan en [`data/README.md`](../data/README.md).

El análisis exploratorio, desarrollado en los notebooks de esta carpeta, aborda:

- la distribución de clases y el desbalanceo;
- la calidad de las imágenes: resolución, iluminación, fondo y ruido;
- la variabilidad: color, tamaño, ángulo y defectos (golpes, manchas y podredumbre);
- la comparación entre los datos de Kaggle y las imágenes propias, con el fin de detectar cambio de dominio;
- la revisión de la carpeta *Mixed quality* y de los elementos que requieren segmentación.

Los criterios con los que se asigna la clase de calidad a cada imagen se documentan en la [guía de anotación](guia_anotacion.md).

## Cuaderno de análisis exploratorio

El análisis se encuentra en [`eda.ipynb`](eda.ipynb) y sus figuras en [`figuras/`](figuras/). Se apoya en el inventario de imágenes que genera [`src/data/inventario.py`](../src/data/inventario.py), que solo lee las imágenes y guarda una fila por archivo (origen, fruta, calidad, resolución, formato, tipo de archivo, estadísticas de color y duplicados exactos).

Para reproducirlo, desde la raíz del repositorio:

```bash
python -m src.data.descargar_kaggle
python -m src.data.inventario \
  --fuente "kaggle=data/raw/datasets/ryandpark/fruit-quality-classification/versions/1" \
  --fuente "companeros=<ruta a las imágenes de otros grupos>" \
  --sin-clasificar "propias_sin_clasificar=<ruta a las fotos del grupo>" \
  --preetiquetas <ruta al CSV de preetiquetas> \
  --salida data/processed/inventario.csv
```

Cada fuente se indica como `NOMBRE=RUTA`: `--fuente` para las carpetas organizadas por calidad y fruta, y `--sin-clasificar` para una carpeta plana cuya clase proviene del CSV de preetiquetas. Después se ejecuta el cuaderno desde esta carpeta. `descargar_kaggle` baja el conjunto de Kaggle a `data/raw/`. Las imágenes de Kaggle y de otros grupos no se versionan y no aparecen en las figuras.

Principales hallazgos, detallados en la sección 7 del cuaderno:

- Kaggle aporta 19.526 imágenes (11.664 Good, 6.788 Bad y 1.074 Mixed con varias frutas por foto) y no tiene clase Regular; no comparte duplicados exactos con las demás fuentes.
- Las 144 imágenes de la muestra etiquetada están repetidas en las imágenes de otros grupos.
- La resolución y el tipo de archivo (capturas de pantalla e imágenes aumentadas) dependen de la clase, de modo que la etiqueta está confundida con la fuente: solo con metadatos del archivo se predice la calidad con una exactitud de 0,79 frente a 0,49 de la clase mayoritaria en las imágenes de otros grupos y de 0,72 frente a 0,63 en Kaggle.
- Las tres fuentes difieren en resolución e iluminación (las fotos propias son mucho más oscuras y de mayor resolución), por lo que hay cambio de dominio entre ellas.
- Hay etiquetas contradictorias y duplicados que deben resolverse antes de dividir en entrenamiento y prueba.

Los hallazgos de esta fase orientan las decisiones de preparación de datos de la fase siguiente.
