from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
from datetime import datetime
import hashlib
import pandas as pd
from werkzeug.utils import secure_filename

from colorimetry_analyzer import ColorimetryAnalyzer
from outfit_generator import OutfitGenerator
from wardrobe_manager import WardrobeManager
from clothing_database import ClothingDatabase
from gtts import gTTS

app = Flask(__name__)
app.secret_key = 'armario-inteligente-uie-2025-SECRET-KEY-CHANGE-THIS'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Crear carpetas necesarias
os.makedirs('static/uploads', exist_ok=True)
os.makedirs('data', exist_ok=True)
os.makedirs('data/wardrobes', exist_ok=True)
os.makedirs('data/history', exist_ok=True)
os.makedirs('data/colorimetry', exist_ok=True)
os.makedirs('static/audio', exist_ok=True)
os.makedirs('static/clothing_images', exist_ok=True)
os.makedirs('static/user_clothing', exist_ok=True)

USERS_FILE = 'data/users.json'

# Inicializar módulos
colorimetry_analyzer = ColorimetryAnalyzer()
outfit_generator = OutfitGenerator()
clothing_db = ClothingDatabase()

# ========== FUNCIONES DE USUARIO ==========

def load_users():
    """Carga usuarios desde JSON"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    """Guarda usuarios a JSON"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def hash_password(password):
    """Hashea contraseña con SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

# ========== FUNCIONES DE COLORIMETRÍA GUARDADA ==========

def get_user_colorimetry(user_email):
    """Obtiene colorimetría guardada del usuario"""
    color_file = f'data/colorimetry/{_sanitize_email(user_email)}.json'
    if os.path.exists(color_file):
        try:
            with open(color_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Verificar que no sea muy antigua (más de 6 meses)
                saved_date = datetime.fromisoformat(data.get('saved_at', '2000-01-01'))
                if (datetime.now() - saved_date).days < 180:
                    return data.get('colorimetry_result')
        except:
            pass
    return None

def save_user_colorimetry(user_email, colorimetry_result):
    """Guarda colorimetría del usuario"""
    color_file = f'data/colorimetry/{_sanitize_email(user_email)}.json'
    with open(color_file, 'w', encoding='utf-8') as f:
        json.dump({
            'saved_at': datetime.now().isoformat(),
            'colorimetry_result': colorimetry_result
        }, f, indent=2, ensure_ascii=False)

def _sanitize_email(email):
    """Convierte email en nombre de archivo seguro"""
    return email.replace('@', '_at_').replace('.', '_')

# ========== FUNCIONES DE HISTORIAL ==========

def save_to_history(user_email, result_data):
    """Guarda consulta en el historial del usuario"""
    history_file = f'data/history/{_sanitize_email(user_email)}.json'
    
    # Cargar historial existente
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            history = []
    
    # Añadir nueva consulta
    history.append({
        'timestamp': datetime.now().isoformat(),
        'result': result_data
    })
    
    # Guardar (mantener solo las últimas 20 consultas)
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history[-20:], f, indent=2, ensure_ascii=False)

def get_user_history(user_email):
    """Obtiene historial de consultas del usuario"""
    history_file = f'data/history/{_sanitize_email(user_email)}.json'
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

# ========== FUNCIONES DE CLIMA ==========

def load_clima_data():
    """Carga datos climáticos desde Excel"""
    try:
        # Intenta la carga con la ruta relativa
        df = pd.read_excel('data/clima_provincias.xlsx')
        print("✅ DEBUG: Archivo clima_provincias.xlsx cargado con éxito.")
        return df
    except FileNotFoundError:
        # Se activa si el archivo no se encuentra en la ruta esperada
        print("⚠️ Archivo clima_provincias.xlsx no encontrado (Fallo en la ruta).")
        return None
    except Exception as e:
        # ¡ESTA ES LA CLAVE! Captura y muestra cualquier otro error (ej. formato, permisos, etc.)
        print(f"❌ ERROR CRÍTICO al cargar clima_provincias.xlsx. Causa: {e}")
        return None

def get_clima_info(provincia, mes):
    """Obtiene información climática de provincia y mes"""
    df = load_clima_data()
    
    # Valores por defecto según provincia y mes (datos aproximados de España)
    defaults_by_month = {
        'Diciembre': {'temperatura': 11, 'prob_lluvia': 60},
        'Enero': {'temperatura': 10, 'prob_lluvia': 55},
        'Febrero': {'temperatura': 11, 'prob_lluvia': 50},
        'Marzo': {'temperatura': 13, 'prob_lluvia': 45},
        'Abril': {'temperatura': 15, 'prob_lluvia': 50},
        'Mayo': {'temperatura': 18, 'prob_lluvia': 45},
        'Junio': {'temperatura': 22, 'prob_lluvia': 30},
        'Julio': {'temperatura': 25, 'prob_lluvia': 20},
        'Agosto': {'temperatura': 25, 'prob_lluvia': 20},
        'Septiembre': {'temperatura': 23, 'prob_lluvia': 35},
        'Octubre': {'temperatura': 18, 'prob_lluvia': 50},
        'Noviembre': {'temperatura': 13, 'prob_lluvia': 60}
    }
    
    # Ajustes específicos por provincia (A Coruña es más fría y lluviosa)
    if 'Coruña' in provincia or 'A Coruña' in provincia:
        defaults_by_month = {k: {'temperatura': v['temperatura'] - 1, 'prob_lluvia': min(v['prob_lluvia'] + 10, 80)} 
                            for k, v in defaults_by_month.items()}
    
    if df is None:
        return defaults_by_month.get(mes, {"temperatura": 18, "prob_lluvia": 40})
    
    try:
        row = df[(df['Provincia'] == provincia) & (df['Mes'] == mes)]
        if not row.empty:
            return {
                "temperatura": int(row.iloc[0]['Temp_media']),
                "prob_lluvia": int(row.iloc[0]['Prob_lluvia'])
            }
    except Exception as e:
        print(f"Error al obtener clima: {e}")
    
    return defaults_by_month.get(mes, {"temperatura": 18, "prob_lluvia": 40})

# ========== FUNCIONES DE AUDIO ==========

def generate_audio(text, filename):
    """Genera audio con gTTS"""
    try:
        tts = gTTS(text=text, lang='es', slow=False)
        audio_path = f'static/audio/{filename}'
        tts.save(audio_path)
        return audio_path
    except Exception as e:
        print(f"Error generando audio: {e}")
        return None

# ========== RUTAS PRINCIPALES ==========

@app.route('/')
def welcome():
    """Página de bienvenida principal"""
    return render_template('welcome.html')

@app.route('/index')
def index():
    """Página de inicio"""
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('welcome'))

@app.route('/dashboard')
def dashboard():
    """Dashboard del usuario (requiere autenticación)"""
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user_email=session['user'])

# ========== RUTAS DE AUTENTICACIÓN ==========

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Inicio de sesión"""
    if request.method == 'POST':
        try:
            data = request.get_json()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            
            if not email or not password:
                return jsonify({'success': False, 'message': 'Email y contraseña requeridos'}), 400
            
            users = load_users()
            
            if email in users:
                stored_hash = users[email]['password']
                input_hash = hash_password(password)
                
                if stored_hash == input_hash:
                    session['user'] = email
                    return jsonify({'success': True, 'message': 'Login exitoso'})
                else:
                    return jsonify({'success': False, 'message': 'Contraseña incorrecta'}), 401
            else:
                return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
        
        except Exception as e:
            print(f"Error en login: {e}")
            return jsonify({'success': False, 'message': 'Error del servidor'}), 500
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registro de usuario"""
    if request.method == 'POST':
        try:
            data = request.get_json()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            confirm_password = data.get('confirm_password', '')
            
            # Validaciones
            if not email or not password:
                return jsonify({'success': False, 'message': 'Email y contraseña requeridos'}), 400
            
            if len(password) < 6:
                return jsonify({'success': False, 'message': 'La contraseña debe tener al menos 6 caracteres'}), 400
            
            if password != confirm_password:
                return jsonify({'success': False, 'message': 'Las contraseñas no coinciden'}), 400
            
            if '@' not in email or '.' not in email:
                return jsonify({'success': False, 'message': 'Email inválido'}), 400
            
            users = load_users()
            
            if email in users:
                return jsonify({'success': False, 'message': 'El usuario ya existe'}), 409
            
            # Crear usuario
            users[email] = {
                'password': hash_password(password),
                'created_at': datetime.now().isoformat()
            }
            save_users(users)
            
            session['user'] = email
            return jsonify({'success': True, 'message': 'Registro exitoso'})
        
        except Exception as e:
            print(f"Error en registro: {e}")
            return jsonify({'success': False, 'message': 'Error del servidor'}), 500
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Cierra sesión"""
    session.pop('user', None)
    return redirect(url_for('welcome'))

