# INFORME BREVE - ARMARIO INTELIGENTE
**Autora:** Lucía Nistal Palacios  

---

## 1. RESUMEN

Sistema web de recomendación de outfits con análisis de colorimetría mediante visión por computadora.

Python, Flask, OpenCV, NumPy, scikit-learn, gTTS

---

## 2. CAMBIOS vs PLAN INICIAL

### Plan Original → Implementación Final

| Aspecto | Inicial | Final |
|---------|---------|-------|
| **Flujo** | Bienvenida → Cuestionario → Resultados | Bienvenida → Login → Dashboard → Cuestionario/Armario/Historial → Resultados |
| **Autenticación** | NO |  Login/Registro |
| **Persistencia** | NO |  Caché análisis + Historial |
| **Armario personal** | NO |  CRUD completo |
| **Priorización** | Solo BD genérica | Usuario primero → BD fallback |
| **Filtrado** | NO |  Automático por género(cuando alguien descarta falda top y vestido tampoco se reocmienda botas, tacones o bolso)|

**Razón cambios:** Sin sistema de usuarios no se podría guardar análisis  ni personalizar recomendaciones.

---

## 3. PROBLEMAS RESUELTOS 

### 3.1 Análisis colorimetría
-  **RGB:** Sensible a luz →  **CIELAB:** Mejor separación color
-  **Solo piel:** Impreciso → **Piel+ojos+cabello:** Contraste completo

### 3.2 Base de datos
-  **Excel promedios:** 52 provincias

### 3.3 Matching de prendas
-  **Case-sensitive:** "Formal" ≠ "formal" →  **`.lower()`:** Convierte todo a minusculas para que en caso de que el usuario lo escriba de una forma u otra el sistema reconozca
-  **Formato JSON inconsistente** →  **`normalize_field()`:** Detecta y convierte todo a array, esto es en caso de que una prenda añadida por el usuario sirva para varias ocasiones, al principio la misma información se guardaba de formas diferentes en el JSON.

### 3.4 Audio
-  **"combina un camisa"** →  **Función género/número:** "una camisa blanca"

### 3.5 Filtrado Género
-  **Tacones a hombres** →  **Detección automática + filtrado**  Solo en caso de que marque como incómodo vestidos top y faldas

---

## 4. ESTRUCTURA PROYECTO

```
armario-inteligente/
├── app.py                    # Servidor Flask
├── colorimetry_analyzer.py   # OpenCV + K-means + CIELAB
├── clothing_database.py      # BD 91 prendas
├── outfit_generator.py       # Matching + TTS
├── wardrobe_manager.py       # CRUD armario
├── requirements.txt
│
├── data/
│   ├── clothing_items.json  # BD genérica
│   ├── clima_provincias.xlsx
│   ├── wardrobes/           # Armarios usuarios
│   ├── history/             # Historial
│   └── colorimetry/         # Caché análisis
│
├── static/
│   ├── css/, js/
│   ├── clothing_images/     # 91 imágenes BD
│   └── audio/               # MP3 generados
│
└── templates/
    └── *.html               # 9 páginas
```

---

## 5. INSTRUCCIONES EJECUCIÓN

### Instalación:
```bash
cd armario-inteligente
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Ejecutar:
```bash
python app.py
```
Abrir: `http://localhost:5003`

### Datos de prueba:
- **Email:** test@example.com
- **Pass:** test123

### Requisitos foto:
- Buena iluminación
- Fondo neutro
- Rostro visible

---

## 6. COMPONENTES CLAVE

### 6.1 Análisis Colorimetría
```
Foto → Detección rostro (Haar Cascade) → Extraer ROIs (piel/ojos/cabello)
     → K-means clustering → CIELAB subtono → Contraste + Saturación
     → Clasificar estación: Primavera/Verano/Otoño/Invierno
```

**Matriz decisión:**
- Cálido + bajo contraste + alta saturación = **Primavera**
- Cálido + alto contraste + baja saturación = **Otoño**
- Frío + bajo contraste + baja saturación = **Verano**
- Frío + alto contraste + alta saturación = **Invierno**

### 6.2 Generación Outfit
```
1. Buscar en ARMARIO USUARIO (prioridad)
   ├─ Verificar: ocasión + clima + colores + preferencias
   └─ ¿Encontró? → Usar prenda usuario
   
2. Si no → Buscar en BASE DATOS (91 prendas)
   ├─ Aplicar filtros género
   └─ Scoring por paleta colores
   
3. Seleccionar: Superior + Inferior (o Vestido) + Calzado + Complemento
```

**Reglas especiales:**
- Vestido → No buscar superior/inferior
- Lluvia >60% → Botas
- Temp <10°C → Bufanda/gorro

---

## 7. DEPENDENCIAS (requirements.txt)

```
Flask==2.3.0
opencv-python==4.8.0
numpy==1.24.3
scikit-learn==1.3.0
Pillow==10.0.0
pandas==2.0.3
openpyxl==3.1.2
gTTS==2.3.2
bcrypt==4.0.1
```

---

## 8. ALGORITMO PRIORIZACIÓN DE LAS PRENDAS (Evolución)

### Versión 1 (descartada):
```python
if prenda['ocasion'] == ocasion:
    return True
```
**Problema:** No consideraba clima ni colorimetría

### Versión 2 (mejorada):
```python
if match_ocasion and match_clima and match_estacion:
    return True
```
**Problema:** Muy restrictivo

### Versión 3 (actual):
```python
score = 0
if match_ocasion: score += 50    
if match_clima: score += 30     
if match_estacion: score += 20   
return score >= 50
```
**Ventaja:** Flexible + requisitos críticos, realmente se parece a la sgeunda pero no es tan estricta y no tiene por qué cumplirse TODO si o si, porque como la base de datos es limitada ( es el armario de la persona) puede haber prendas que no cumplas todo al 100% pero si de la mejor manera, lo minimo es que cumpla con la ocasión. Si no llega a ese minimo de puntos, el sistema pasa a buscar una prenda en la base de datos genérica. 
De esta forma se consigue priorizar las prendas del armario del usuario.

---

## 9. LIMITACIONES

1. **Análisis:** Sensible a iluminación extrema
2. **Clima:** Promedios históricos, no tiempo real
3. **BD:** 91 prendas genéricas (base de dato no muy grande, el usuario puede añadir)
4. **Foto:** Solo rostro, una persona



## 10. CONCLUSIÓN

Proyecto que cumple con los objetivos marcados en un inicio. Y con cambios respecto al plan inicial que mejoraron la personalización y utilidad. El desarrollo iterativo permitió identificar y resolver problemas técnicos, resultando en un sistema robusto que combina CV, análisis datos y síntesis voz.

**Logros principales:**
- Sistema funcional 
- Análisis colorimetría científicamente fundamentado
- Priorización inteligente usuario/BD
- Filtrado por género e inclusividad
- Audio gramaticalmente correcto
- Interfaz intuitiva

