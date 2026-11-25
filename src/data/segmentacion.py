from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps

try:
    import pillow_heif

    pillow_heif.register_heif_opener()
except ImportError:
    pass

EXTENSIONES = {".jpg", ".jpeg", ".png", ".webp", ".heic"}


@dataclass
class Fruta:

    caja: tuple[int, int, int, int]
    mascara: np.ndarray
    area_fraccion: float
    solidez: float
    posible_agrupacion: bool


def cargar_imagen(ruta: Path) -> np.ndarray:
    with Image.open(ruta) as im:
        return np.asarray(ImageOps.exif_transpose(im).convert("RGB"))


def _mascara_primer_plano(rgb: np.ndarray, saturacion_minima: int) -> np.ndarray:
    suave = cv2.GaussianBlur(rgb, (7, 7), 0)
    hsv = cv2.cvtColor(suave, cv2.COLOR_RGB2HSV)
    saturacion = hsv[:, :, 1]
    valor = hsv[:, :, 2]
    matiz = hsv[:, :, 0]
    umbral, _ = cv2.threshold(saturacion, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    umbral = max(int(umbral), saturacion_minima)
    fondo_azulado = (matiz >= 95) & (matiz <= 140) & (valor < 140)
    mascara = (saturacion > umbral) & (valor > 50) & ~fondo_azulado
    mascara |= (saturacion > max(saturacion_minima, 65)) & (valor > 170) & (matiz < 95)
    mascara = mascara.astype(np.uint8) * 255

    lado = max(rgb.shape[:2])
    k_cierre = max(3, int(lado * 0.012) | 1)
    k_apertura = max(3, int(lado * 0.006) | 1)
    cierre = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_cierre, k_cierre))
    apertura = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_apertura, k_apertura))
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, cierre)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, apertura)
    return mascara


