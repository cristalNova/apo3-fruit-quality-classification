# Guía de anotación de calidad

Esta guía establece los criterios con los que se asigna la clase de calidad (**Buena**, **Regular** o **Mala**) a cada fruta del proyecto. Se aplica por igual a las imágenes de *Fruit Quality Classification* y a las imágenes propias, y se aplicaría también a las frutas segmentadas de la carpeta *Mixed quality* si se incorporan. El objetivo es que cualquier integrante, o cualquier otro grupo que aporte anotaciones, llegue a la misma etiqueta para la misma fruta.

## 1. Imágenes anotables

Una imagen se anota solo si cumple las siguientes condiciones:

- contiene una única fruta completa y visible, sobre un fondo simple y uniforme;
- tiene nitidez y resolución suficientes para distinguir la textura de la piel y los defectos;
- presenta una iluminación que permite apreciar el color real de la fruta (no está subexpuesta ni sobreexpuesta);
- el color de la imagen no está alterado de forma evidente (dominantes azules o violetas, filtros).

Las imágenes que no cumplen estas condiciones se excluyen del conjunto anotado y no se les asigna clase. Una mano que sostiene la fruta no excluye la imagen si el fondo es uniforme y la fruta es claramente visible; la mano no se considera parte de la fruta.

## 2. Criterio general por clase

| Clase | Criterio | Decisión de negocio |
|---|---|---|
| **Buena** | Piel íntegra, forma regular y color propio de la fruta en estado comercial o de consumo. Sin manchas, golpes, moho ni deformaciones apreciables. | Venta normal |
| **Regular** | Defectos leves y localizados que afectan hasta el **20 %** de la superficie visible, o madurez claramente avanzada o insuficiente, sin signos de descomposición. La piel permanece cerrada. | Venta con descuento o uso inmediato |
| **Mala** | Presencia de moho o pudrición (con cualquier extensión), piel rota o abierta, zonas blandas o necrosadas, o defectos que afectan más del **20 %** de la superficie visible. | Descarte |

### 2.1 Reglas de aplicación

1. **Signos de descomposición.** El moho, la pudrición, la piel rota o abierta y las zonas blandas o necrosadas clasifican la fruta como **Mala** sin importar el porcentaje de superficie afectada.
2. **Porcentaje de superficie.** La extensión del defecto se estima sobre la superficie visible de la fruta en la imagen. En caso de que se observen varias caras (por ejemplo, en imágenes de varias vistas), se considera la cara más afectada.
3. **Color y variedad.** La variación de color propia de la especie o de la variedad no constituye un defecto: manzanas y granadas pueden ser rojas, amarillentas o bicolores, y el limón puede ser verde o amarillo. El color solo se considera defecto cuando evidencia deterioro (oscurecimiento, zonas pardas, manchas).
4. **Madurez.** La madurez avanzada o insuficiente clasifica como **Regular** mientras la fruta conserve piel íntegra y no presente signos de descomposición; si hay ablandamiento, fermentación o piel dañada, clasifica como **Mala**.
5. **Duda entre dos clases.** Cuando la fruta no se puede asignar con certeza a una de dos clases contiguas, se asigna la de mayor severidad. Esta regla es coherente con la métrica prioritaria del proyecto, que es no dejar pasar frutas de clase Mala.
6. **Independencia del origen.** La clase depende únicamente del estado de la fruta, no de la fuente, el fondo, la resolución ni la cámara de la imagen.

## 3. Defectos de referencia por fruta

| Fruta | Regular (leve, localizado) | Mala (severo) |
|---|---|---|
| **Manzana** | Magulladuras o manchas pardas pequeñas, rugosidad leve, piel con punteado; ablandamiento incipiente sin rotura. | Zonas oscuras y blandas extensas, piel arrugada o rota, lesiones profundas, moho. |
| **Banano** | Manchas pardas pequeñas dispersas (maduración avanzada) o color verdoso por inmadurez, con cáscara íntegra. | Cáscara mayormente negra o parda, zonas blandas o húmedas, cáscara rota, moho. |
| **Naranja** | Manchas superficiales pequeñas, piel opaca o con decoloración parcial; tono verdoso por maduración incompleta. | Moho blanco o verdeazulado, zonas pardas extensas y blandas, piel hundida o rota. |
| **Limón** | Manchas pardas o cicatrices pequeñas en la piel, sin ablandamiento. | Moho, zonas pardas o rosadas extensas, extremos blandos o hundidos, piel rota. |
| **Guayaba** | Pequeñas manchas oscuras o magulladuras localizadas, con piel íntegra. | Manchas oscuras extensas, zonas blandas, piel rota, moho. |
| **Granada** | Pequeñas manchas o raspaduras en la cáscara, sin grietas. | Cáscara agrietada o abierta con arilos expuestos, oscurecimiento extenso, zonas secas o podridas, moho. |

## 4. Registro de la anotación

Cada fruta anotada se registra en `data/propias/anotaciones.csv` con las columnas `archivo`, `fruta` y `calidad` (véase [`data/README.md`](../data/README.md)). Los valores de `calidad` son exactamente `buena`, `regular` o `mala`; las imágenes excluidas por la sección 1 no se registran.
