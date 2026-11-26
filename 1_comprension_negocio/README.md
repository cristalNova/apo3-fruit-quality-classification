# 1. Comprensión del negocio

Esta fase establece el problema, su contexto y su importancia, el alcance del sistema, las definiciones de las variables de salida, los criterios de evaluación, el análisis inicial de impactos y las consideraciones éticas iniciales.

## 1.1 Contexto y problema

En mercados, plazas y agroindustrias, la clasificación de productos frescos según su madurez, tamaño y defectos visibles se realiza de forma manual. Se trata de un proceso **lento, subjetivo y propenso a errores**: dos personas pueden clasificar de manera distinta la misma fruta, y el criterio varía con el cansancio o la hora del día. Esta situación genera pérdidas económicas, desperdicio de alimentos y falta de estandarización entre productores, mayoristas y vendedores.

El proyecto desarrolla un sistema de visión por computadora que, a partir de una fotografía de **una fruta individual sobre fondo simple y uniforme**, entrega:

1. su **clase de calidad** (Buena, Regular o Mala), y
2. su **tamaño** (Pequeño, Mediano o Grande).

El sistema se despliega en una interfaz gráfica que permite cargar una imagen o utilizar la cámara en tiempo real.

**Partes interesadas:** vendedores y compradores en plazas de mercado y supermercados, pequeños y medianos productores, centros de acopio y empacadoras, y consumidores finales.

## 1.2 Importancia del problema

La pérdida y el desperdicio de alimentos constituyen un problema de escala mundial, con especial incidencia en frutas y hortalizas:

- A nivel mundial, alrededor del **14 %** de los alimentos producidos (13,8 % en 2016) se pierde desde la finca hasta el comercio minorista, sin incluirlo, y los niveles de pérdida son, en general, mayores en frutas y hortalizas que en cereales y legumbres [1].
- En 2022 se desperdiciaron **1.050 millones de toneladas** de alimentos, equivalentes al **19 %** de los alimentos disponibles para los consumidores en los niveles minorista, de servicios de alimentación y hogares. Esta cifra se suma al 13 % de los alimentos que se pierde en la cadena de suministro, desde la poscosecha hasta el comercio minorista, sin incluirlo [2].
- La pérdida y el desperdicio de alimentos generan entre el **8 % y el 10 %** de las emisiones mundiales de gases de efecto invernadero [2].
- En Colombia, el estudio del Departamento Nacional de Planeación (DNP) publicado en 2016 estima que cada año se pierden o desperdician **9,76 millones de toneladas** de alimentos, equivalentes al **34 %** de la oferta nacional disponible, estimada en 28,5 millones de toneladas. Las frutas y verduras representan el **62 %** de ese total [3].

En este contexto, la clasificación de la calidad en los puntos de la cadena donde se decide si un producto se vende, se rebaja o se descarta constituye una oportunidad para estandarizar y mejorar esas decisiones. Las cifras anteriores describen la magnitud del problema; no constituyen una estimación de la reducción que logra el sistema.

## 1.3 Alcance

El sistema considera las seis frutas del conjunto de datos de referencia: manzana, banano, guayaba, limón, naranja y granada. Las fotografías propias con una sola fruta y una sola calidad son 106 y cubren tres de las seis frutas (manzana 64, limón 25 y naranja 17), por lo que los resultados se reportan también de forma desagregada por fruta.

## 1.4 Clases de calidad

Se definen tres clases, comunes a todas las frutas:

| Clase | Criterio | Decisión de negocio asociada |
|---|---|---|
| **Buena** | Sin defectos visibles relevantes; color y forma propios de una fruta en buen estado de consumo. | Venta normal |
| **Regular** | Defectos leves: manchas pequeñas, golpes superficiales, madurez avanzada o insuficiente, pero aún aprovechable. | Venta con descuento o uso inmediato |
| **Mala** | Podredumbre, moho, golpes profundos o deformaciones severas; no apta para consumo. | Descarte |

**Correspondencia con las etiquetas del conjunto de referencia:**