def _rellenar_huecos(mascara: np.ndarray) -> np.ndarray:
    relleno = cv2.copyMakeBorder(mascara, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    alto, ancho = relleno.shape
    cv2.floodFill(relleno, np.zeros((alto + 2, ancho + 2), np.uint8), (0, 0), 255)
    huecos = cv2.bitwise_not(relleno)[1:-1, 1:-1]
    return mascara | huecos


def _refinar_grabcut(rgb: np.ndarray, mascara: np.ndarray, caja: tuple[int, int, int, int]) -> np.ndarray:
    x, y, w, h = caja
    margen = max(4, int(0.08 * max(w, h)))
    x0, y0 = max(0, x - margen), max(0, y - margen)
    x1, y1 = min(rgb.shape[1], x + w + margen), min(rgb.shape[0], y + h + margen)
    sub_rgb = np.ascontiguousarray(rgb[y0:y1, x0:x1])
    sub_masc = mascara[y0:y1, x0:x1]
    nucleo = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    seguro = cv2.erode(sub_masc, nucleo)
    probable = cv2.dilate(sub_masc, nucleo)
    gc = np.full(sub_masc.shape, cv2.GC_BGD, np.uint8)
    gc[probable > 0] = cv2.GC_PR_BGD
    gc[sub_masc > 0] = cv2.GC_PR_FGD
    gc[seguro > 0] = cv2.GC_FGD
    try:
        bgd = np.zeros((1, 65), np.float64)
        fgd = np.zeros((1, 65), np.float64)
        cv2.grabCut(sub_rgb, gc, None, bgd, fgd, 3, cv2.GC_INIT_WITH_MASK)
    except cv2.error:
        return mascara
    nueva = np.where((gc == cv2.GC_FGD) | (gc == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    if nueva.sum() < 0.5 * sub_masc.sum():
        return mascara
    salida = np.zeros_like(mascara)
    salida[y0:y1, x0:x1] = nueva
    return salida


def _solidez(mascara: np.ndarray) -> float:
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contornos:
        return 0.0
    contorno = max(contornos, key=cv2.contourArea)
    casco = cv2.contourArea(cv2.convexHull(contorno))
    return float(cv2.contourArea(contorno) / casco) if casco > 0 else 0.0


def _separar_en_contacto(rgb: np.ndarray, comp: np.ndarray, solidez_minima: float) -> list[np.ndarray]:
    if _solidez(comp) >= solidez_minima:
        return [comp]
    distancia = cv2.distanceTransform(comp, cv2.DIST_L2, 5)
    _, centros = cv2.threshold(distancia, 0.6 * distancia.max(), 255, cv2.THRESH_BINARY)
    centros = centros.astype(np.uint8)
    n, marcadores = cv2.connectedComponents(centros)
    if n - 1 < 2:
        return [comp]
    marcadores = marcadores.astype(np.int32) + 1
    marcadores[(comp > 0) & (centros == 0)] = 0
    marcadores[comp == 0] = 1
    cv2.watershed(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), marcadores)
    partes = []
    for etiqueta in range(2, n + 1):
        parte = ((marcadores == etiqueta) & (comp > 0)).astype(np.uint8) * 255
        if parte.sum() > 0:
            partes.append(parte)
    total = float((comp > 0).sum())
    if len(partes) < 2 or any((p > 0).sum() < 0.25 * total / len(partes) for p in partes):
        return [comp]
    return partes


def segmentar_frutas(
    rgb: np.ndarray,
    lado_trabajo: int = 1024,
    area_minima: float = 0.005,
    area_maxima: float = 0.9,
    saturacion_minima: int = 50,
    solidez_minima: float = 0.88,
    brillo_minimo: float = 90.0,
    descartar_borde: bool = True,
    refinar: bool = True,
) -> list[Fruta]:
    alto0, ancho0 = rgb.shape[:2]
    escala = min(1.0, lado_trabajo / max(alto0, ancho0))
    if escala < 1.0:
        trabajo = cv2.resize(rgb, (round(ancho0 * escala), round(alto0 * escala)), interpolation=cv2.INTER_AREA)
    else:
        trabajo = rgb
    alto, ancho = trabajo.shape[:2]

    mascara = _rellenar_huecos(_mascara_primer_plano(trabajo, saturacion_minima))
    n, etiquetas, stats, _ = cv2.connectedComponentsWithStats(mascara, connectivity=8)

    candidatas: list[np.ndarray] = []
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] < area_minima * alto * ancho:
            continue
        candidatas += _separar_en_contacto(trabajo, (etiquetas == i).astype(np.uint8) * 255, 0.95)

    frutas: list[Fruta] = []
    for comp in candidatas:
        x, y, w, h = cv2.boundingRect(comp)
        area = int((comp > 0).sum())
        fraccion = area / float(alto * ancho)
        if not (area_minima <= fraccion <= area_maxima):
            continue
        toca_borde = x <= 1 or y <= 1 or x + w >= ancho - 1 or y + h >= alto - 1
        if descartar_borde and toca_borde:
            continue
        brillo = float(cv2.cvtColor(trabajo, cv2.COLOR_RGB2HSV)[:, :, 2][comp > 0].mean())
        if brillo < brillo_minimo:
            continue
        if refinar:
            comp = _refinar_grabcut(trabajo, comp, (x, y, w, h))
        sin_sombra = comp.copy()
        sin_sombra[cv2.cvtColor(trabajo, cv2.COLOR_RGB2HSV)[:, :, 2] < 60] = 0
        contornos, _ = cv2.findContours(sin_sombra, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contornos:
            continue
        contorno = max(contornos, key=cv2.contourArea)
        area_c = cv2.contourArea(contorno)
        casco_pts = cv2.convexHull(contorno)
        casco = cv2.contourArea(casco_pts)
        solidez = float(area_c / casco) if casco > 0 else 0.0
        forma = casco_pts if solidez >= 0.85 else contorno
        x, y, w, h = cv2.boundingRect(forma)
        limpia = np.zeros_like(comp)
        cv2.drawContours(limpia, [forma], -1, 255, thickness=cv2.FILLED)
        if escala < 1.0:
            limpia = cv2.resize(limpia, (ancho0, alto0), interpolation=cv2.INTER_NEAREST)
            x, y, w, h = (int(round(v / escala)) for v in (x, y, w, h))
        frutas.append(
            Fruta(
                caja=(x, y, min(w, ancho0 - x), min(h, alto0 - y)),
                mascara=limpia,
                area_fraccion=float(area_c / (alto * ancho)),
                solidez=solidez,
                posible_agrupacion=solidez < solidez_minima,
            )
        )
    frutas.sort(key=lambda f: (round(f.caja[1] / max(1, alto0 * 0.15)), f.caja[0]))
    return frutas


def recortar_fruta(
    rgb: np.ndarray,
    fruta: Fruta,
    margen: float = 0.06,
    fondo: str = "original",
    lado_max: int | None = 512,
) -> np.ndarray:
    x, y, w, h = fruta.caja
    m = int(margen * max(w, h))
    x0, y0 = max(0, x - m), max(0, y - m)
    x1, y1 = min(rgb.shape[1], x + w + m), min(rgb.shape[0], y + h + m)
    recorte = rgb[y0:y1, x0:x1].copy()
    if fondo == "blanco":
        masc = fruta.mascara[y0:y1, x0:x1] > 0
        recorte[~masc] = 255
    if lado_max and max(recorte.shape[:2]) > lado_max:
        e = lado_max / max(recorte.shape[:2])
        recorte = cv2.resize(
            recorte, (round(recorte.shape[1] * e), round(recorte.shape[0] * e)), interpolation=cv2.INTER_AREA
        )
    return recorte


def procesar_carpeta(
    entrada: Path,
    salida: Path,
    fondo: str = "original",
    lado_max: int | None = 512,
    **opciones,
) -> Path:
    salida.mkdir(parents=True, exist_ok=True)
    registro = salida / "recortes.csv"
    campos = [
        "recorte", "origen", "indice", "x", "y", "ancho", "alto",
        "area_fraccion", "solidez", "posible_agrupacion", "n_frutas_en_imagen",
    ]
    archivos = sorted(p for p in entrada.iterdir() if p.suffix.lower() in EXTENSIONES)
    with registro.open("w", newline="", encoding="utf-8") as fh:
        escritor = csv.DictWriter(fh, fieldnames=campos)
        escritor.writeheader()
        for ruta in archivos:
            rgb = cargar_imagen(ruta)
            frutas = segmentar_frutas(rgb, **opciones)
            if not frutas:
                escritor.writerow({"recorte": "", "origen": ruta.name, "n_frutas_en_imagen": 0})
                continue
            for k, fruta in enumerate(frutas, start=1):
                nombre = f"{ruta.stem}_f{k}.jpg"
                recorte = recortar_fruta(rgb, fruta, fondo=fondo, lado_max=lado_max)
                Image.fromarray(recorte).save(salida / nombre, quality=92)
                x, y, w, h = fruta.caja
                escritor.writerow(
                    {
                        "recorte": nombre, "origen": ruta.name, "indice": k,
                        "x": x, "y": y, "ancho": w, "alto": h,
                        "area_fraccion": round(fruta.area_fraccion, 4),
                        "solidez": round(fruta.solidez, 3),
                        "posible_agrupacion": fruta.posible_agrupacion,
                        "n_frutas_en_imagen": len(frutas),
                    }
                )
    return registro


def _argumentos() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Segmenta frutas individuales de una carpeta de imágenes.")
    p.add_argument("entrada", type=Path, help="Carpeta con las imágenes de origen.")
    p.add_argument("salida", type=Path, help="Carpeta donde se escriben los recortes y el registro.")
    p.add_argument("--fondo", choices=["original", "blanco"], default="original")
    p.add_argument("--lado-max", type=int, default=512, help="Lado mayor de cada recorte (0 = tamaño original).")
    p.add_argument("--sin-refinar", action="store_true", help="No refinar el contorno con GrabCut.")
    p.add_argument("--permitir-borde", action="store_true", help="Conservar frutas que tocan el borde.")
    return p.parse_args()


if __name__ == "__main__":
    a = _argumentos()
    ruta = procesar_carpeta(
        a.entrada,
        a.salida,
        fondo=a.fondo,
        lado_max=a.lado_max or None,
        refinar=not a.sin_refinar,
        descartar_borde=not a.permitir_borde,
    )
    print(f"Registro escrito en {ruta}")
