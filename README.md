#  Sistema de Recomendación de Moda Inteligente

Se trata de un sistema web que analiza tu colorimetría personal mediante una foto y te recomienda outfits adaptados al clima y a tus preferencias.


## ¿Qué hace?

1. **Analiza tu foto**  Detecta tu tono de piel, color de ojos y cabello
2. **Determina tu colorimetría**  Te clasifica en Primavera, Verano, Otoño o Invierno
3. **Recomienda outfits** Sugiere prendas según el clima, ocasión y colores que te favorecen
4. **Te lo explica por voz**  Genera audio describiendo el outfit recomendado

---

##  Instalación Rápida

### 1. Requisitos
- Archivo : requirements.txt


### 2. Instalar

```bash
# Clonar repositorio
git clone https://github.com/lucianistal/armario-inteligente.git
cd armario-inteligente

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  

# Instalar dependencias
pip install -r requirements.txt

# Crear las carpetas que sean necesarias
mkdir -p data/wardrobes data/history data/colorimetry
mkdir -p static/audio static/user_clothing
```

### 3. Ejecutar

```bash
python3 app.py
```

Abrir navegador en: `http://localhost:5003`

---

##  Estructura del Proyecto

```
armario-inteligente/
├── app.py                      # Servidor Flask
├── colorimetry_analyzer.py     # Análisis de colorimetría
├── clothing_database.py        # Base de datos de prendas
├── outfit_generator.py         # Generación de outfits + voz
├── wardrobe_manager.py         # Armario virtual
├── requirements.txt            # Dependencias
│
├── data/
│   ├── clothing_items.json    # casi 100 prendas
│   ├── clima_provincias.xlsx  # Datos climáticos por meses y provincias
│   └── wardrobes/             # Armarios de usuarios
│
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   ├── clothing_images/       # Fotos de prendas
│   └── audio/                 # Audios generados
│
└── templates/
    └── *.html                 # Páginas 
```

---

##  Cómo Funciona

### Análisis de Colorimetría

El sistema analiza tres características de tu rostro:

1. **Tono de piel** → Usa CIELAB para detectar si es cálido o frío
2. **Color de ojos** → Clasifica en claro u oscuro
3. **Color de cabello** → Determina rubio, castaño, negro, pelirrojo

Con esta información calcula:
- **Contraste:** Diferencia entre piel y cabello
- **Saturación:** Intensidad de los colores

Y te clasifica en una estación:

| Estación | Características |
|----------|----------------|
| **Primavera** | Cálido + bajo contraste + alta saturación |
| **Verano** | Frío + bajo contraste + baja saturación |
| **Otoño** | Cálido + alto contraste + baja saturación |
| **Invierno** | Frío + alto contraste + alta saturación |

### Generación de Outfits

El sistema:
1. Busca primero en TU armario virtual (es decir, si has añadido una prenda la priorizará ante otras)
2. Si no encuentra, usa la base de datos 
3. Filtra por género, clima y ocasión
4. Prioriza colores de tu paleta 
5. Genera narrativa y la convierte a audio 

---

## Tecnologías

- **Python 3.8+** - Lenguaje principal
- **Flask** - Servidor web
- **OpenCV** - Análisis de imagen
- **NumPy** - Procesamiento numérico
- **scikit-learn** - Clustering K-means
- **gTTS** - Síntesis de voz
- **pandas** - Datos climáticos

---

##  Uso Básico

### 1. Registro
Crea una cuenta con tu email y contraseña.

### 2. Cuestionario (8 pasos)
- Nombre y género
- Provincia y mes
- Ocasión (formal/casual/deportiva)
- Preferencias de ajuste
- Prendas a evitar
- Foto de tu rostro
- Confirmar

### 3. Ver Resultados
- Paleta de colores personalizada
- Outfit recomendado con imágenes
- Explicación por voz
- Detalles del análisis

### 4. Armario Virtual (Opcional)
- Añade tus propias prendas
- El sistema priorizará esas prendas en recomendaciones