# ========== RUTAS DE LA APLICACIÓN ==========

@app.route('/recommendation')
def recommendation():
    """Página de análisis y recomendación"""
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('onboarding.html')

@app.route('/wardrobe')
def wardrobe():
    """Gestión del armario virtual"""
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('wardrobe.html', user_email=session['user'])

@app.route('/history')
def history():
    """Historial de consultas"""
    if 'user' not in session:
        return redirect(url_for('login'))
    user_history = get_user_history(session['user'])
    return render_template('history.html', history=user_history)

@app.route('/results')
def results():
    """Página de resultados"""
    if 'user' not in session:
        return redirect(url_for('login'))
    result_data = session.get('last_result', {})
    return render_template('results.html', data=result_data)

# ========== FUNCIONES DE GENERACIÓN INTELIGENTE ==========

def detectar_preferencia_masculina(no_vestidos, no_faldas, no_tops, genero=None):
    """
    Detecta si el usuario tiene preferencia masculina.
    
    CRITERIOS:
    - Marca NO vestidos + NO faldas + NO tops = Preferencia masculina
    - O género explícito = "Hombre"
    """
    if genero and genero.lower() == 'hombre':
        return True
    
    if no_vestidos and no_faldas and no_tops:
        print(f"   🚹 Preferencia MASCULINA detectada (no vestidos + no faldas + no tops)")
        return True
    
    return False

