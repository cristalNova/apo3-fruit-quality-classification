# 6. Despliegue

La interfaz gráfica es una aplicación web en Streamlit ([`app.py`](app.py)) que permite cargar una imagen o capturarla con la cámara, y muestra la calidad y el tamaño de la fruta.

## Ejecución

```bash
pip install -r requirements.txt
streamlit run 6_despliegue/app.py
```

La aplicación necesita los modelos `experiments/checkpoints/cnn.keras` y `experiments/checkpoints/svm.joblib`, incluidos en el repositorio.

## Flujo

1. La persona elige la fruta y carga o captura la fotografía.
2. [`src/inferencia.py`](../src/inferencia.py) segmenta la fruta con [`segmentacion.py`](../src/data/segmentacion.py), la recorta y la redimensiona a 64 × 64 píxeles; si no encuentra fruta, usa la imagen completa.
3. La red convolucional estima la probabilidad de cada clase de calidad y el SVM entrega su propia predicción.
4. El diámetro normalizado de la máscara se compara con los umbrales de la fruta elegida para asignar el tamaño: pequeño, mediano o grande.

## Plan de despliegue y limitaciones

- La aplicación funciona en un computador con cámara web, sin GPU; la inferencia de una imagen tarda menos de un segundo (0,3 s con una fotografía de 4032 px, medido en un entorno de 2 núcleos).
- Es una herramienta de apoyo y no sustituye la decisión humana (véase [`docs/etica.md`](../docs/etica.md)).
- El desempeño es menor con fotografías de iluminación y fondos distintos a los del entrenamiento (véase [`5_evaluacion/`](../5_evaluacion)).
- El tamaño es relativo al encuadre, porque no hay escala física, y la fruta debe indicarse manualmente.
