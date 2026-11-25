# Clasificación de calidad de frutas con visión por computadora

Proyecto final del curso **Algoritmos y Programación III (2026-2)**, Ingeniería de Sistemas, Universidad Icesi, Cali, Colombia.

## Integrantes

| Nombre | GitHub |
|---|---|
| Cristina Angulo | [@cristalNova](https://github.com/cristalNova) |
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
├── docs/                                     # Informe, ética, impactos, formulación matemática, video
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

1. Clonar el repositorio y crear un entorno virtual.
2. Instalar las dependencias: `pip install -r requirements.txt`.
3. Iniciar la aplicación: `streamlit run 6_despliegue/app.py`.
4. Ejecutar las pruebas: `python -m pytest -q tests`.

Para reproducir el entrenamiento, obtener primero las imágenes según `data/README.md` y generar los datos procesados siguiendo `3_preparacion_datos/README.md`.
## Licencia

Véase [`LICENSE`](LICENSE).
