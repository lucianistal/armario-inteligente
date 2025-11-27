import cv2
import numpy as np
from sklearn.cluster import KMeans

class ColorimetryAnalyzer:
    """
    Sistema PROFESIONAL de colorimetría con análisis completo:
    - PIEL (subtono CIELAB)
    - OJOS (color HSV + categorización)
    - CABELLO (color HSV + categorización)
    - CONTRASTE (diferencia luminosidad)
    - SATURACIÓN (intensidad colores)
    """
    
    def __init__(self):
        cascade_path = cv2.data.haarcascades
        self.face_cascade = cv2.CascadeClassifier(
            cascade_path + 'haarcascade_frontalface_default.xml'
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cascade_path + 'haarcascade_eye.xml'
        )
        
        # ✨ PALETAS PROFESIONALES CORRECTAS (códigos HEX)
        self.paletas = {
            "Primavera": {
                "colores": [
                    "#FFD700",  # Amarillo dorado
                    "#FF6347",  # Naranja coral
                    "#90EE90",  # Verde claro
                    "#FFB6C1",  # Rosa claro
                    "#FFDAB9",  # Melocotón
                    "#98FB98",  # Verde menta
                    "#F0E68C",  # Amarillo cálido
                    "#FFA07A"   # Salmón
                ],
                "descripcion": "Tonos cálidos y vibrantes (amarillos, naranjas, verdes claros, rosas)",
                "colores_texto": ["amarillo dorado", "naranja coral", "verde claro", "rosa claro", "melocotón", "verde menta"]
            },
            "Verano": {
                "colores": [
                    "#B0E0E6",  # Azul claro
                    "#FFB6C1",  # Rosa pastel
                    "#F5DEB3",  # Beige nude
                    "#E6E6FA",  # Lavanda
                    "#AFEEEE",  # Turquesa claro
                    "#FFFACD",  # Amarillo muy claro
                    "#D8BFD8",  # Violeta claro
                    "#B2DFDB"   # Verde agua
                ],
                "descripcion": "Tonos suaves y fríos (azules claros, rosas pastel, lavanda, verde agua)",
                "colores_texto": ["azul claro", "rosa pastel", "beige nude", "lavanda", "turquesa claro", "verde agua"]
            },
            "Otoño": {
                "colores": [
                    "#8B4513",  # Marrón
                    "#FF8C00",  # Naranja oscuro
                    "#556B2F",  # Verde oliva
                    "#F5DEB3",  # Beige cálido
                    "#CD853F",  # Bronce
                    "#A0522D",  # Siena
                    "#DC143C",  # Rojo
                    "#B8860B"   # Dorado oscuro
                ],
                "descripcion": "Tonos tierra y cálidos (marrones, naranjas, verdes oliva, beige, rojo, bronce)",
                "colores_texto": ["marrón", "naranja", "verde oliva", "beige cálido", "rojo", "bronce"]
            },
            "Invierno": {
                "colores": [
                    "#000000",  # Negro
                    "#FFFFFF",  # Blanco
                    "#C0C0C0",  # Gris plateado
                    "#000080",  # Azul marino
                    "#4682B4",  # Azul acero
                    "#2E8B57",  # Esmeralda
                    "#696969",  # Gris oscuro
                    "#191970"   # Azul medianoche
                ],
                "descripcion": "Tonos fríos e intensos (negro, blanco, grises, azules profundos, esmeralda)",
                "colores_texto": ["negro", "blanco", "gris", "azul marino", "azul acero", "esmeralda"]
            }
        }
    
    def analyze_image(self, image_path):
        """Pipeline completo de análisis profesional"""
        try:
            print(f"📸 Cargando imagen: {image_path}")
            img = cv2.imread(image_path)
            if img is None:
                print("❌ No se pudo cargar la imagen")
                return self._get_default_result()
            
            # 1. Normalización de iluminación
            print("💡 Normalizando iluminación...")
            img = self._normalize_illumination(img)
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) == 0:
                print("❌ No se detectó rostro")
                return self._get_default_result()
            
            print(f"✅ Rostro detectado: {len(faces)} cara(s)")
            (x, y, w, h) = faces[0]
            face_roi = img[y:y+h, x:x+w]
            gray_face = gray[y:y+h, x:x+w]
            
            # 2. Análisis de PIEL
            print("👤 Analizando tono de piel...")
            skin_tone, skin_lightness, skin_lab = self._analyze_skin_tone_cielab(face_roi)
            print(f"   Piel: {skin_tone} (L={int(skin_lightness)})")
            
            # 3. Análisis de OJOS
            print("👁️  Analizando color de ojos...")
            eye_analysis = self._analyze_eye_color(face_roi, gray_face)
            eye_category = self._categorize_eye_color(eye_analysis)
            print(f"   Ojos: {eye_category}")
            
            # 4. Análisis de CABELLO
            print("💇 Analizando color de cabello...")
            hair_color = self._analyze_hair_color(img, (x, y, w, h))
            hair_category = self._categorize_hair_color(hair_color)
            print(f"   Cabello: {hair_category}")
            
            # 5. Cálculo de CONTRASTE y SATURACIÓN
            print("📊 Calculando contraste y saturación...")
            contrast = self._calculate_contrast(skin_lightness, eye_analysis, hair_color)
            saturation = self._calculate_saturation(eye_analysis, hair_color)
            print(f"   Contraste: {contrast}, Saturación: {saturation}")
            
            # 6. CLASIFICACIÓN EN ESTACIÓN
            print("🎨 Clasificando en estación...")
            season = self._classify_season_professional(
                skin_tone, eye_analysis, hair_color, contrast, saturation
            )
            print(f"✅ RESULTADO: {season}")
            
            return {
                'season': season,
                'skin_tone': skin_tone,
                'skin_lightness': int(skin_lightness),
                'skin_lab': {
                    'L': int(skin_lab[0]),
                    'a': int(skin_lab[1]),
                    'b': int(skin_lab[2])
                },
                'eye_color': {
                    'category': eye_category,
                    'hue': eye_analysis['hue'],
                    'saturation': eye_analysis['saturation'],
                    'value': eye_analysis['value']
                },
                'hair_color': {
                    'category': hair_category,
                    'hue': hair_color['hue'],
                    'saturation': hair_color['saturation'],
                    'value': hair_color['value']
                },
                'contrast': contrast,
                'saturation': saturation,
                'palette': self.paletas[season]['colores'],
                'palette_description': self.paletas[season]['descripcion'],
                'palette_names': self.paletas[season]['colores_texto'],
                'confidence': 0.90,
                'detailed_analysis': {
                    'skin': f"Subtono {skin_tone}",
                    'eyes': f"Ojos {eye_category}",
                    'hair': f"Cabello {hair_category}",
                    'conclusion': f"Clasificación: {season}"
                }
            }
            
        except Exception as e:
            print(f"❌ Error crítico: {e}")
            import traceback
            traceback.print_exc()
            return self._get_default_result()
    
    def _normalize_illumination(self, img):
        """Normalización con CLAHE"""
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        return cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)
    
    def _analyze_skin_tone_cielab(self, face_roi):
        """Análisis profesional de subtono con CIELAB"""
        h, w = face_roi.shape[:2]
        
        # ROIs de piel optimizadas
        forehead = face_roi[int(h*0.15):int(h*0.35), int(w*0.25):int(w*0.75)]
        left_cheek = face_roi[int(h*0.45):int(h*0.65), int(w*0.1):int(w*0.4)]
        right_cheek = face_roi[int(h*0.45):int(h*0.65), int(w*0.6):int(w*0.9)]
        
        skin_pixels = []
        for region in [forehead, left_cheek, right_cheek]:
            if region.size > 0:
                lab = cv2.cvtColor(region, cv2.COLOR_BGR2LAB)
                pixels = lab.reshape(-1, 3)
                # Filtrar outliers
                mask = (pixels[:, 0] > 50) & (pixels[:, 0] < 220)
                skin_pixels.extend(pixels[mask])
        
        skin_pixels = np.array(skin_pixels)
        mean_l = np.mean(skin_pixels[:, 0])
        mean_a = np.mean(skin_pixels[:, 1])
        mean_b = np.mean(skin_pixels[:, 2])
        
        # Clasificación profesional
        warmth = mean_b - mean_a
        if warmth > 5:
            subtono = 'warm'
        elif warmth < -5:
            subtono = 'cool'
        else:
            subtono = 'neutral'
        
        return subtono, mean_l, np.array([mean_l, mean_a, mean_b])
    
    def _analyze_eye_color(self, face_roi, face_gray):
        """Análisis profesional de color de ojos"""
        eyes = self.eye_cascade.detectMultiScale(face_gray, 1.05, 8, minSize=(30, 30))
        
        if len(eyes) == 0:
            return {'hue': 90, 'saturation': 60, 'value': 100, 'brightness': 100}
        
        # Tomar el ojo más grande
        eyes = sorted(eyes, key=lambda e: e[2]*e[3], reverse=True)
        (ex, ey, ew, eh) = eyes[0]
        
        eye_roi = face_roi[ey:ey+eh, ex:ex+ew]
        if eye_roi.size == 0:
            return {'hue': 90, 'saturation': 60, 'value': 100, 'brightness': 100}
        
        hsv = cv2.cvtColor(eye_roi, cv2.COLOR_BGR2HSV)
        h, w = eye_roi.shape[:2]
        
        # Región del iris (centro)
        center = hsv[int(h*0.3):int(h*0.7), int(w*0.3):int(w*0.7)]
        pixels = center.reshape(-1, 3)
        
        # Filtrar pupila y esclera
        valid = pixels[(pixels[:, 2] > 50) & (pixels[:, 2] < 220)]
        
        if len(valid) < 20:
            return {'hue': 90, 'saturation': 60, 'value': 100, 'brightness': 100}
        
        # K-means para color dominante
        kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
        kmeans.fit(valid)
        
        colors = kmeans.cluster_centers_
        labels = kmeans.labels_
        counts = np.bincount(labels)
        dominant = colors[np.argmax(counts)]
        
        return {
            'hue': int(dominant[0]),
            'saturation': int(dominant[1]),
            'value': int(dominant[2]),
            'brightness': int(np.mean(valid[:, 2]))
        }
    
    def _categorize_eye_color(self, eye_data):
        """Categorización profesional de ojos"""
        h = eye_data['hue']
        s = eye_data['saturation']
        v = eye_data['value']
        
        if v < 70:
            return 'marrón oscuro'
        elif h < 20 or h > 160:
            return 'marrón' if s > 50 else 'ámbar'
        elif 20 <= h <= 80:
            return 'verde' if s > 60 else 'avellana'
        else:
            return 'azul' if s > 50 else 'gris'
    
    def _analyze_hair_color(self, img, face_coords):
        """Análisis profesional de cabello"""
        x, y, w, h = face_coords
        hair_top = max(0, y - int(h * 0.6))
        hair_roi = img[hair_top:y, max(0, x-int(w*0.1)):min(img.shape[1], x+w+int(w*0.1))]
        
        if hair_roi.size == 0:
            return {'hue': 15, 'saturation': 60, 'value': 80}
        
        hsv = cv2.cvtColor(hair_roi, cv2.COLOR_BGR2HSV)
        
        # Máscara para eliminar piel
        lower_skin = np.array([0, 15, 60])
        upper_skin = np.array([30, 170, 255])
        mask_skin = cv2.inRange(hsv, lower_skin, upper_skin)
        mask_hair = cv2.bitwise_not(mask_skin)
        
        hair_pixels = hsv[mask_hair > 0]
        hair_pixels = hair_pixels[hair_pixels[:, 2] > 25]
        
        if len(hair_pixels) < 100:
            return {'hue': 15, 'saturation': 60, 'value': 80}
        
        # K-means para color dominante
        kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
        kmeans.fit(hair_pixels)
        
        colors = kmeans.cluster_centers_
        labels = kmeans.labels_
        counts = np.bincount(labels)
        dominant = colors[np.argmax(counts)]
        
        return {
            'hue': int(dominant[0]),
            'saturation': int(dominant[1]),
            'value': int(dominant[2])
        }
    
    def _categorize_hair_color(self, hair_data):
        """Categorización profesional de cabello"""
        v = hair_data['value']
        h = hair_data['hue']
        s = hair_data['saturation']
        
        if v < 40:
            return 'negro'
        elif v < 70:
            return 'castaño oscuro'
        elif v < 100:
            return 'castaño'
        elif h <= 25 and s > 70:
            return 'pelirrojo'
        elif v > 140:
            return 'rubio'
        else:
            return 'castaño claro'
    
    def _calculate_contrast(self, skin_l, eye_data, hair_data):
        """Cálculo de contraste profesional"""
        diffs = [
            abs(skin_l - eye_data['value']),
            abs(skin_l - hair_data['value']),
            abs(eye_data['value'] - hair_data['value'])
        ]
        avg = np.mean(diffs)
        
        return 'high' if avg > 80 else 'medium' if avg > 45 else 'low'
    
    def _calculate_saturation(self, eye_data, hair_data):
        """Cálculo de saturación profesional"""
        avg = (eye_data['saturation'] + hair_data['saturation']) / 2
        return 'high' if avg > 110 else 'medium' if avg > 65 else 'low'
    
    def _classify_season_professional(self, skin, eye, hair, contrast, saturation):
        """
        Clasificación PROFESIONAL en 4 estaciones
        
        Lógica:
        - PRIMAVERA: Cálido + Claro + Alta saturación
        - VERANO: Frío + Suave + Baja saturación
        - OTOÑO: Cálido + Profundo + Baja saturación
        - INVIERNO: Frío + Alto contraste + Alta saturación
        """
        
        # Determinar calidez de ojos y cabello
        eye_warm = (eye['hue'] < 40 or eye['hue'] > 150)
        hair_warm = (hair['hue'] < 50 or hair['hue'] > 330)
        
        # Determinar claridad
        eye_light = eye['value'] > 110
        hair_light = hair['value'] > 110
        
        # Score de calidez (0-3)
        warmth_score = sum([skin == 'warm', eye_warm, hair_warm])
        is_warm = warmth_score >= 2
        
        # CLASIFICACIÓN
        if is_warm:
            # Cálidos: Primavera o Otoño
            if saturation in ['high', 'medium'] and (eye_light or hair_light):
                return "Primavera"
            else:
                return "Otoño"
        else:
            # Fríos: Verano o Invierno
            if contrast == 'high' or saturation == 'high':
                return "Invierno"
            else:
                return "Verano"
    
    def _get_default_result(self):
        """Resultado por defecto profesional"""
        return {
            'season': "Primavera",
            'skin_tone': 'warm',
            'skin_lightness': 150,
            'skin_lab': {'L': 150, 'a': 128, 'b': 135},
            'eye_color': {
                'category': 'marrón',
                'hue': 20,
                'saturation': 70,
                'value': 100
            },
            'hair_color': {
                'category': 'castaño',
                'hue': 15,
                'saturation': 60,
                'value': 80
            },
            'contrast': 'medium',
            'saturation': 'medium',
            'palette': self.paletas["Primavera"]['colores'],
            'palette_description': self.paletas["Primavera"]['descripcion'],
            'palette_names': self.paletas["Primavera"]['colores_texto'],
            'confidence': 0.50,
            'detailed_analysis': {
                'conclusion': 'Análisis por defecto (sin detección facial)'
            }
        }