# Ética

Este documento identifica las situaciones y decisiones del proyecto en las que pueden surgir dilemas o responsabilidades éticas, las relaciona con los principios del código de ética profesional del ingeniero y describe las medidas adoptadas para un desarrollo responsable del sistema.

## Marco de referencia

El análisis se basa en dos códigos de ética profesional:

- El **Código de Ética del IEEE** [1], que compromete a sus miembros, entre otros principios, a velar por la seguridad, la salud y el bienestar del público, aplicar prácticas de diseño ético y desarrollo sostenible, proteger la privacidad de otros, ser honestos y realistas al formular afirmaciones basadas en los datos disponibles, reconocer adecuadamente las contribuciones de otros y tratar a todas las personas con equidad y respeto, sin discriminación.
- La **Ley 842 de 2003** [2], que adopta el Código de Ética Profesional para el ejercicio de la ingeniería en Colombia y establece, en su artículo 33, deberes especiales de los profesionales para con la sociedad.

## Decisiones clave, dilemas y medidas adoptadas

| # | Situación o decisión del proyecto | Dilema o riesgo | Principio del código de ética | Medida adoptada |
|---|---|---|---|---|
| 1 | Recolección de fotografías propias en mercados, supermercados y hogares | Captura accidental de personas, puestos de venta o espacios privados, sin su consentimiento | Protección de la privacidad de otros; deberes para con la sociedad [1], [2] | Encuadre restringido a la fruta sobre fondo uniforme; no se capturan ni almacenan imágenes de personas; autorización previa del responsable del lugar y consentimiento de las personas del hogar cuando corresponda |
| 2 | Definición de las clases de calidad y etiquetado manual | Criterios subjetivos que introducen sesgos y etiquetas inconsistentes | Honestidad y realismo en las afirmaciones basadas en datos [1] | Criterios explícitos y documentados en la fase de comprensión del negocio; guía de anotación escrita y revisión cruzada entre integrantes |
| 3 | Uso de datos y código de terceros (conjunto de Kaggle y anotaciones de otros grupos) | Uso sin atribución o contrario a las condiciones de licencia | Reconocimiento adecuado de las contribuciones de otros; evitar conductas ilícitas [1] | Referencia explícita de toda fuente de datos y de código de terceros; descripción del origen de los datos en `data/README.md`; respeto de las licencias |
| 4 | Entrenamiento y evaluación con clases desbalanceadas y datos de distinto origen | Desempeño desigual entre frutas, clases y condiciones de captura, con mayor error en la clase Regular | Trato equitativo; honestidad en la presentación de resultados [1] | Métricas por clase y por fruta; evaluación separada sobre las fotografías propias; reporte explícito de las limitaciones del sistema |
| 5 | Criterios de calidad que penalizan defectos | Descartar fruta aún consumible por defectos meramente cosméticos, lo que aumenta el desperdicio; los estándares estéticos figuran entre las causas del desperdicio en el comercio minorista [3] | Bienestar del público y prácticas de desarrollo sostenible [1] | Criterios basados en defectos que afectan el consumo y no solo la apariencia; clase intermedia (Regular) que permite aprovechar fruta imperfecta |
| 6 | Uso del sistema como apoyo a decisiones de venta, rebaja o descarte | Errores que perjudiquen el ingreso del vendedor o que dejen pasar fruta en mal estado hacia el consumidor | Seguridad, salud y bienestar del público; honestidad sobre las capacidades y límites del sistema [1], [2] | El sistema actúa como apoyo y no como sustituto de la decisión humana; se reporta la exhaustividad de cada clase, incluida la Mala; las limitaciones se documentan en el informe y en la aplicación |
| 7 | Automatización de una tarea hoy manual | Desplazamiento parcial del trabajo de clasificación | Comprensión de las implicaciones sociales de las tecnologías emergentes, incluidos los sistemas inteligentes [1]; deberes para con la sociedad [2] | Diseño como herramienta de apoyo; análisis de impactos sociales y económicos en la sección 1.8 de [`1_comprension_negocio/README.md`](../1_comprension_negocio/README.md#18-impactos-de-la-solución) |

## Referencias

[1] Institute of Electrical and Electronics Engineers (IEEE), "IEEE Code of Ethics," IEEE Policies, Sec. 7.8. [Online]. Available: https://www.ieee.org/about/corporate/governance/p7-8

[2] Congreso de Colombia, "Ley 842 de 2003, por la cual se modifica la reglamentación del ejercicio de la ingeniería, de sus profesiones afines y de sus profesiones auxiliares, se adopta el Código de Ética Profesional y se dictan otras disposiciones," *Diario Oficial* No. 45.340, Oct. 14, 2003. [Online]. Available: https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=40907

[3] Food and Agriculture Organization of the United Nations (FAO), *The State of Food and Agriculture 2019: Moving Forward on Food Loss and Waste Reduction*. Rome, Italy: FAO, 2019. [Online]. Available: https://openknowledge.fao.org/server/api/core/bitstreams/11f9288f-dc78-4171-8d02-92235b8d7dc7/content
