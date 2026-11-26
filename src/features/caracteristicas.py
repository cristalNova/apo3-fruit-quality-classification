"""Extrae las 55 características de color y textura (histogramas HSV, momentos, región central y gradiente) de imágenes de 64×64."""

import cv2
import numpy as np

BINS_MATIZ, BINS_SATURACION, BINS_VALOR = 18, 8, 8


def caracteristicas_imagen(rgb):
    """Calcula las 55 características de color y textura de una imagen RGB."""
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    gris = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]

    hist = [
        np.histogram(h, BINS_MATIZ, (0, 180))[0],
        np.histogram(s, BINS_SATURACION, (0, 256))[0],
        np.histogram(v, BINS_VALOR, (0, 256))[0],
    ]
    hist = np.concatenate(hist).astype(np.float32) / h.size

    canales = np.dstack([rgb, hsv]).reshape(-1, 6).astype(np.float32)
    centro = hsv[16:48, 16:48].reshape(-1, 3).astype(np.float32)

    gx = cv2.Sobel(gris, cv2.CV_32F, 1, 0)
    gy = cv2.Sobel(gris, cv2.CV_32F, 0, 1)
    gradiente = np.hypot(gx, gy)
    textura = [
        gradiente.mean(), gradiente.std(),
        cv2.Laplacian(gris, cv2.CV_32F).var(),
        (v < 60).mean(), (s < 40).mean(), ((h < 25) & (s > 80)).mean(),
    ]
    return np.concatenate([hist, canales.mean(0), canales.std(0), centro.mean(0), textura]).astype(np.float32)


def caracteristicas(imagenes):
    """Apila las características de una colección de imágenes."""
    return np.stack([caracteristicas_imagen(im) for im in imagenes])
