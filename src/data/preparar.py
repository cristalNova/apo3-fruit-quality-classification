import argparse
import time
from multiprocessing.pool import ThreadPool
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageOps
from sklearn.model_selection import train_test_split

from src.data.segmentacion import cargar_imagen, recortar_fruta, segmentar_frutas

try:
    import pillow_heif

    pillow_heif.register_heif_opener()
except ImportError:
    pass

CALIDADES = ["buena", "regular", "mala"]
ORIGENES_ENTRENABLES = ["kaggle", "companeros", "drive2"]


def construir_indice(inventario, salida, por_grupo=400, lado_minimo=128, semilla=0):
    inv = pd.read_csv(inventario)
    calidades_por_hash = inv[inv["md5"].notna()].groupby("md5")["calidad"].nunique()
    conflictivos = set(calidades_por_hash[calidades_por_hash > 1].index)

    base = inv[
        inv["calidad"].isin(CALIDADES)
        & (inv["tipo_archivo"] == "original")
        & ~inv["duplicado_exacto"]
        & ~inv["md5"].isin(conflictivos)
    ]
    entrenables = base[base["origen"].isin(ORIGENES_ENTRENABLES) & (base["lado_mayor"] >= lado_minimo)]
    muestra = pd.concat(
        g.sample(min(len(g), por_grupo), random_state=semilla)
        for _, g in entrenables.groupby(["origen", "fruta", "calidad"])
    )

    estrato = muestra["fruta"] + "_" + muestra["calidad"]
    resto, prueba = train_test_split(muestra, test_size=0.15, stratify=estrato, random_state=semilla)
    entrenamiento, validacion = train_test_split(
        resto, test_size=0.15 / 0.85, stratify=resto["fruta"] + "_" + resto["calidad"], random_state=semilla
    )
    propias = base[base["origen"] == "propias_sin_clasificar"]
    indice = pd.concat(
        [
            entrenamiento.assign(particion="entrenamiento"),
            validacion.assign(particion="validacion"),
            prueba.assign(particion="prueba"),
            propias.assign(particion="propias"),
        ]
    )[["origen", "fruta", "calidad", "particion", "archivo", "ruta_absoluta"]].reset_index(drop=True)
    Path(salida).parent.mkdir(parents=True, exist_ok=True)
    indice.to_csv(salida, index=False)
    return indice


def leer(ruta, lado):
    with Image.open(ruta) as im:
        im.draft("RGB", (lado * 4, lado * 4))
        im = ImageOps.exif_transpose(im).convert("RGB")
        return np.asarray(im.resize((lado, lado), Image.BILINEAR))


def cachear(indice, carpeta, lado=64, tam_bloque=500, presupuesto=140):
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    inicio = time.time()
    pendientes = 0
    with ThreadPool(16) as pool:
        for b in range(-(-len(indice) // tam_bloque)):
            destino = carpeta / f"bloque_{b:03d}.npy"
            if destino.exists():
                continue
            if time.time() - inicio > presupuesto:
                pendientes += 1
                continue
            rutas = indice["ruta_absoluta"].iloc[b * tam_bloque:(b + 1) * tam_bloque]
            np.save(destino, np.stack(pool.map(lambda r: leer(r, lado), rutas)))
    return pendientes


def cargar_arreglos(carpeta):
    return np.concatenate([np.load(a) for a in sorted(Path(carpeta).glob("bloque_*.npy"))])


def recortar_propias(indice, carpeta, lado=64):
    destino = Path(carpeta) / "propias_recortes.npy"
    filas = indice[indice["particion"] == "propias"]
    recortes, con_segmentacion = [], []
    for ruta in filas["ruta_absoluta"]:
        rgb = cargar_imagen(Path(ruta))
        frutas = segmentar_frutas(rgb)
        if frutas:
            rgb = recortar_fruta(rgb, max(frutas, key=lambda f: f.area_fraccion), lado_max=256)
        con_segmentacion.append(bool(frutas))
        recortes.append(np.asarray(Image.fromarray(rgb).resize((lado, lado), Image.BILINEAR)))
    np.save(destino, np.stack(recortes))
    return np.array(con_segmentacion)


def cargar_dataset(indice, carpeta):
    X = cargar_arreglos(carpeta)
    propias = np.load(Path(carpeta) / "propias_recortes.npy")
    X[(indice["particion"] == "propias").to_numpy()] = propias
    return X


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--inventario", default="data/processed/inventario.csv")
    p.add_argument("--indice", default="data/processed/dataset.csv")
    p.add_argument("--cache", default="data/processed/arreglos_64")
    p.add_argument("--por-grupo", type=int, default=400)
    p.add_argument("--lado-minimo", type=int, default=128)
    p.add_argument("--lado", type=int, default=64)
    p.add_argument("--reconstruir-indice", action="store_true")
    a = p.parse_args()

    if a.reconstruir_indice or not Path(a.indice).exists():
        idx = construir_indice(a.inventario, a.indice, a.por_grupo, a.lado_minimo)
    else:
        idx = pd.read_csv(a.indice)
    print(idx.groupby(["particion", "calidad"]).size().unstack(fill_value=0))
    print(idx.groupby(["origen", "calidad"]).size().unstack(fill_value=0))
    print("bloques pendientes:", cachear(idx, a.cache, a.lado))
    if not (Path(a.cache) / "propias_recortes.npy").exists():
        print("propias con segmentación:", recortar_propias(idx, a.cache, a.lado).mean())
