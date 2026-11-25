import keras
from keras import layers

CLASES = ["buena", "regular", "mala"]


def construir_cnn(filtros=32, dropout=0.3, lado=64):
    entrada = keras.Input((lado, lado, 3))
    x = layers.Rescaling(1 / 255)(entrada)
    x = layers.RandomFlip("horizontal_and_vertical")(x)
    x = layers.RandomRotation(0.1)(x)
    x = layers.RandomBrightness(0.4, value_range=(0, 1))(x)
    x = layers.RandomContrast(0.3)(x)
    for multiplo in (1, 2, 4):
        x = layers.Conv2D(filtros * multiplo, 3, padding="same", activation="relu")(x)
        x = layers.BatchNormalization()(x)
        x = layers.MaxPooling2D()(x)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(dropout)(x)
    x = layers.Dense(64, activation="relu")(x)
    salida = layers.Dense(len(CLASES), activation="softmax")(x)
    return keras.Model(entrada, salida)
