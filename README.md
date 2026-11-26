# Clasificación de calidad de frutas con visión por computadora

Proyecto final del curso **Algoritmos y Programación III (2026-2)**, Ingeniería de Sistemas, Universidad Icesi, Cali, Colombia.

## Integrantes

| Nombre | GitHub |
|---|---|
| Cristina Angulo (A00404027) | [@cristalNova](https://github.com/cristalNova) |
| Samuel Navia (A00405006) |  |

## Objetivo

El proyecto desarrolla un sistema automático que, a partir de una fotografía de una fruta individual sobre fondo uniforme, **asigna una clase de calidad** (Buena, Regular o Mala) y **estima su tamaño** (Pequeño, Mediano o Grande). Su propósito es reducir la subjetividad, la lentitud y las pérdidas propias de la clasificación manual en mercados y agroindustria.

## Metodología

El trabajo se organiza según la metodología **CRISP-DM**. Cada fase cuenta con una carpeta que reúne la evidencia correspondiente:

| Fase | Carpeta |
|---|---|
| 1. Comprensión del negocio | [`1_comprension_negocio/`](1_comprension_negocio) |
| 2. Comprensión de los datos | [`2_comprension_datos/`](2_comprension_datos) |
| 3. Preparación de los datos | [`3_preparacion_datos/`](3_preparacion_datos) |
| 4. Modelado (dos modelos de aprendizaje automático tradicional y uno de aprendizaje profundo) | [`4_modelado/`](4_modelado) |
| 5. Evaluación | [`5_evaluacion/`](5_evaluacion) |
| 6. Despliegue (interfaz gráfica) | [`6_despliegue/`](6_despliegue) |

## Estructura del repositorio

```
├── 1_comprension_negocio/ … 6_despliegue/   # Una carpeta por fase de CRISP-DM
├── src/                                      # Código reutilizable (data, features, models, evaluation, utils)
├── data/                                     # raw/ (Kaggle), propias/ (imágenes y anotaciones), processed/
├── experiments/                              # logs, checkpoints, results (métricas y gráficas)
├── tests/
├── docs/                                     # Informe, ética, formulación matemática, video
├── requirements.txt
└── README.md
```

## Documentación complementaria

- **Ética:** [`docs/etica.md`](docs/etica.md)
- **Impactos global, social, ambiental y económico:** [`1_comprension_negocio/README.md`](1_comprension_negocio/README.md#18-impactos-de-la-solución)
- **Formulación y fundamentos matemáticos:** [`docs/formulacion_matematica.md`](docs/formulacion_matematica.md)
- **Informe final (PDF):** [`docs/informe/`](docs/informe)
- **Video de presentación (máximo 10 minutos):** [`docs/video/`](docs/video)

## Datos

El proyecto utiliza el conjunto de referencia [Fruit Quality Classification (Kaggle)](https://www.kaggle.com/datasets/ryandpark/fruit-quality-classification), complementado con imágenes propias y con las anotaciones compartidas entre los grupos del curso. Las instrucciones de obtención y las fuentes se describen en [`data/README.md`](data/README.md).

## Ejecución

1. Clonar el repositorio.
2. Crear un entorno virtual e instalar las dependencias: `pip install -r requirements.txt`.
3. Obtener los datos según [`data/README.md`](data/README.md).
4. Ejecutar el flujo desde la raíz del repositorio (cada fase detalla sus opciones en su `README.md`):
   - Fase 2: `python -m src.data.descargar_kaggle` y `python -m src.data.inventario ...`; el análisis exploratorio está en `2_comprension_datos/eda.ipynb`.
   - Fase 3: `python -m src.data.preparar --reconstruir-indice`.
   - Fase 4: `python -m src.models.entrenar_ml`, `python -m src.models.entrenar_alternativas` y `python -m src.models.entrenar_cnn 0 80` (también `1` y `2`).
   - Fase 5: `python -m src.evaluation.analisis` y `python -m src.evaluation.errores`.
   - Fase 6: `streamlit run 6_despliegue/app.py`.

## Licencia

Véase [`LICENSE`](LICENSE).
