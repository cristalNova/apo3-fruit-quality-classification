# Formulación y fundamentos matemáticos

Este documento presenta la formulación matemática del problema y los fundamentos teóricos que sustentan la estrategia de solución, las métricas y el análisis de resultados.

## 1. Formulación del problema

**Entrada.** Una imagen RGB de una fruta individual sobre fondo uniforme: $x \in \mathbb{R}^{H \times W \times 3}$.

**Salidas.**
- Clase de calidad $y_c \in \mathcal{C} = \{\text{Buena}, \text{Regular}, \text{Mala}\}$.
- Tamaño $y_s \in \mathcal{S} = \{\text{Pequeño}, \text{Mediano}, \text{Grande}\}$, obtenido de un diámetro normalizado $d_{norm} \in [0,1]$.
- Contexto: tipo de fruta $f \in \{\text{manzana, banano, guayaba, limón, naranja, granada}\}$.

**Calidad (aprendizaje supervisado).** Dado un conjunto etiquetado $\mathcal{D} = \{(x_i, y_{c,i})\}_{i=1}^{N}$, aprender un clasificador $f_\theta : x \mapsto \hat{y}_c$ que minimice el riesgo empírico

$$\hat{\theta} = \arg\min_\theta \; \frac{1}{N} \sum_{i=1}^{N} \ell\big(f_\theta(x_i), y_{c,i}\big) + \lambda\,\Omega(\theta)$$

con $\ell$ una función de pérdida de clasificación (p. ej. entropía cruzada, posiblemente ponderada por clase) y $\Omega$ un regularizador. El objetivo real es el riesgo esperado sobre datos no vistos (generalización), que se estima con validación y prueba.

**Tamaño (geometría sobre la segmentación).** Sea $M \subset \{1..H\}\times\{1..W\}$ la máscara de la fruta y $A = |M|$ su área en píxeles. El diámetro equivalente y el normalizado son

$$d_{equiv} = \sqrt{\frac{4A}{\pi}}, \qquad d_{norm} = \frac{d_{equiv}}{L}, \quad L = \min(H, W)$$

y la categoría se asigna con umbrales por fruta $\tau_{1}^{(f)} < \tau_{2}^{(f)}$:

$$y_s = \begin{cases} \text{Pequeño} & d_{norm} < \tau_{1}^{(f)} \\ \text{Mediano} & \tau_{1}^{(f)} \le d_{norm} < \tau_{2}^{(f)} \\ \text{Grande} & d_{norm} \ge \tau_{2}^{(f)} \end{cases}$$

**Por qué es un problema complejo de ingeniería.**
- Variabilidad visual dentro de una misma clase (variedad, color, iluminación, ángulo) y fronteras difusas entre clases vecinas (Buena/Regular, Regular/Mala).
- Datos de varios orígenes (dataset público y fotos propias) con posible cambio de dominio.
- Clases desbalanceadas: Regular no tiene etiqueta en el dataset original.
- El tamaño depende del encuadre, porque no hay escala física en las imágenes redimensionadas.
- Requiere decisiones bajo restricciones reales: precisión suficiente, tiempo de respuesta en cámara y costo de hardware.

Los umbrales $\tau$, la función de pérdida $\ell$ y el regularizador $\Omega$ se especifican en las fases de preparación de datos y modelado.

## 2. Estrategia de solución y fundamentos matemáticos

**Representación.** Para los modelos clásicos, cada imagen se resume en un vector $\phi(x) \in \mathbb{R}^{55}$ de histogramas y momentos de color y textura. La red convolucional recibe $x \in [0,1]^{64 \times 64 \times 3}$ y aprende su propia representación.

**SVM.** Con kernel gaussiano $k(u, v) = \exp(-\gamma \lVert u - v \rVert^2)$, resuelve el problema dual de margen blando con parámetro $C$, que regula el equilibrio entre margen y error. Se usa la estrategia uno contra uno para las tres clases y pesos $w_c$ inversamente proporcionales a la frecuencia de cada clase.

**Random Forest.** Promedia los votos de $B$ árboles entrenados con muestras bootstrap y subconjuntos aleatorios de variables; cada división minimiza la impureza de Gini $G = 1 - \sum_c p_c^2$. El promedio reduce la varianza respecto a un árbol individual.

**Red convolucional.** Cada capa calcula $h^{(l+1)} = \sigma(W^{(l)} * h^{(l)} + b^{(l)})$, con $\sigma$ la función ReLU, seguida de normalización por lotes y agrupación máxima. La salida es $\hat{p} = \text{softmax}(z)$ y se minimiza la entropía cruzada ponderada

$$\mathcal{L}(\theta) = -\frac{1}{N} \sum_{i=1}^{N} w_{y_i} \log \hat{p}_{i, y_i}$$

con el optimizador Adam. La ponderación $w_c = N / (3 N_c)$ compensa que Regular sea la clase minoritaria. El dropout y el aumento de datos actúan como regularizadores $\Omega(\theta)$.

**Métricas.** Para cada clase $c$: $\text{precisión}_c = \frac{TP_c}{TP_c + FP_c}$, $\text{exhaustividad}_c = \frac{TP_c}{TP_c + FN_c}$ y $F1_c = \frac{2 \, P_c R_c}{P_c + R_c}$. El F1 macro es el promedio simple de los $F1_c$ y, a diferencia de la exactitud, no queda dominado por la clase mayoritaria. La exactitud de la línea base (clase mayoritaria) es el valor mínimo que debe superar cualquier modelo.

**Selección y generalización.** Los hiperparámetros se eligen maximizando el F1 macro en validación cruzada (modelos clásicos) o en el conjunto de validación (red). El riesgo esperado se estima en un conjunto de prueba que no interviene en la selección y, además, en fotografías propias de una fuente distinta, que miden la robustez ante cambio de dominio: la distribución de las fotos de uso real $P_{uso}(x, y)$ difiere de la de entrenamiento $P_{ent}(x, y)$.

**Tamaño.** Los umbrales $\tau_1^{(f)}, \tau_2^{(f)}$ de cada fruta son los cuantiles 1/3 y 2/3 de $d_{norm}$ sobre una muestra de entrenamiento, de modo que las tres categorías son equiprobables en la muestra. Por construcción, $d_{norm}$ depende del encuadre y no equivale a un diámetro físico.
