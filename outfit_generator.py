import random

class OutfitGenerator:
    """
    Generador SINCRONIZADO de outfits:
    - outfit_simple: Texto escueto para mostrar con imágenes
    - outfit_narrative: Narrativa detallada para audio
    AMBOS COINCIDEN en las prendas recomendadas
    """
    
    def __init__(self):
        self.intros_audio = {
            'formal': [
                "Para tu evento formal, te recomiendo un look elegante:",
                "Para lucir impecable en esta ocasión formal:",
                "Un outfit sofisticado perfecto para ti sería:"
            ],
            'casual': [
                "Para tu día a día, te sugiero un look cómodo pero con estilo:",
                "Para estar relajado y a la moda:",
                "Mi recomendación casual para ti es:"
            ],
            'deportiva': [
                "Para tu actividad deportiva, lo ideal es:",
                "Para mantenerte activo con comodidad:",
                "Un conjunto perfecto para tu entrenamiento:"
            ]
        }
        
        self.explicaciones_color = {
            'Primavera': "Como tienes colorimetría de Primavera, te favorecen los tonos cálidos y vibrantes que iluminan tu tez.",
            'Verano': "Tu colorimetría de Verano se lleva mejor con tonos suaves y fríos que crean armonía con tu subtono rosado.",
            'Otoño': "Como Otoño, te sientan de maravilla los tonos tierra y cálidos que potencian tu calidez natural.",
            'Invierno': "Tu colorimetría de Invierno brilla con colores intensos y fríos que realzan tu contraste natural."
        }

    # =========================
    # Asegurar prendas obligatorias
    # =========================
    def ensure_complete_outfit(self, outfit_items, genero='mujer'):
        es_mujer = 'mujer' in genero.lower()

        # Vestido o superior
        if 'vestido' not in outfit_items and 'superior' not in outfit_items:
            outfit_items['superior'] = {
                'nombre': 'blusa básica' if es_mujer else 'camisa básica',
                'nombre_corto': 'blusa' if es_mujer else 'camisa',
                'color': 'blanco'
            }

        # Inferior si no hay vestido
        if 'vestido' not in outfit_items and 'inferior' not in outfit_items:
            outfit_items['inferior'] = {
                'nombre': 'falda negra' if es_mujer else 'pantalón negro',
                'nombre_corto': 'falda' if es_mujer else 'pantalón',
                'color': 'negro'
            }

        # Calzado obligatorio
        if 'calzado' not in outfit_items:
            outfit_items['calzado'] = {
                'nombre': 'tacones' if es_mujer else 'zapatillas',
                'nombre_corto': 'tacones' if es_mujer else 'zapatillas',
                'color': 'blanco'
            }

        return outfit_items

    # =========================
    # Descripción de prenda con artículo según género y plural
    # =========================
    def _get_prenda_descripcion(self, prenda, genero='mujer'):
        if isinstance(prenda, dict):
            nombre = prenda.get('nombre_corto') or prenda.get('nombre', 'prenda')
            primera_palabra = nombre.split()[0].lower()
            
            # Palabras SIEMPRE plural (independiente de género)
            plural_palabras = ['sandalias', 'botines', 'zapatillas', 'tacones', 'mocasines', 'zapatos', 
                              'botas', 'vaqueros', 'leggings', 'pantalones', 'gafas']
            
            # Palabras SIEMPRE masculinas (terminan en 'o' o son excepciones)
            masculinas = ['pantalón', 'jersey', 'abrigo', 'vestido', 'bolso', 'cinturón',
                         'sombrero', 'gorro', 'zapato', 'mocasín', 'botín', 'collar']
            
            # Palabras SIEMPRE femeninas (terminan en 'a' generalmente)
            femeninas = ['blusa', 'falda', 'camisa', 'chaqueta', 'camiseta', 'bufanda',
                        'sandalia', 'zapatilla', 'bota', 'sudadera', 'mochila']
            
            # Determinar si es plural
            es_plural = (primera_palabra.endswith('s') and not primera_palabra.endswith('és')) or primera_palabra in plural_palabras
            
            # Determinar el artículo correcto
            if es_plural:
                articulo = 'unos' if primera_palabra in masculinas or primera_palabra.endswith('os') else 'unas'
            else:
                # Singular
                if primera_palabra in masculinas:
                    articulo = 'un'
                elif primera_palabra in femeninas:
                    articulo = 'una'
                elif primera_palabra.endswith('o'):
                    articulo = 'un'
                elif primera_palabra.endswith('a'):
                    articulo = 'una'
                else:
                    # Por defecto, basarse en el género del usuario
                    articulo = 'un' if genero.lower() == 'hombre' else 'una'
            
            return f"{articulo} {nombre}"
        return "una prenda"

    # =========================
    # GENERACIÓN OUTFIT
    # =========================

    def generate_outfit_complete(self, user_data, clima_info, colorimetry_result, outfit_items):
        ocasion = user_data.get('ocasion', 'casual').lower()
        temperatura = clima_info.get('temperatura', 20)
        prob_lluvia = clima_info.get('prob_lluvia', 30)
        season = colorimetry_result.get('season', 'Primavera')
        nombre = user_data.get('nombre', 'amigo')
        fit = user_data.get('fit', 'Normal').lower()
        
        # Aseguramos prendas obligatorias
        outfit_items = self.ensure_complete_outfit(outfit_items, user_data.get('genero', 'mujer'))

        #  GENERAR OUTFIT SIMPLE
        outfit_simple = self._generate_outfit_simple(outfit_items, user_data.get('genero', 'mujer'))
        
        #  GENERAR NARRATIVA
        outfit_narrative = self._generate_outfit_narrative(
            outfit_items=outfit_items,
            user_data=user_data,
            clima_info=clima_info,
            colorimetry_result=colorimetry_result
        )
        
        return {
            'outfit_simple': outfit_simple,
            'outfit_narrative': outfit_narrative,
            'outfit_items': outfit_items
        }
    
    def _generate_outfit_simple(self, outfit_items, genero='mujer'):
        if not outfit_items:
            return "Outfit personalizado"
        
        parts = []
        if 'vestido' in outfit_items:
            parts.append(self._get_prenda_descripcion(outfit_items['vestido'], genero))
        else:
            if 'superior' in outfit_items:
                parts.append(self._get_prenda_descripcion(outfit_items['superior'], genero))
            if 'inferior' in outfit_items:
                parts.append(self._get_prenda_descripcion(outfit_items['inferior'], genero))
        
        if 'calzado' in outfit_items:
            parts.append(self._get_prenda_descripcion(outfit_items['calzado'], genero))
        
        if 'complemento' in outfit_items:
            parts.append(self._get_prenda_descripcion(outfit_items['complemento'], genero))
        
        return " + ".join(parts) if parts else "Outfit personalizado"
    
    def _get_item_short_name(self, item):
        if isinstance(item, dict):
            name = item.get('nombre_corto') or item.get('nombre', 'prenda')
            words = name.lower().split()
            return " ".join(words[:3])
        return str(item).lower()
    
    def _generate_outfit_narrative(self, outfit_items, user_data, clima_info, colorimetry_result):
        ocasion = user_data.get('ocasion', 'casual').lower()
        temperatura = clima_info.get('temperatura', 20)
        prob_lluvia = clima_info.get('prob_lluvia', 30)
        season = colorimetry_result.get('season', 'Primavera')
        nombre = user_data.get('nombre', 'amigo')
        fit = user_data.get('fit', 'Normal').lower()
        genero = user_data.get('genero', 'mujer')
        palette_names = colorimetry_result.get('palette_names', [])
        
        if temperatura > 25:
            temp_cat = 'calor'
            temp_desc = 'este día caluroso'
        elif temperatura > 15:
            temp_cat = 'templado'
            temp_desc = 'este clima agradable'
        else:
            temp_cat = 'frio'
            temp_desc = 'este día frío'
        
        narrativa = f"Hola {nombre}. "
        narrativa += random.choice(self.intros_audio[ocasion]) + "\n\n"
        
        if 'vestido' in outfit_items:
            vestido = outfit_items['vestido']
            narrativa += f"Te sugiero {self._get_prenda_descripcion(vestido, genero)}. "
        else:
            if 'superior' in outfit_items:
                superior = outfit_items['superior']
                narrativa += f"Combina {self._get_prenda_descripcion(superior, genero)} "
            if 'inferior' in outfit_items:
                inferior = outfit_items['inferior']
                narrativa += f"con {self._get_prenda_descripcion(inferior, genero)}. "
        
        if 'calzado' in outfit_items:
            calzado = outfit_items['calzado']
            narrativa += f"Complétalo con {self._get_prenda_descripcion(calzado, genero)}. "
        
        if 'complemento' in outfit_items:
            comp = outfit_items['complemento']
            narrativa += f"Y no olvides {self._get_prenda_descripcion(comp, genero)}. "
        
        narrativa += f"\n\nEste outfit es perfecto para {temp_desc}. "
        
        if prob_lluvia > 60:
            narrativa += f"Importante: hay {prob_lluvia}% de probabilidad de lluvia, lleva paraguas. "
        elif prob_lluvia > 30:
            narrativa += f"Considera llevar paraguas, hay {prob_lluvia}% de probabilidad de lluvia. "
        
        if palette_names:
            colores_texto = ", ".join(palette_names[:3])
            narrativa += f"\n\n{self.explicaciones_color[season]} "
            narrativa += f"Apuesta por colores como {colores_texto}. "
        
        fit_texts = {
            'ajustada': "Como prefieres corte ajustado, busca prendas que marquen tu silueta sin perder comodidad.",
            'holgada': "Como prefieres ropa holgada, elige prendas oversized que te den libertad de movimiento.",
            'normal': "Un corte regular te permitirá jugar con diferentes estilos."
        }
        narrativa += fit_texts.get(fit, "")
        
        return narrativa
    
    # =========================
    # OUTFIT GENÉRICO COMPLETO
    # =========================
    def generate_generic_outfit(self, ocasion, temp_cat, genero, fit, no_v=None, no_f=None, no_t=None, no_p=None):
        gender_key = 'mujer' if 'mujer' in genero.lower() else 'hombre'
        
        generic_outfits = {
            'casual': {
                'mujer': {
                    'calor': {
                        'superior': {'nombre': 'top ligero', 'nombre_corto': 'top ligero', 'color': 'blanco'},
                        'inferior': {'nombre': 'shorts', 'nombre_corto': 'shorts', 'color': 'azul'},
                        'calzado': {'nombre': 'sandalias', 'nombre_corto': 'sandalias', 'color': 'beige'}
                    },
                    'templado': {
                        'superior': {'nombre': 'jersey liviano', 'nombre_corto': 'jersey', 'color': 'gris'},
                        'inferior': {'nombre': 'vaqueros', 'nombre_corto': 'vaqueros', 'color': 'azul'},
                        'calzado': {'nombre': 'zapatillas blancas', 'nombre_corto': 'zapatillas', 'color': 'blanco'}
                    },
                    'frio': {
                        'superior': {'nombre': 'suéter grueso', 'nombre_corto': 'suéter', 'color': 'negro'},
                        'inferior': {'nombre': 'pantalón de pana', 'nombre_corto': 'pantalón', 'color': 'marrón'},
                        'calzado': {'nombre': 'botas', 'nombre_corto': 'botas', 'color': 'negro'}
                    }
                },
                'hombre': {
                    'calor': {
                        'superior': {'nombre': 'camiseta básica', 'nombre_corto': 'camiseta', 'color': 'blanco'},
                        'inferior': {'nombre': 'shorts', 'nombre_corto': 'shorts', 'color': 'beige'},
                        'calzado': {'nombre': 'zapatillas', 'nombre_corto': 'zapatillas', 'color': 'blanco'}
                    },
                    'templado': {
                        'superior': {'nombre': 'camiseta', 'nombre_corto': 'camiseta', 'color': 'gris'},
                        'inferior': {'nombre': 'vaqueros', 'nombre_corto': 'vaqueros', 'color': 'azul'},
                        'calzado': {'nombre': 'zapatillas', 'nombre_corto': 'zapatillas', 'color': 'blanco'}
                    },
                    'frio': {
                        'superior': {'nombre': 'jersey', 'nombre_corto': 'jersey', 'color': 'negro'},
                        'inferior': {'nombre': 'vaqueros', 'nombre_corto': 'vaqueros', 'color': 'azul oscuro'},
                        'calzado': {'nombre': 'botas', 'nombre_corto': 'botas', 'color': 'marrón'}
                    }
                }
            },
            'formal': {
                'mujer': {
                    'calor': {
                        'vestido': {'nombre': 'vestido midi elegante', 'nombre_corto': 'vestido midi', 'color': 'azul'},
                        'calzado': {'nombre': 'tacones', 'nombre_corto': 'tacones', 'color': 'beige'}
                    },
                    'templado': {
                        'superior': {'nombre': 'blazer', 'nombre_corto': 'blazer', 'color': 'negro'},
                        'inferior': {'nombre': 'pantalón de vestir', 'nombre_corto': 'pantalón', 'color': 'negro'},
                        'calzado': {'nombre': 'tacones', 'nombre_corto': 'tacones', 'color': 'negro'}
                    },
                    'frio': {
                        'superior': {'nombre': 'traje sastre', 'nombre_corto': 'traje', 'color': 'gris'},
                        'inferior': {'nombre': 'pantalón de vestir', 'nombre_corto': 'pantalón', 'color': 'gris'},
                        'calzado': {'nombre': 'botas de tacón', 'nombre_corto': 'botas', 'color': 'negro'}
                    }
                },
                'hombre': {
                    'calor': {
                        'superior': {'nombre': 'camisa de lino', 'nombre_corto': 'camisa', 'color': 'blanco'},
                        'inferior': {'nombre': 'pantalón ligero', 'nombre_corto': 'pantalón', 'color': 'beige'},
                        'calzado': {'nombre': 'mocasines', 'nombre_corto': 'mocasines', 'color': 'marrón'}
                    },
                    'templado': {
                        'superior': {'nombre': 'traje', 'nombre_corto': 'traje', 'color': 'azul marino'},
                        'inferior': {'nombre': 'pantalón de vestir', 'nombre_corto': 'pantalón', 'color': 'azul marino'},
                        'calzado': {'nombre': 'zapatos oxford', 'nombre_corto': 'zapatos', 'color': 'negro'}
                    },
                    'frio': {
                        'superior': {'nombre': 'traje', 'nombre_corto': 'traje', 'color': 'negro'},
                        'inferior': {'nombre': 'pantalón de vestir', 'nombre_corto': 'pantalón', 'color': 'negro'},
                        'calzado': {'nombre': 'zapatos', 'nombre_corto': 'zapatos', 'color': 'negro'}
                    }
                }
            },
            'deportiva': {
                'mujer': {
                    'calor': {
                        'superior': {'nombre': 'top deportivo', 'nombre_corto': 'top deportivo', 'color': 'negro'},
                        'inferior': {'nombre': 'leggings cortos', 'nombre_corto': 'leggings', 'color': 'negro'},
                        'calzado': {'nombre': 'zapatillas running', 'nombre_corto': 'zapatillas', 'color': 'blanco'}
                    },
                    'templado': {
                        'superior': {'nombre': 'camiseta técnica', 'nombre_corto': 'camiseta', 'color': 'gris'},
                        'inferior': {'nombre': 'mallas', 'nombre_corto': 'mallas', 'color': 'negro'},
                        'calzado': {'nombre': 'zapatillas', 'nombre_corto': 'zapatillas', 'color': 'blanco'}
                    },
                    'frio': {
                        'superior': {'nombre': 'camiseta térmica', 'nombre_corto': 'camiseta térmica', 'color': 'negro'},
                        'inferior': {'nombre': 'mallas térmicas', 'nombre_corto': 'mallas', 'color': 'negro'},
                        'calzado': {'nombre': 'zapatillas', 'nombre_corto': 'zapatillas', 'color': 'gris'}
                    }
                },
                'hombre': {
                    'calor': {
                        'superior': {'nombre': 'camiseta técnica', 'nombre_corto': 'camiseta', 'color': 'blanco'},
                        'inferior': {'nombre': 'shorts', 'nombre_corto': 'shorts', 'color': 'negro'},
                        'calzado': {'nombre': 'zapatillas', 'nombre_corto': 'zapatillas', 'color': 'blanco'}
                    },
                    'templado': {
                        'superior': {'nombre': 'camiseta manga larga', 'nombre_corto': 'camiseta', 'color': 'gris'},
                        'inferior': {'nombre': 'mallas', 'nombre_corto': 'mallas', 'color': 'negro'},
                        'calzado': {'nombre': 'zapatillas', 'nombre_corto': 'zapatillas', 'color': 'blanco'}
                    },
                    'frio': {
                        'superior': {'nombre': 'camiseta térmica', 'nombre_corto': 'camiseta térmica', 'color': 'negro'},
                        'inferior': {'nombre': 'pantalón deportivo', 'nombre_corto': 'pantalón', 'color': 'negro'},
                        'calzado': {'nombre': 'zapatillas', 'nombre_corto': 'zapatillas', 'color': 'negro'}
                    }
                }
            }
        }  
        return generic_outfits.get(ocasion, generic_outfits['casual']).get(gender_key, {}).get(temp_cat, {})