def filtrar_prendas_femeninas(items, categoria):
    """
    Filtra prendas consideradas femeninas de una lista.
    
    CALZADO FEMENINO:
    - tacones, stilettos, alpargatas (con tacón), sandalias
    
    COMPLEMENTOS FEMENINOS:
    - bolso, bolsa, cartera (de mano)
    - collar (excepto cadenas gruesas)
    - pendientes, aretes, diadema
    """
    
    palabras_femeninas = {
        'calzado': ['tacón', 'tacones', 'stiletto', 'alpargata', 'sandalia'],
        'complemento': ['bolso', 'bolsa', 'cartera', 'collar', 'pendiente', 
                       'arete', 'diadema', 'horquilla', 'pañuelo']
    }
    
    if categoria not in palabras_femeninas:
        return items
    
    filtradas = []
    for item in items:
        nombre = item.get('nombre', '').lower()
        
        # Verificar si contiene palabras femeninas
        es_femenina = any(palabra in nombre for palabra in palabras_femeninas[categoria])
        
        if not es_femenina:
            filtradas.append(item)
        else:
            print(f"   🚫 Filtrado (femenino): {item.get('nombre')}")
    
    return filtradas

def generate_smart_outfit(user_items, db_items, ocasion, clima, temperatura, prob_lluvia, 
                          estacion, palette_colors, fit_preference, no_vestidos, no_faldas, no_pantalones, no_tops=False, genero=None):
    """
    Genera outfit INTELIGENTE combinando prendas del usuario y base de datos.
    
    LÓGICA:
    1. PRIORIZA prendas del usuario que cumplan condiciones
    2. Si hay vestido → NO buscar superior/inferior
    3. Clima inteligente: lluvia alta → botas/abrigo
    4. Colores de la paleta del usuario
    """
    
    outfit = {}
    
    # DETECTAR PREFERENCIA MASCULINA
    preferencia_masculina = detectar_preferencia_masculina(no_vestidos, no_faldas, no_tops, genero)
    
    def match_item(item, ocasion, clima, estacion, palette_colors):
        """Verifica si una prenda cumple las condiciones - CASE INSENSITIVE"""
        # Ocasión - manejar string o array
        item_ocasiones = item.get('ocasion', [])
        if isinstance(item_ocasiones, str):
            try:
                # Intentar parsear si es JSON string
                import json
                item_ocasiones = json.loads(item_ocasiones)
            except:
                item_ocasiones = [item_ocasiones]
        if not isinstance(item_ocasiones, list):
            item_ocasiones = [item_ocasiones]
        
        # CASE INSENSITIVE comparison
        if ocasion.lower() not in [o.lower() for o in item_ocasiones]:
            return False
        
        # Clima - manejar string o array
        item_climas = item.get('clima_apropiado', item.get('clima', []))
        if isinstance(item_climas, str):
            try:
                import json
                item_climas = json.loads(item_climas)
            except:
                item_climas = [item_climas]
        if not isinstance(item_climas, list):
            item_climas = [item_climas]
        
        # CASE INSENSITIVE comparison
        if clima.lower() not in [c.lower() for c in item_climas]:
            return False
        
        # Estación - opcional
        if 'estacion' in item:
            item_estaciones = item.get('estacion', [])
            if isinstance(item_estaciones, str):
                try:
                    import json
                    item_estaciones = json.loads(item_estaciones)
                except:
                    item_estaciones = [item_estaciones]
            if not isinstance(item_estaciones, list):
                item_estaciones = [item_estaciones]
            
            # CASE INSENSITIVE comparison
            if estacion not in [e for e in item_estaciones]:
                return False
        
        return True
    
    def color_match_score(item, palette_colors):
        """Score de coincidencia de color - CASE INSENSITIVE"""
        item_colors = item.get('color', [])
        
        # Manejar string JSON
        if isinstance(item_colors, str):
            try:
                import json
                item_colors = json.loads(item_colors)
            except:
                item_colors = [item_colors]
        
        if not isinstance(item_colors, list):
            item_colors = [item_colors]
        
        # Keywords de la paleta en minúsculas
        palette_keywords = set()
        for color_name in palette_colors:
            words = color_name.lower().split()
            palette_keywords.update(words)
        
        # Contar coincidencias (case insensitive)
        matches = sum(1 for item_color in item_colors 
                     if any(kw in item_color.lower() for kw in palette_keywords))
        
        if matches > 0:
            print(f"      Color match: {item_colors} vs {list(palette_keywords)[:3]} = {matches} coincidencias")
        
        return (matches / max(len(item_colors), 1)) * 100
    
    # 1. VESTIDO (si aplica)
    if not no_vestidos and ocasion in ['formal', 'casual']:
        vestidos_usuario = [item for item in user_items 
                           if item.get('tipo') == 'vestido' and match_item(item, ocasion, clima, estacion, palette_colors)]
        
        if vestidos_usuario:
            vestidos_usuario.sort(key=lambda x: color_match_score(x, palette_colors), reverse=True)
            outfit['vestido'] = vestidos_usuario[0]
            print(f"   ✓ Vestido USUARIO: {outfit['vestido'].get('nombre')}")
        else:
            vestidos_db = db_items.search_items(tipo='vestido', ocasion=ocasion, clima=clima, estacion=estacion)
            if vestidos_db:
                vestidos_db.sort(key=lambda x: color_match_score(x, palette_colors), reverse=True)
                outfit['vestido'] = vestidos_db[0]
    
    # 2. SI NO HAY VESTIDO → SUPERIOR + INFERIOR
    if 'vestido' not in outfit:
        # SUPERIOR
        superiores_usuario = [item for item in user_items 
                             if item.get('tipo') == 'superior' and match_item(item, ocasion, clima, estacion, palette_colors)]
        
        if superiores_usuario:
            superiores_usuario.sort(key=lambda x: color_match_score(x, palette_colors), reverse=True)
            outfit['superior'] = superiores_usuario[0]
            print(f"   ✓ Superior USUARIO: {outfit['superior'].get('nombre')}")
        else:
            superiores_db = db_items.search_items(tipo='superior', ocasion=ocasion, clima=clima, estacion=estacion)
            if superiores_db:
                superiores_db.sort(key=lambda x: color_match_score(x, palette_colors), reverse=True)
                outfit['superior'] = superiores_db[0]
        
        # INFERIOR
        inferiores_usuario = [item for item in user_items 
                             if item.get('tipo') == 'inferior' and match_item(item, ocasion, clima, estacion, palette_colors)]
        
        if no_faldas:
            inferiores_usuario = [item for item in inferiores_usuario 
                                 if 'falda' not in item.get('nombre', '').lower()]
        if no_pantalones:
            inferiores_usuario = [item for item in inferiores_usuario 
                                 if 'pantalon' not in item.get('nombre', '').lower()]
        
        if inferiores_usuario:
            inferiores_usuario.sort(key=lambda x: color_match_score(x, palette_colors), reverse=True)
            outfit['inferior'] = inferiores_usuario[0]
            print(f"   ✓ Inferior USUARIO: {outfit['inferior'].get('nombre')}")
        else:
            inferiores_db = db_items.search_items(tipo='inferior', ocasion=ocasion, clima=clima, estacion=estacion)
            if inferiores_db:
                inferiores_db.sort(key=lambda x: color_match_score(x, palette_colors), reverse=True)
                outfit['inferior'] = inferiores_db[0]
    
    # 3. CALZADO (lluvia → botas, filtrar femenino si aplica)
    calzados_usuario = [item for item in user_items 
                       if item.get('tipo') == 'calzado' and match_item(item, ocasion, clima, estacion, palette_colors)]
    
    # FILTRAR CALZADO FEMENINO si preferencia masculina
    if preferencia_masculina:
        calzados_usuario = filtrar_prendas_femeninas(calzados_usuario, 'calzado')
    
    if prob_lluvia > 60 and calzados_usuario:
        botas = [item for item in calzados_usuario if 'bota' in item.get('nombre', '').lower()]
        if botas:
            calzados_usuario = botas
            print(f"   ☔ Lluvia {prob_lluvia}% → Botas")
    
    if calzados_usuario:
        calzados_usuario.sort(key=lambda x: color_match_score(x, palette_colors), reverse=True)
        outfit['calzado'] = calzados_usuario[0]
        print(f"   ✓ Calzado USUARIO: {outfit['calzado'].get('nombre')}")
    else:
        calzados_db = db_items.search_items(tipo='calzado', ocasion=ocasion, clima=clima)
        if calzados_db:
            # FILTRAR CALZADO FEMENINO de base de datos
            if preferencia_masculina:
                calzados_db = filtrar_prendas_femeninas(calzados_db, 'calzado')
            if calzados_db:  # Verificar que aún hay opciones después del filtro
                calzados_db.sort(key=lambda x: color_match_score(x, palette_colors), reverse=True)
                outfit['calzado'] = calzados_db[0]
    
    # 4. COMPLEMENTO (frío → bufanda, filtrar femenino si aplica)
    complementos_usuario = [item for item in user_items 
                           if item.get('tipo') == 'complemento' and match_item(item, ocasion, clima, estacion, palette_colors)]
    
    # FILTRAR COMPLEMENTOS FEMENINOS si preferencia masculina
    if preferencia_masculina:
        complementos_usuario = filtrar_prendas_femeninas(complementos_usuario, 'complemento')
    
    if temperatura < 10 and complementos_usuario:
        abrigados = [item for item in complementos_usuario 
                    if 'bufanda' in item.get('nombre', '').lower() or 'gorro' in item.get('nombre', '').lower()]
        if abrigados:
            complementos_usuario = abrigados
            print(f"   ❄️ Frío {temperatura}°C → Bufanda/gorro")
    
    if complementos_usuario:
        complementos_usuario.sort(key=lambda x: color_match_score(x, palette_colors), reverse=True)
        outfit['complemento'] = complementos_usuario[0]
        print(f"   ✓ Complemento USUARIO: {outfit['complemento'].get('nombre')}")
    else:
        complementos_db = db_items.search_items(tipo='complemento', ocasion=ocasion, clima=clima)
        if complementos_db:
            # FILTRAR COMPLEMENTOS FEMENINOS de base de datos
            if preferencia_masculina:
                complementos_db = filtrar_prendas_femeninas(complementos_db, 'complemento')
            if complementos_db:  # Verificar que aún hay opciones después del filtro
                complementos_db.sort(key=lambda x: color_match_score(x, palette_colors), reverse=True)
                outfit['complemento'] = complementos_db[0]
    
    return outfit

