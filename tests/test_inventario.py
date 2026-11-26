from pathlib import Path

from PIL import Image

from src.data.inventario import calidad_y_fruta, catalogar, marcar_duplicados_exactos, tipo_archivo


def test_tipo_archivo():
    assert tipo_archivo("Captura de pantalla 2026-06-03 114050.png") == "captura"
    assert tipo_archivo("rotated_by_15_Screen Shot 2018.png") == "aumentada"
    assert tipo_archivo("guava_bad18_aug_9.jpg") == "aumentada"
    assert tipo_archivo("IMG_1887.jpg") == "original"


def testcalidad_y_fruta():
    assert calidad_y_fruta(("bad", "Apple_Bad", "Apple_Bad", "a.jpg")) == ("mala", "manzana")
    assert calidad_y_fruta(("good", "limon", "b.jpg")) == ("buena", "limon")
    assert calidad_y_fruta(("Bad Quality_Fruits", "Lime_Bad", "c.jpg")) == ("mala", "limon")
    assert calidad_y_fruta(("Mixed Qualit_Fruits", "Lemon", "d.jpg")) == ("mezclada", "limon")


def test_catalogar_y_duplicados(tmp_path: Path):
    for carpeta, nombre in [("good/Apple_Good", "a.jpg"), ("regular/Apple_Regular", "b.jpg")]:
        destino = tmp_path / carpeta
        destino.mkdir(parents=True)
        Image.new("RGB", (40, 30), (200, 30, 30)).save(destino / nombre)
    df = catalogar("prueba", tmp_path)
    assert len(df) == 2
    assert set(df["calidad"]) == {"buena", "regular"}
    assert (df["fruta"] == "manzana").all()
    assert (df["lado_mayor"] == 40).all()
    df = marcar_duplicados_exactos(df)
    assert df["duplicado_exacto"].sum() == 1
