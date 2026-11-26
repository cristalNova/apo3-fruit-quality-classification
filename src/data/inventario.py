"""Cataloga las imágenes de cada fuente (fruta, calidad, tamaño, duplicados exactos y estadísticas de color) en un CSV."""

import argparse
import hashlib
import re
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

try:
    import pillow_heif

    pillow_heif.register_heif_opener()
except ImportError:
    pass

EXTENSIONES = {".jpg", ".jpeg", ".png", ".heic"}
FRUTAS = {
    "apple": "manzana", "manzana": "manzana",
    "banana": "banano", "banano": "banano",
    "guava": "guayaba", "guayaba": "guayaba",
    "lime": "limon", "lemon": "limon", "limon": "limon",
    "orange": "naranja", "orage": "naranja", "naranja": "naranja",
    "pomegranate": "granada", "granada": "granada",
}
CALIDADES = {
    "good": "buena", "buena": "buena",
    "regular": "regular",
    "bad": "mala", "mala": "mala",
    "mixed": "mezclada",
}


def tipo_archivo(nombre):
    """Clasifica el archivo como original, aumentada o captura de pantalla según su nombre."""
    if re.search(r"_aug_|^rotated_by_|^aug_", nombre, re.I):
        return "aumentada"
    if re.search(r"captura de pantalla|screen ?shot", nombre, re.I):
        return "captura"
    return "original"


def calidad_y_fruta(partes):
    """Deduce la calidad y la fruta a partir de las carpetas de la ruta."""
    calidad = CALIDADES.get(partes[0].lower().split()[0].split("_")[0])
    for parte in partes[1:-1]:
        clave = parte.lower().split("_")[0]
        if clave in FRUTAS:
            return calidad, FRUTAS[clave]
    return calidad, None


def dimensiones(ruta):
    """Devuelve (ancho, alto) de la imagen, o (-1, -1) si no se puede abrir."""
    try:
        with Image.open(ruta) as im:
            return im.size
    except OSError:
        return -1, -1


def medir(ruta):
    """Devuelve ancho, alto y tamaño en bytes del archivo."""
    ancho, alto = dimensiones(ruta)
    return ancho, alto, ruta.stat().st_size


def catalogar(origen, raiz, preetiquetas=None):
    """Recorre una fuente y construye la tabla de imágenes con origen, calidad, fruta y medidas."""
    rutas = [r for r in sorted(raiz.rglob("*")) if r.suffix.lower() in EXTENSIONES]
    with ThreadPool(16) as pool:
        medidas = pool.map(medir, rutas)
    filas = []
    for ruta, (ancho, alto, peso) in zip(rutas, medidas):
        rel = ruta.relative_to(raiz)
        if preetiquetas is None:
            partes = rel.parts if calidad_y_fruta(rel.parts)[0] else (raiz.name, *rel.parts)
            calidad, fruta = calidad_y_fruta(partes)
        elif ruta.name in preetiquetas.index:
            fruta, calidad = preetiquetas.loc[ruta.name, ["fruta", "calidad"]]
        else:
            calidad = fruta = None
        filas.append({
            "origen": origen,
            "ruta": rel.as_posix(),
            "archivo": ruta.name,
            "fruta": fruta,
            "calidad": calidad,
            "ancho": ancho,
            "alto": alto,
            "lado_mayor": max(ancho, alto),
            "bytes": peso,
            "formato": ruta.suffix.lower().lstrip("."),
            "tipo_archivo": tipo_archivo(ruta.name),
            "ruta_absoluta": str(ruta),
        })
    return pd.DataFrame(filas)


def calcular_md5(ruta):
    """Calcula el hash MD5 del contenido de un archivo."""
    return hashlib.md5(Path(ruta).read_bytes()).hexdigest()