# ========== API DE RECOMENDACIÓN ==========

@app.route('/api/onboarding', methods=['POST'])
def onboarding():
    """Procesa formulario de recomendación"""
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'No autenticado'}), 401
    
    try:
        data = request.form.to_dict()
        user_email = session['user']
        
        # Verificar si el usuario ya tiene colorimetría guardada
        saved_colorimetry = get_user_colorimetry(user_email)
        
        # Análisis de foto (solo si no hay guardada o hay foto nueva)
        photo_path = None
        colorimetry_result = saved_colorimetry
        
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename:
                filename = secure_filename(f"{user_email}_{datetime.now().timestamp()}.jpg")
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                photo.save(photo_path)
                
                print("🔍 Analizando colorimetría...")
                colorimetry_result = colorimetry_analyzer.analyze_image(photo_path)
                print(f"✅ Análisis completado: {colorimetry_result['season']}")
                
                # Guardar colorimetría para futuras consultas
                save_user_colorimetry(user_email, colorimetry_result)
        
        if colorimetry_result is None:
            # Si no hay foto ni guardada, usar valores por defecto
            colorimetry_result = colorimetry_analyzer._get_default_result()
            print("⚠️ Usando colorimetría por defecto")
        else:
            print(f"📁 Usando colorimetría guardada: {colorimetry_result['season']}")
        
        # Obtener clima
        clima_info = get_clima_info(data.get('provincia'), data.get('mes'))
        
        # Categorizar temperatura
        temp = clima_info.get('temperatura', 20)
        if temp > 25:
            clima_cat = 'calor'
        elif temp > 15:
            clima_cat = 'templado'
        else:
            clima_cat = 'frio'
        
        # Obtener outfit de la base de datos
        season = colorimetry_result['season']
        
        # USAR LOS COLORES DE LA PALETA DE COLORIMETRÍA (no hardcodeado)
        palette_colors = colorimetry_result.get('palette_names', [])
        print(f"🎨 Usando paleta de {season}: {', '.join(palette_colors[:4])}")
        
        # Obtener armario del usuario
        wardrobe = WardrobeManager(user_email)
        user_items = wardrobe.get_all_items()
        
        # GENERACIÓN INTELIGENTE DE OUTFIT
        print(f"👔 Generando outfit inteligente...")
        print(f"   - Prendas del usuario disponibles: {len(user_items)}")
        print(f"   - Ocasión: {data.get('ocasion', 'casual')}")
        print(f"   - Clima: {clima_cat} ({clima_info.get('temperatura')}°C)")
        print(f"   - Prob. lluvia: {clima_info.get('prob_lluvia')}%")
        
        outfit_items = generate_smart_outfit(
            user_items=user_items,
            db_items=clothing_db,
            ocasion=data.get('ocasion', 'casual').lower(),
            clima=clima_cat,
            temperatura=clima_info.get('temperatura', 20),
            prob_lluvia=clima_info.get('prob_lluvia', 30),
            estacion=season,
            palette_colors=palette_colors,
            fit_preference=data.get('fit'),
            no_vestidos=data.get('no_vestidos', False),
            no_faldas=data.get('no_faldas', False),
            no_pantalones=data.get('no_pantalones', False),
            no_tops=data.get('no_tops', False),
            genero=data.get('genero')
        )
        
        outfit_source = "user" if any(item.get('id', '').startswith('item_') for item in outfit_items.values()) else "database"
        print(f"✅ Outfit generado desde: {outfit_source}")
        
        # Generar narrativa completa (para voz)
        print("🎬 Generando recomendación narrativa...")
        outfit_result = outfit_generator.generate_outfit_complete(
            user_data=data,
            clima_info=clima_info,
            colorimetry_result=colorimetry_result,
            outfit_items=outfit_items
        )
        outfit_narrative = outfit_result['outfit_narrative']
        
        # Generar texto SIMPLIFICADO (para pantalla)
        outfit_simple = generate_simple_outfit_text(outfit_items)
        
        # Generar audio
        audio_filename = f"recommendation_{user_email}_{datetime.now().timestamp()}.mp3"
        audio_path = generate_audio(outfit_narrative, audio_filename)
        
        # Preparar resultado
        result = {
            'success': True,
            'usuario': data.get('nombre'),
            'colorimetria': season,
            'paleta': colorimetry_result['palette'],
            'outfit_narrative': outfit_narrative,
            'outfit_simple': outfit_simple,
            'outfit_items': outfit_items,
            'outfit_source': outfit_source,
            'clima': f"{data.get('provincia')}, {data.get('mes')}",
            'temperatura': clima_info.get('temperatura'),
            'prob_lluvia': clima_info.get('prob_lluvia'),
            'ocasion': data.get('ocasion'),
            'preferencia': data.get('fit'),
            'audio_url': f"/static/audio/{audio_filename}" if audio_path else None,
            'confidence': colorimetry_result.get('confidence', 0.85),
            'colorimetry_saved': saved_colorimetry is not None,
            'skin_analysis': {
                'undertone': colorimetry_result.get('skin_tone'),
                'lightness': colorimetry_result.get('skin_lightness'),
                'description': colorimetry_result.get('detailed_analysis', {}).get('skin', '')
            },
            'eye_analysis': {
                'category': colorimetry_result.get('eye_color', {}).get('category', 'desconocido'),
                'hue': colorimetry_result.get('eye_color', {}).get('hue', 0),
                'description': colorimetry_result.get('detailed_analysis', {}).get('eyes', '')
            },
            'hair_analysis': {
                'category': colorimetry_result.get('hair_color', {}).get('category', 'desconocido'),
                'hue': colorimetry_result.get('hair_color', {}).get('hue', 0),
                'description': colorimetry_result.get('detailed_analysis', {}).get('hair', '')
            },
            'detailed_explanation': colorimetry_result.get('detailed_analysis', {})
        }
        
        # Guardar en historial
        save_to_history(user_email, result)
        
        session['last_result'] = result
        
        return jsonify(result)
    
    except Exception as e:
        print(f"ERROR EN SUBMIT: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

def generate_simple_outfit_text(outfit_items):
    """Genera texto simplificado del outfit para pantalla"""
    if not outfit_items:
        return "No se pudo generar outfit"
    
    parts = []
    
    if 'vestido' in outfit_items:
        parts.append(outfit_items['vestido'].get('nombre_corto', outfit_items['vestido'].get('nombre', 'vestido')))
    else:
        if 'superior' in outfit_items:
            parts.append(outfit_items['superior'].get('nombre_corto', outfit_items['superior'].get('nombre', 'prenda superior')))
        if 'inferior' in outfit_items:
            parts.append(outfit_items['inferior'].get('nombre_corto', outfit_items['inferior'].get('nombre', 'prenda inferior')))
    
    if 'calzado' in outfit_items:
        parts.append(outfit_items['calzado'].get('nombre_corto', outfit_items['calzado'].get('nombre', 'calzado')))
    
    if 'complemento' in outfit_items:
        parts.append(outfit_items['complemento'].get('nombre_corto', outfit_items['complemento'].get('nombre', 'complemento')))
    
    return " + ".join(parts) if parts else "Outfit personalizado"

# ========== API DEL ARMARIO ==========

@app.route('/api/wardrobe/items', methods=['GET', 'POST'])
def wardrobe_items():
    """Gestiona prendas del armario"""
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'No autenticado'}), 401
    
    user_email = session['user']
    wardrobe = WardrobeManager(user_email)
    
    if request.method == 'POST':
        try:
            # Manejar foto si existe
            if 'imagen' in request.files:
                photo = request.files['imagen']
                if photo.filename:
                    filename = secure_filename(f"{user_email}_{datetime.now().timestamp()}_{photo.filename}")
                    photo_path = os.path.join('static/user_clothing', filename)
                    photo.save(photo_path)
                    
                    item_data = request.form.to_dict()
                    item_data['imagen'] = filename
                else:
                    item_data = request.get_json()
            else:
                item_data = request.get_json()
            
            item_id = wardrobe.add_item(item_data)
            return jsonify({'success': True, 'item_id': item_id})
        except Exception as e:
            print(f"Error añadiendo prenda: {e}")
            return jsonify({'success': False, 'message': str(e)}), 400
    
    else:  # GET
        items = wardrobe.get_all_items()
        return jsonify({'success': True, 'items': items})