| Origen | Etiqueta original | Clase del proyecto |
|---|---|---|
| Carpeta `Good Quality_Fruits` | Calidad buena | **Buena**, previa verificación visual |
| Carpeta `Bad Quality_Fruits` | Calidad mala | **Mala**, previa verificación visual |
| Carpeta `Mixed Qualit_Fruits` | Varias frutas por imagen, con calidades mezcladas | No se usa en esta versión: exige segmentar cada fruta y etiquetarla por recorte (trabajo futuro) |
| Imágenes propias | No aplica | Se etiquetan manualmente con los mismos criterios |

El conjunto de referencia distingue únicamente entre calidad buena y mala. Por ello, la clase **Regular** no cuenta con etiquetas originales y proviene de las imágenes compartidas por otros grupos y de las fotografías adicionales; las fotografías propias aportan solo 10 regulares, reservadas como prueba externa. Esta particularidad constituye el principal riesgo de desbalanceo del proyecto (véase la sección 1.7).

Los criterios operativos de cada clase, incluido el umbral del 20 % de superficie afectada que separa Regular de Mala, se detallan en la [guía de anotación](../2_comprension_datos/guia_anotacion.md).

## 1.5 Tamaño

El tamaño se estima como un **diámetro normalizado** que luego se agrupa en tres categorías:

1. Se **segmenta** la fruta, separándola del fondo.
2. Se calcula el diámetro equivalente de la máscara y se divide por el lado de la imagen: `d_norm = d_equiv / L`.
3. Se asigna la categoría **Pequeño**, **Mediano** o **Grande** mediante umbrales **definidos por fruta**, dado que los tamaños de frutas distintas no son comparables entre sí.

Las imágenes de las carpetas *Good* y *Bad* del conjunto de referencia miden 256×256 píxeles (las de *Mixed*, que no se usan, 256×192), por lo que se pierde la escala física y el valor obtenido es relativo al encuadre. La formulación completa se presenta en [`docs/formulacion_matematica.md`](../docs/formulacion_matematica.md).

## 1.6 Métricas de éxito

**Técnicas.** Los valores objetivo se establecen a partir de la línea base obtenida en la fase de evaluación.
- *Calidad:* exactitud (accuracy), precisión, exhaustividad (recall) y F1 por clase, y matriz de confusión. Dado el desbalanceo de clases, se priorizan el **F1 macro** y el **recall de la clase Mala**, porque clasificar como aceptable una fruta en mal estado tiene mayor costo que revisar una fruta en buen estado.
- *Tamaño:* exactitud de la categoría y error de `d_norm` sobre un subconjunto con medida de referencia.
- *Generalización:* desempeño sobre las imágenes propias, de distinto origen y condiciones, frente al desempeño sobre el conjunto de referencia.

**De negocio.** Se busca reducir la subjetividad y el tiempo por fruta frente al proceso manual, así como disminuir el desperdicio causado por errores de clasificación. Este aspecto se analiza de forma cualitativa en el informe.

## 1.7 Riesgos identificados

| Riesgo | Efecto | Mitigación |
|---|---|---|
| Clase **Regular** con pocas muestras | Desbalanceo; el modelo rara vez predice esta clase | Priorizar su recolección y etiquetado; ponderación por clase y aumento de datos |
| Fotografías propias de solo tres frutas (manzana, limón y naranja), con las 10 regulares todas naranjas | Cobertura limitada por fruta y clase confundida con la fruta | Reportar resultados por fruta y ampliar la recolección (trabajo futuro) |
| Criterios de calidad subjetivos | Etiquetas inconsistentes | Guía de anotación escrita y revisión cruzada entre integrantes |
| Cambio de dominio entre el conjunto de referencia y las fotografías propias | Buen desempeño en el conjunto público y bajo desempeño en condiciones reales | Evaluación por separado sobre las fotografías propias |
| Tamaño sin escala física | `d_norm` no comparable entre imágenes | Documentación de la limitación |
| Varias vistas del mismo ejemplar en el conjunto de referencia (frontal, superior, posterior, inferior y rotada) | Fuga de datos entre entrenamiento y prueba y métricas infladas | No hay identificador de ejemplar, por lo que la partición es aleatoria por archivo (véase la fase 3); la evaluación sobre las fotografías propias no depende de esa partición. Agrupar por ejemplar con hash perceptual queda como trabajo futuro |

## 1.8 Impactos de la solución

Análisis inicial de los impactos potenciales del sistema en las dimensiones social, económica, ambiental y global, con las estrategias propuestas para mitigar los riesgos identificados.