def marcar_duplicados_exactos(df):
    """Calcula el MD5 de los archivos de igual tamaño y marca los duplicados exactos."""
    df = df.copy()
    if "md5" not in df:
        df["md5"] = None
    candidatos = df[df.duplicated("bytes", keep=False) & df["md5"].isna()]
    with ThreadPool(16) as pool:
        df.loc[candidatos.index, "md5"] = pool.map(calcular_md5, candidatos["ruta_absoluta"])
    df["duplicado_exacto"] = df["md5"].notna() & df.duplicated("md5")
    return df


def estadisticas(ruta, lado=96):
    """Mide el brillo, la saturación y el brillo del borde de una imagen reducida."""
    with Image.open(ruta) as im:
        im.draft("RGB", (lado * 2, lado * 2))
        rgb = np.asarray(im.convert("RGB").resize((lado, lado)), dtype=np.float32)
    maximo, minimo = rgb.max(axis=2), rgb.min(axis=2)
    saturacion = (maximo - minimo) / np.maximum(maximo, 1)
    b = lado // 12
    borde = np.concatenate([rgb[:b].reshape(-1, 3), rgb[-b:].reshape(-1, 3),
                            rgb[:, :b].reshape(-1, 3), rgb[:, -b:].reshape(-1, 3)])
    return {
        "ruta_absoluta": ruta,
        "brillo": maximo.mean(),
        "saturacion": saturacion.mean() * 255,
        "brillo_borde": borde.max(axis=1).mean(),
        "desv_borde": borde.std(axis=0).mean(),
    }


def agregar_estadisticas(df, por_grupo=60, semilla=0, procesos=4):
    """Añade estadísticas de color a una muestra de imágenes por origen, fruta y calidad."""
    muestra = (df[df["lado_mayor"] > 0]
               .sample(frac=1, random_state=semilla)
               .groupby(["origen", "fruta", "calidad"], dropna=False)
               .head(por_grupo))
    with Pool(procesos) as pool:
        filas = pool.map(estadisticas, muestra["ruta_absoluta"], chunksize=16)
    return df.merge(pd.DataFrame(filas), on="ruta_absoluta", how="left")


def main():
    """Construye el inventario de imágenes desde la línea de comandos."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--fuente", action="append", default=[], metavar="NOMBRE=RUTA",
                        help="carpeta con subcarpetas de calidad y fruta")
    parser.add_argument("--sin-clasificar", metavar="NOMBRE=RUTA",
                        help="carpeta plana cuya clase proviene de --preetiquetas")
    parser.add_argument("--preetiquetas", type=Path)
    parser.add_argument("--agregar", type=Path,
                        help="inventario existente al que se añaden las fuentes indicadas")
    parser.add_argument("--salida", type=Path, required=True)
    parser.add_argument("--por-grupo", type=int, default=60,
                        help="imágenes por grupo para las estadísticas de color (0 las omite)")
    args = parser.parse_args()

    tablas = [catalogar(nombre, Path(ruta))
              for nombre, ruta in (item.split("=", 1) for item in args.fuente)]
    if args.sin_clasificar:
        nombre, ruta = args.sin_clasificar.split("=", 1)
        preetiquetas = pd.read_csv(args.preetiquetas, encoding="utf-8-sig").set_index("archivo")
        tablas.append(catalogar(nombre, Path(ruta), preetiquetas))
    if args.agregar:
        nuevas = pd.concat(tablas, ignore_index=True)
        if args.por_grupo > 0:
            nuevas = agregar_estadisticas(nuevas, args.por_grupo)
        df = marcar_duplicados_exactos(pd.concat([pd.read_csv(args.agregar), nuevas], ignore_index=True))
    else:
        df = marcar_duplicados_exactos(pd.concat(tablas, ignore_index=True))
        if args.por_grupo > 0:
            df = agregar_estadisticas(df, args.por_grupo)
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.salida, index=False)
    print(f"{len(df)} imágenes catalogadas en {args.salida}")


if __name__ == "__main__":
    main()
