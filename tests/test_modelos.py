import numpy as np

from src.evaluation.metricas import resumen
from src.features.caracteristicas import caracteristicas
from src.features.tamano import categoria
from src.models.cnn import construir_cnn


def test_categoria_usa_los_umbrales_por_fruta():
    umbrales = [0.4, 0.6]
    assert categoria(0.3, umbrales) == "pequeño"
    assert categoria(0.5, umbrales) == "mediano"
    assert categoria(0.9, umbrales) == "grande"


def test_caracteristicas_tiene_55_variables_sin_nan():
    imagenes = np.random.default_rng(0).integers(0, 256, (3, 64, 64, 3), dtype=np.uint8)
    x = caracteristicas(imagenes)
    assert x.shape == (3, 55)
    assert not np.isnan(x).any()


def test_resumen_ignora_clases_ausentes_en_el_f1_macro():
    r = resumen(np.array(["buena", "buena", "regular"]), np.array(["buena", "buena", "regular"]))
    assert r["f1_macro"] == 1.0


def test_cnn_produce_tres_probabilidades():
    salida = construir_cnn(8)(np.zeros((2, 64, 64, 3), dtype="float32"))
    assert salida.shape == (2, 3)
    assert np.allclose(np.asarray(salida).sum(1), 1, atol=1e-5)
