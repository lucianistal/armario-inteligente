import json
import os
from datetime import datetime

class WardrobeManager:
    """
    Sistema de gestión de armario virtual del usuario.
    Permite agregar, editar, eliminar y consultar prendas.
    """
    
    def __init__(self, user_email):
        self.user_email = user_email
        self.wardrobe_file = f"data/wardrobes/{self._sanitize_email(user_email)}.json"
        self._ensure_file_exists()
    
    def _sanitize_email(self, email):
        """Convierte email en nombre de archivo seguro"""
        return email.replace('@', '_at_').replace('.', '_')
    
    def _ensure_file_exists(self):
        """Crea archivo de armario si no existe"""
        os.makedirs('data/wardrobes', exist_ok=True)
        if not os.path.exists(self.wardrobe_file):
            with open(self.wardrobe_file, 'w') as f:
                json.dump({'items': [], 'created_at': datetime.now().isoformat()}, f)
    
    def add_item(self, item_data):
        """
        Añade una prenda al armario.
        
        item_data debe incluir:
        - nombre: str (ej: "Camisa blanca de algodón")
        - tipo: str (superior, inferior, vestido, calzado, complemento)
        - color: str o list (ej: "blanco" o ["blanco", "azul"])
        - ocasion: str o list (formal, casual, deportiva)
        - clima_apropiado: str o list (calor, templado, frio)
        - fit: str (ajustada, normal, holgada)
        - imagen: str (nombre de archivo, opcional)
        - notas: str (opcional)
        """
        wardrobe = self._load_wardrobe()
        
        # Añadir timestamp y ID único
        item_data['id'] = self._generate_item_id()
        item_data['added_at'] = datetime.now().isoformat()
        
        # Validar datos básicos
        required_fields = ['nombre', 'tipo', 'color', 'ocasion', 'clima_apropiado']
        for field in required_fields:
            if field not in item_data:
                raise ValueError(f"Campo requerido faltante: {field}")
        
        # Convertir strings JSON a objetos Python si es necesario
        for field in ['color', 'ocasion', 'clima_apropiado']:
            if isinstance(item_data.get(field), str):
                try:
                    item_data[field] = json.loads(item_data[field])
                except:
                    pass
        
        wardrobe['items'].append(item_data)
        self._save_wardrobe(wardrobe)
        
        return item_data['id']
    
    def get_all_items(self):
        """Retorna todas las prendas del armario"""
        wardrobe = self._load_wardrobe()
        return wardrobe['items']
    
    def get_item_by_id(self, item_id):
        """Obtiene una prenda específica por ID"""
        items = self.get_all_items()
        for item in items:
            if item['id'] == item_id:
                return item
        return None
    
    def update_item(self, item_id, updated_data):
        """Actualiza una prenda existente"""
        wardrobe = self._load_wardrobe()
        
        for i, item in enumerate(wardrobe['items']):
            if item['id'] == item_id:
                wardrobe['items'][i].update(updated_data)
                wardrobe['items'][i]['updated_at'] = datetime.now().isoformat()
                self._save_wardrobe(wardrobe)
                return True
        
        return False
    
    def delete_item(self, item_id):
        """Elimina una prenda del armario"""
        wardrobe = self._load_wardrobe()
        original_length = len(wardrobe['items'])
        
        wardrobe['items'] = [item for item in wardrobe['items'] if item['id'] != item_id]
        
        if len(wardrobe['items']) < original_length:
            self._save_wardrobe(wardrobe)
            return True
        
        return False
    
    def search_items(self, **filters):
        """
        Busca prendas con filtros específicos.
        
        Ejemplos:
        - search_items(tipo='superior', ocasion='formal')
        - search_items(color='azul', clima_apropiado='frio')
        """
        items = self.get_all_items()
        results = []
        
        for item in items:
            match = True
            for key, value in filters.items():
                item_value = item.get(key)
                
                # Manejar listas
                if isinstance(item_value, list):
                    if value not in item_value:
                        match = False
                        break
                else:
                    if item_value != value:
                        match = False
                        break
            
            if match:
                results.append(item)
        
        return results
    
    def get_outfit_suggestions(self, ocasion, clima, fit_preference, season_colors):
        """
        Genera sugerencias de outfit basadas en el armario del usuario.
        
        Args:
            ocasion: str (formal, casual, deportiva)
            clima: str (calor, templado, frio)
            fit_preference: str (ajustada, normal, holgada)
            season_colors: list (colores recomendados de colorimetría)
        
        Returns:
            dict con prendas sugeridas
        """
        # Buscar prendas apropiadas
        suitable_items = []
        all_items = self.get_all_items()
        
        for item in all_items:
            # Verificar ocasión
            item_ocasiones = item.get('ocasion', [])
            if isinstance(item_ocasiones, str):
                item_ocasiones = [item_ocasiones]
            
            # Verificar clima
            item_climas = item.get('clima_apropiado', [])
            if isinstance(item_climas, str):
                item_climas = [item_climas]
            
            if ocasion in item_ocasiones and clima in item_climas:
                suitable_items.append(item)
        
        if not suitable_items:
            return None
        
        # Filtrar por preferencia de fit si existe
        if fit_preference:
            fit_items = [item for item in suitable_items if item.get('fit') == fit_preference]
            if fit_items:
                suitable_items = fit_items
        
        # Priorizar prendas que coincidan con colores de la estación
        color_matched = []
        other_items = []
        
        for item in suitable_items:
            item_colors = item.get('color', [])
            if isinstance(item_colors, str):
                item_colors = [item_colors]
            
            if any(color.lower() in [c.lower() for c in season_colors] for color in item_colors):
                color_matched.append(item)
            else:
                other_items.append(item)
        
        # Priorizar prendas con colores de la estación
        suitable_items = color_matched + other_items
        
        # Construir outfit
        outfit = {}
        
        # Buscar cada tipo de prenda
        tipos = ['superior', 'inferior', 'vestido', 'calzado', 'complemento']
        for tipo in tipos:
            for item in suitable_items:
                if item.get('tipo') == tipo and tipo not in outfit:
                    outfit[tipo] = item
                    break
        
        return outfit if outfit else None
    
    def get_statistics(self):
        """
        Retorna estadísticas del armario.
        """
        items = self.get_all_items()
        
        stats = {
            'total_items': len(items),
            'by_type': {},
            'by_occasion': {},
            'by_climate': {},
            'by_color': {}
        }
        
        for item in items:
            # Por tipo
            tipo = item.get('tipo', 'unknown')
            stats['by_type'][tipo] = stats['by_type'].get(tipo, 0) + 1
            
            # Por ocasión
            ocasiones = item.get('ocasion')
            if isinstance(ocasiones, str):
                ocasiones = [ocasiones]
            for ocasion in ocasiones:
                stats['by_occasion'][ocasion] = stats['by_occasion'].get(ocasion, 0) + 1
            
            # Por clima
            climas = item.get('clima_apropiado')
            if isinstance(climas, str):
                climas = [climas]
            for clima in climas:
                stats['by_climate'][clima] = stats['by_climate'].get(clima, 0) + 1
            
            # Por color
            colores = item.get('color')
            if isinstance(colores, str):
                colores = [colores]
            for color in colores:
                stats['by_color'][color] = stats['by_color'].get(color, 0) + 1
        
        return stats
    
    def suggest_missing_items(self):
        """
        Analiza el armario y sugiere qué prendas faltan.
        """
        stats = self.get_statistics()
        suggestions = []
        
        # Verificar prendas básicas
        basic_items = {
            'superior': ['camiseta básica', 'camisa', 'jersey'],
            'inferior': ['pantalón', 'vaqueros'],
            'calzado': ['zapatillas', 'zapatos formales'],
            'complemento': ['bolso', 'cinturón']
        }
        
        for tipo, examples in basic_items.items():
            if stats['by_type'].get(tipo, 0) < 3:
                suggestions.append(f"Considera añadir más prendas de tipo '{tipo}' (ej: {', '.join(examples)})")
        
        # Verificar balance de ocasiones
        for ocasion in ['formal', 'casual', 'deportiva']:
            if stats['by_occasion'].get(ocasion, 0) < 2:
                suggestions.append(f"Te faltan opciones para ocasiones {ocasion}")
        
        # Verificar balance de climas
        for clima in ['calor', 'templado', 'frio']:
            if stats['by_climate'].get(clima, 0) < 2:
                suggestions.append(f"Añade prendas para clima {clima}")
        
        return suggestions
    
    def _generate_item_id(self):
        """Genera ID único para la prenda"""
        import time
        return f"item_{int(time.time() * 1000)}"
    
    def _load_wardrobe(self):
        """Carga el armario desde JSON"""
        with open(self.wardrobe_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_wardrobe(self, wardrobe_data):
        """Guarda el armario a JSON"""
        with open(self.wardrobe_file, 'w', encoding='utf-8') as f:
            json.dump(wardrobe_data, f, indent=2, ensure_ascii=False)


# === EJEMPLO DE USO ===

def ejemplo_uso():
    """Ejemplos de cómo usar el WardrobeManager"""
    
    # Crear manager para un usuario
    wardrobe = WardrobeManager('usuario@ejemplo.com')
    
    # 1. Añadir prendas
    wardrobe.add_item({
        'nombre': 'Camisa blanca de algodón',
        'tipo': 'superior',
        'color': 'blanco',
        'ocasion': ['formal', 'casual'],
        'clima_apropiado': ['templado', 'calor'],
        'fit': 'normal',
        'marca': 'Zara',
        'notas': 'Muy versátil, combina con todo'
    })
    
    wardrobe.add_item({
        'nombre': 'Vaqueros azul oscuro',
        'tipo': 'inferior',
        'color': 'azul',
        'ocasion': ['casual'],
        'clima_apropiado': ['templado', 'frio'],
        'fit': 'ajustada'
    })
    
    # 2. Buscar prendas
    prendas_formales = wardrobe.search_items(ocasion='formal')
    print(f"Prendas formales: {len(prendas_formales)}")
    
    # 3. Obtener sugerencias de outfit
    outfit = wardrobe.get_outfit_suggestions(
        ocasion='casual',
        clima='templado',
        fit_preference='normal',
        season_colors=['azul', 'rosa', 'lavanda']
    )
    
    if outfit:
        print("\n=== OUTFIT SUGERIDO ===")
        for tipo, prenda in outfit.items():
            print(f"{tipo.upper()}: {prenda['nombre']}")
    
    # 4. Estadísticas
    stats = wardrobe.get_statistics()
    print(f"\n=== ESTADÍSTICAS ===")
    print(f"Total de prendas: {stats['total_items']}")
    print(f"Por tipo: {stats['by_type']}")
    
    # 5. Sugerencias de qué comprar
    suggestions = wardrobe.suggest_missing_items()
    print(f"\n=== SUGERENCIAS ===")
    for sugg in suggestions:
        print(f"- {sugg}")


if __name__ == "__main__":
    ejemplo_uso()