@app.route('/api/wardrobe/items/<item_id>', methods=['DELETE'])
def delete_wardrobe_item(item_id):
    """Elimina una prenda del armario"""
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'No autenticado'}), 401
    
    user_email = session['user']
    wardrobe = WardrobeManager(user_email)
    
    if wardrobe.delete_item(item_id):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Prenda no encontrada'}), 404

@app.route('/api/wardrobe/stats')
def wardrobe_stats():
    """Estadísticas del armario"""
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'No autenticado'}), 401
    
    user_email = session['user']
    wardrobe = WardrobeManager(user_email)
    
    stats = wardrobe.get_statistics()
    suggestions = wardrobe.suggest_missing_items()
    
    return jsonify({'success': True, 'stats': stats, 'suggestions': suggestions})

# ========== API DE HISTORIAL ==========

@app.route('/api/history')
def api_history():
    """Obtiene historial de consultas"""
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'No autenticado'}), 401
    
    user_history = get_user_history(session['user'])
    return jsonify({'success': True, 'history': user_history})

@app.route('/api/colorimetry')
def api_colorimetry():
    """Obtiene colorimetría guardada del usuario"""
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'No autenticado'}), 401
    
    colorimetry = get_user_colorimetry(session['user'])
    return jsonify({
        'success': True, 
        'has_colorimetry': colorimetry is not None,
        'colorimetry': colorimetry
    })

