# Datos

| Carpeta | Contenido | Versionado |
|---|---|---|
| `raw/` | Conjunto de datos original descargado | No (ignorado por git) |
| `propias/` | Imágenes recolectadas por el grupo y sus anotaciones | Sí |
| `processed/` | Imágenes segmentadas, particiones y características | No (se regenera) |

## Fuentes

- **Fruit Quality Classification** (Kaggle, ryandpark): <https://www.kaggle.com/datasets/ryandpark/fruit-quality-classification>. Se descarga y se descomprime en `data/raw/`. La carpeta *Mixed quality* se emplea para la evaluación y el enriquecimiento del conjunto, segmentando cada fruta.
- **Imágenes propias:** entre 30 y 50 fotografías como mínimo, tomadas en mercados, supermercados u hogares, que cubren distintos estados de madurez, tamaños y defectos.
- **Anotaciones compartidas** por los demás grupos del curso, que se integran al conjunto de datos.
- **Fotografías adicionales** de banano, guayaba, limón, manzana y naranja con etiqueta de calidad, que se integran al conjunto de datos como una tercera fuente (`drive2`) y no se versionan. Su preparación se describe en [`3_preparacion_datos/`](../3_preparacion_datos).

## Estructura del conjunto de referencia

La versión 1 del conjunto (3,29 GB) reúne **19.526 imágenes** de **seis frutas** (manzana, banano, guayaba, limón, naranja y granada), organizadas en tres carpetas:

| Carpeta | Contenido | Tamaño de imagen |
|---|---|---|
| `Good Quality_Fruits` | Frutas de calidad buena | 256×256 píxeles |
| `Bad Quality_Fruits` | Frutas de calidad mala | 256×256 píxeles |
| `Mixed Qualit_Fruits` | Imágenes con calidades mezcladas, que requieren segmentar cada fruta (el nombre de la carpeta aparece con esa errata en el original) | 256×192 píxeles |

Según su ficha, las imágenes se tomaron desde cinco orientaciones: frontal, superior, posterior, inferior y rotada 180 grados. Por tanto, un mismo ejemplar puede aparecer en varias imágenes.

Las clases de calidad del proyecto (Buena, Regular y Mala) se construyen a partir de estas carpetas y de las imágenes propias, según la correspondencia descrita en [`1_comprension_negocio/README.md`](../1_comprension_negocio/README.md).

Todo dato o código de terceros se referencia de forma explícita.

[1] ryandpark, "Fruit Quality Classification," Kaggle. [Online]. Available: https://www.kaggle.com/datasets/ryandpark/fruit-quality-classification

## Anotaciones propias

Las anotaciones se registran en `data/propias/anotaciones.csv` con las columnas: `archivo`, `fruta`, `calidad`, `tamano`, `fecha` y `lugar`.
