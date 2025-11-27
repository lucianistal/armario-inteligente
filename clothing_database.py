import json
import os

class ClothingDatabase:
    """
    Base de datos profesional de prendas con imágenes.
    Permite búsquedas avanzadas por características.
    """
    
    def __init__(self):
        self.db_file = 'data/clothing_items.json'
        self.images_dir = 'static/clothing_images'
        self._ensure_structure()
        self._load_database()
    
    def _ensure_structure(self):
        """Crea estructura de carpetas si no existe"""
        os.makedirs('data', exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Crear subcarpetas por tipo
        types = ['superior', 'inferior', 'vestido', 'calzado', 'complemento']
        for t in types:
            os.makedirs(f'{self.images_dir}/{t}', exist_ok=True)
    
    def _load_database(self):
        """Carga base de datos desde JSON"""
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r', encoding='utf-8') as f:
                self.items = json.load(f)
        else:
            self.items = self._create_default_database()
            self._save_database()
    
    def _save_database(self):
        """Guarda base de datos a JSON"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.items, f, indent=2, ensure_ascii=False)
    
    def _create_default_database(self):
        """Crea base de datos por defecto con prendas ejemplo"""
        return {
            "superior": [
                {
                    "id": "sup_001",
                    "nombre": "Camiseta Blanca Básica",
                    "nombre_corto": "camiseta blanca",
                    "color": ["blanco"],
                    "ocasion": ["casual", "deportiva"],
                    "clima": ["calor", "templado"],
                    "estacion": ["Primavera", "Verano"],
                    "fit": "normal",
                    "imagen": "superior/camiseta_blanca.jpg",
                    "descripcion": "Camiseta de algodón 100%, corte clásico"
                },
                {
                    "id": "sup_002",
                    "nombre": "Blusa de Seda Azul Celeste",
                    "nombre_corto": "blusa azul",
                    "color": ["azul"],
                    "ocasion": ["formal", "casual"],
                    "clima": ["templado", "calor"],
                    "estacion": ["Verano", "Primavera"],
                    "fit": "normal",
                    "imagen": "superior/blusa_azul.jpg",
                    "descripcion": "Blusa elegante de seda, ideal para eventos"
                },
                {
                    "id": "sup_003",
                    "nombre": "Jersey de Punto Gris",
                    "nombre_corto": "jersey gris",
                    "color": ["gris"],
                    "ocasion": ["casual", "formal"],
                    "clima": ["frio", "templado"],
                    "estacion": ["Otoño", "Invierno"],
                    "fit": "normal",
                    "imagen": "superior/jersey_gris.jpg",
                    "descripcion": "Jersey de lana suave, perfecto para días fríos"
                },
                {
                    "id": "sup_004",
                    "nombre": "Camisa Verde Oliva",
                    "nombre_corto": "camisa verde oliva",
                    "color": ["verde"],
                    "ocasion": ["casual"],
                    "clima": ["templado"],
                    "estacion": ["Otoño", "Primavera"],
                    "fit": "normal",
                    "imagen": "superior/camisa_verde.jpg",
                    "descripcion": "Camisa versátil, combina con todo"
                },
                {
                    "id": "sup_005",
                    "nombre": "Top Coral",
                    "nombre_corto": "top coral",
                    "color": ["coral"],
                    "ocasion": ["casual", "formal"],
                    "clima": ["calor"],
                    "estacion": ["Primavera", "Verano"],
                    "fit": "ajustada",
                    "imagen": "superior/top_coral.jpg",
                    "descripcion": "Top vibrante ideal para primavera"
                }
            ],
            "inferior": [
                {
                    "id": "inf_001",
                    "nombre": "Vaqueros Azul Oscuro",
                    "nombre_corto": "vaqueros",
                    "color": ["azul"],
                    "ocasion": ["casual"],
                    "clima": ["templado", "frio"],
                    "estacion": ["Otoño", "Primavera", "Invierno"],
                    "fit": "normal",
                    "imagen": "inferior/vaqueros_azul.jpg",
                    "descripcion": "Vaqueros clásicos, nunca fallan"
                },
                {
                    "id": "inf_002",
                    "nombre": "Pantalón Negro de Vestir",
                    "nombre_corto": "pantalón negro",
                    "color": ["negro"],
                    "ocasion": ["formal"],
                    "clima": ["templado", "frio"],
                    "estacion": ["Invierno", "Otoño"],
                    "fit": "ajustada",
                    "imagen": "inferior/pantalon_negro.jpg",
                    "descripcion": "Pantalón elegante para ocasiones formales"
                },
                {
                    "id": "inf_003",
                    "nombre": "Falda Midi Beige",
                    "nombre_corto": "falda beige",
                    "color": ["beige"],
                    "ocasion": ["casual", "formal"],
                    "clima": ["calor", "templado"],
                    "estacion": ["Primavera", "Verano"],
                    "fit": "normal",
                    "imagen": "inferior/falda_beige.jpg",
                    "descripcion": "Falda versátil de longitud midi"
                },
                {
                    "id": "inf_004",
                    "nombre": "Shorts Blancos",
                    "nombre_corto": "shorts blancos",
                    "color": ["blanco"],
                    "ocasion": ["casual", "deportiva"],
                    "clima": ["calor"],
                    "estacion": ["Verano"],
                    "fit": "normal",
                    "imagen": "inferior/shorts_blancos.jpg",
                    "descripcion": "Shorts frescos para días calurosos"
                }
            ],
            "vestido": [
                {
                    "id": "ves_001",
                    "nombre": "Vestido Negro Corto",
                    "nombre_corto": "vestido negro",
                    "color": ["negro"],
                    "ocasion": ["formal"],
                    "clima": ["templado", "calor"],
                    "estacion": ["Invierno", "Verano"],
                    "fit": "ajustada",
                    "imagen": "vestido/vestido_negro.jpg",
                    "descripcion": "El clásico little black dress"
                },
                {
                    "id": "ves_002",
                    "nombre": "Vestido Floral Rosa",
                    "nombre_corto": "vestido floral",
                    "color": ["rosa"],
                    "ocasion": ["casual"],
                    "clima": ["calor"],
                    "estacion": ["Primavera", "Verano"],
                    "fit": "normal",
                    "imagen": "vestido/vestido_floral.jpg",
                    "descripcion": "Vestido romántico con estampado floral"
                }
            ],
            "calzado": [
                {
                    "id": "cal_001",
                    "nombre": "Zapatillas Blancas",
                    "nombre_corto": "zapatillas",
                    "color": ["blanco"],
                    "ocasion": ["casual", "deportiva"],
                    "clima": ["calor", "templado"],
                    "estacion": ["Primavera", "Verano", "Otoño"],
                    "fit": "normal",
                    "imagen": "calzado/zapatillas_blancas.jpg",
                    "descripcion": "Zapatillas cómodas para el día a día"
                },
                {
                    "id": "cal_002",
                    "nombre": "Tacones Negros",
                    "nombre_corto": "tacones",
                    "color": ["negro"],
                    "ocasion": ["formal"],
                    "clima": ["templado"],
                    "estacion": ["Invierno", "Otoño", "Primavera"],
                    "fit": "ajustada",
                    "imagen": "calzado/tacones_negros.jpg",
                    "descripcion": "Tacones elegantes de altura media"
                },
                {
                    "id": "cal_003",
                    "nombre": "Botas Marrones",
                    "nombre_corto": "botas",
                    "color": ["marron"],
                    "ocasion": ["casual"],
                    "clima": ["frio"],
                    "estacion": ["Otoño", "Invierno"],
                    "fit": "normal",
                    "imagen": "calzado/botas_marrones.jpg",
                    "descripcion": "Botas cómodas para el invierno"
                }
            ],
            "complemento": [
                {
                    "id": "com_001",
                    "nombre": "Bolso Negro de Piel",
                    "nombre_corto": "bolso negro",
                    "color": ["negro"],
                    "ocasion": ["formal", "casual"],
                    "clima": ["templado", "frio"],
                    "estacion": ["Invierno", "Otoño"],
                    "fit": "normal",
                    "imagen": "complemento/bolso_negro.jpg",
                    "descripcion": "Bolso versátil para cualquier ocasión"
                },
                {
                    "id": "com_002",
                    "nombre": "Gafas de Sol",
                    "nombre_corto": "gafas de sol",
                    "color": ["negro"],
                    "ocasion": ["casual", "deportiva"],
                    "clima": ["calor"],
                    "estacion": ["Verano", "Primavera"],
                    "fit": "normal",
                    "imagen": "complemento/gafas_sol.jpg",
                    "descripcion": "Gafas de sol estilo aviador"
                },
                {
                    "id": "com_003",
                    "nombre": "Collar Dorado",
                    "nombre_corto": "collar dorado",
                    "color": ["dorado"],
                    "ocasion": ["formal"],
                    "clima": ["templado", "calor"],
                    "estacion": ["Primavera", "Verano"],
                    "fit": "normal",
                    "imagen": "complemento/collar_dorado.jpg",
                    "descripcion": "Collar elegante con acabado dorado"
                }
            ]
        }
    
    def search_items(self, tipo=None, ocasion=None, clima=None, estacion=None, color=None):
        """
        Búsqueda avanzada de prendas
        
        Args:
            tipo: str - superior, inferior, vestido, calzado, complemento
            ocasion: str - formal, casual, deportiva
            clima: str - calor, templado, frio
            estacion: str - Primavera, Verano, Otoño, Invierno
            color: str - cualquier color
        
        Returns:
            list: Prendas que coinciden con los criterios
        """
        results = []
        
        # Si se especifica tipo, buscar solo en ese tipo
        if tipo:
            items_to_search = {tipo: self.items.get(tipo, [])}
        else:
            items_to_search = self.items
        
        for item_type, items in items_to_search.items():
            for item in items:
                match = True
                
                # Filtrar por ocasión
                if ocasion and ocasion not in item.get('ocasion', []):
                    match = False
                
                # Filtrar por clima
                if clima and clima not in item.get('clima', []):
                    match = False
                
                # Filtrar por estación
                if estacion and estacion not in item.get('estacion', []):
                    match = False
                
                # Filtrar por color
                if color:
                    item_colors = item.get('color', [])
                    if not any(color.lower() in c.lower() for c in item_colors):
                        match = False
                
                if match:
                    item_copy = item.copy()
                    item_copy['tipo'] = item_type
                    results.append(item_copy)
        
        return results
    
    def get_outfit_suggestion(self, ocasion, clima, estacion, colores_favorables):
        """
        Genera sugerencia de outfit completo con imágenes
        
        Args:
            ocasion: str
            clima: str
            estacion: str
            colores_favorables: list - colores de la paleta del usuario
        
        Returns:
            dict: Outfit completo con prendas e imágenes
        """
        outfit = {}
        
        # 1. Buscar superior
        superiores = self.search_items(
            tipo='superior',
            ocasion=ocasion,
            clima=clima,
            estacion=estacion
        )
        
        # Priorizar prendas con colores favorables
        # Convertir nombres complejos ("amarillo dorado") a palabras clave ("amarillo", "dorado")
        color_keywords = set()
        for color_name in colores_favorables:
            # Extraer palabras clave de colores compuestos
            words = color_name.lower().split()
            color_keywords.update(words)
        
        superiores_favorables = [s for s in superiores if any(
            any(keyword in c.lower() for keyword in color_keywords) 
            for c in s.get('color', [])
        )]
        
        if superiores_favorables:
            outfit['superior'] = superiores_favorables[0]
        elif superiores:
            outfit['superior'] = superiores[0]
        
        # 2. Buscar inferior o vestido
        vestidos = self.search_items(
            tipo='vestido',
            ocasion=ocasion,
            clima=clima,
            estacion=estacion
        )
        
        inferiores = self.search_items(
            tipo='inferior',
            ocasion=ocasion,
            clima=clima,
            estacion=estacion
        )
        
        if vestidos and ocasion == 'formal':
            outfit['vestido'] = vestidos[0]
        elif inferiores:
            outfit['inferior'] = inferiores[0]
        
        # 3. Buscar calzado
        calzados = self.search_items(
            tipo='calzado',
            ocasion=ocasion,
            clima=clima
        )
        if calzados:
            outfit['calzado'] = calzados[0]
        
        # 4. Buscar complemento
        complementos = self.search_items(
            tipo='complemento',
            ocasion=ocasion,
            clima=clima
        )
        if complementos:
            outfit['complemento'] = complementos[0]
        
        return outfit
    
    def get_item_by_id(self, item_id):
        """Obtiene una prenda por su ID"""
        for tipo, items in self.items.items():
            for item in items:
                if item['id'] == item_id:
                    item_copy = item.copy()
                    item_copy['tipo'] = tipo
                    return item_copy
        return None


# Ejemplo de uso
if __name__ == "__main__":
    db = ClothingDatabase()
    
    print("✅ Base de datos creada con éxito!")
    print(f"\n📊 Estadísticas:")
    for tipo, items in db.items.items():
        print(f"   {tipo}: {len(items)} prendas")
    
    print("\n🔍 Prueba de búsqueda - Prendas casuales para calor:")
    results = db.search_items(ocasion='casual', clima='calor')
    for item in results[:3]:
        print(f"   - {item['nombre']} ({item['tipo']})")
    
    print("\n👗 Outfit sugerido para evento formal en verano:")
    outfit = db.get_outfit_suggestion(
        ocasion='formal',
        clima='calor',
        estacion='Verano',
        colores_favorables=['azul', 'rosa', 'blanco']
    )
    for tipo, prenda in outfit.items():
        print(f"   {tipo}: {prenda['nombre']}")