| Dimensión | Impactos positivos | Riesgos | Mitigación |
|---|---|---|---|
| **Social** | Criterios de clasificación consistentes y explícitos para vendedores, compradores y productores; apoyo a la decisión de vender, rebajar o descartar. | Desplazamiento parcial del trabajo manual de clasificación. Errores de clasificación que afecten el ingreso del vendedor o la confianza del comprador. Privacidad y percepción de vigilancia: las fotografías tomadas en mercados pueden captar personas o puestos de venta. | El sistema actúa como apoyo y no como sustituto de la decisión humana. En la recolección, el encuadre se restringe a la fruta, no se capturan ni almacenan imágenes de personas y se solicita autorización previa en los puntos de toma. |
| **Económica** | Contexto de pérdidas significativas en frutas y verduras [3]. Posible reducción de errores de decisión y del tiempo por fruta. Aplicaciones comerciales en centros de acopio, empacadoras y supermercados. | Costos de equipo (cámara y computador o dispositivo de borde), de desarrollo, de mantenimiento y de reentrenamiento ante nuevas variedades. Barrera de acceso para pequeños productores. | Uso de hardware de bajo costo (cámara web o teléfono celular) y de software abierto; modelos de tamaño reducido. |
| **Ambiental** | La pérdida y el desperdicio de alimentos generan entre el 8 % y el 10 % de las emisiones globales de gases de efecto invernadero [2]; clasificar mejor puede favorecer el aprovechamiento de fruta aún consumible (clase Regular). El efecto no se cuantifica en este proyecto. | Consumo energético del entrenamiento y de la inferencia en tiempo real; fabricación y vida útil del hardware. | Arquitecturas pequeñas, inferencia por imagen sin procesamiento continuo innecesario y reutilización de equipos existentes. |
| **Global** | Metodología replicable en otros mercados y frutas. | Las variedades y las condiciones visuales de la fruta varían entre regiones, y el conjunto de referencia puede no representarlas. Los criterios y las normas de calidad difieren entre países y mercados. La necesidad de cumplir estándares estéticos de color, forma y tamaño en el comercio minorista figura entre las causas del desperdicio [1]; un clasificador que penalice defectos meramente cosméticos podría aumentar los descartes. | Criterios de calidad basados en defectos que afectan el consumo y no solo la apariencia; clase intermedia que permite aprovechar fruta imperfecta; reevaluación y recalibración de umbrales al cambiar de mercado o variedad. |

## 1.9 Consideraciones éticas iniciales

Desde esta fase se identifican tres situaciones con implicaciones éticas:

1. **Privacidad y consentimiento** en la recolección de fotografías en mercados, supermercados y hogares, donde pueden aparecer personas o espacios privados.
2. **Subjetividad de los criterios de calidad y de las etiquetas**, que puede introducir sesgos en los datos y, por tanto, en el modelo.
3. **Penalización de defectos meramente cosméticos**, que puede aumentar el descarte de fruta consumible.

El análisis completo, con su relación con el código de ética profesional y las medidas adoptadas a lo largo del proyecto, se presenta en [`docs/etica.md`](../docs/etica.md).

## Referencias

[1] Food and Agriculture Organization of the United Nations (FAO), *The State of Food and Agriculture 2019: Moving Forward on Food Loss and Waste Reduction*. Rome, Italy: FAO, 2019. [Online]. Available: https://openknowledge.fao.org/server/api/core/bitstreams/11f9288f-dc78-4171-8d02-92235b8d7dc7/content

[2] United Nations Environment Programme (UNEP), "Food Waste Index Report 2024: Key messages," Nairobi, Kenya, 2024. [Online]. Available: https://wedocs.unep.org/bitstream/handle/20.500.11822/45275/Food-Waste-Index-2024-key-messages.pdf

[3] Departamento Nacional de Planeación (DNP), "El DNP se une con las centrales de abastos para fortalecer los procesos logísticos y la reducción de pérdida de alimentos," Bogotá, Colombia, Dec. 19, 2024. [Online]. Available: https://dnp.gov.co/Prensa_/Noticias/Paginas/el-dnp-se-une-con-las-centrales-de-abastos-para-fortalecer-los-procesos-logisticos-y-la-reduccion-de-perdida-de-alimentos.aspx