# ========== RUTAS DE SALUD ==========

@app.route('/api/health')
def health():
    """Endpoint de salud del sistema"""
    return jsonify({
        'status': 'ok',
        'colorimetry_ready': colorimetry_analyzer is not None,
        'clima_data_ready': load_clima_data() is not None,
        'outfit_generator_ready': outfit_generator is not None,
        'clothing_db_ready': clothing_db is not None,
        'total_clothing_items': sum(len(items) for items in clothing_db.items.values())
    })

@app.route('/api/dashboard/stats')
def dashboard_stats():
    """Estadísticas del dashboard del usuario"""
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'No autenticado'}), 401
    
    user_email = session['user']
    
    # Obtener historial
    history = get_user_history(user_email)
    num_consultas = len(history)
    
    # Obtener prendas del armario
    wardrobe = WardrobeManager(user_email)
    user_items = wardrobe.get_all_items()
    num_prendas = len(user_items)
    
    # Obtener colorimetría guardada
    colorimetry = get_user_colorimetry(user_email)
    num_colores = len(colorimetry.get('palette', [])) if colorimetry else 0
    
    # Contar outfits creados (consultas con outfit completo)
    num_outfits = sum(1 for h in history if h.get('result', {}).get('outfit_items'))
    
    return jsonify({
        'success': True,
        'stats': {
            'consultas': num_consultas,
            'prendas': num_prendas,
            'outfits': num_outfits,
            'colores': num_colores
        }
    })

# ========== INICIAR SERVIDOR ==========

if __name__ == '__main__':
    print("=" * 60)
    print("🎨 ARMARIO INTELIGENTE - Servidor PROFESIONAL v2.0")
    print("=" * 60)
    print("✅ Analizador de colorimetría: ACTIVO")
    print("✅ Generador de narrativas: ACTIVO")
    print("✅ Base de datos de prendas: ACTIVO")
    print("✅ Sistema de autenticación: ACTIVO")
    print("✅ Sistema de historial: ACTIVO")
    print("✅ Colorimetría guardada: ACTIVO")
    
    if load_clima_data() is not None:
        print("✅ Datos de clima: CARGADOS")
    else:
        print("⚠️ Datos de clima: NO DISPONIBLES")
    
    print(f"✅ Prendas en base de datos: {sum(len(items) for items in clothing_db.items.values())}")
    
    print("=" * 60)
    print("🌐 Accede a: http://localhost:5003")
    print("=" * 60)
    
    app.run(debug=True, port=5003)