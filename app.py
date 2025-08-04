import streamlit as st
import requests
import json
import time
import base64
import io
from PIL import Image
import mimetypes
from datetime import datetime, timedelta
import uuid
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import tempfile
import os
import pandas as pd
# New dependencies for audio input
from audiorecorder import audiorecorder
import speech_recognition as sr

# --- Most of the existing code remains the same ---

# Configure the page
st.set_page_config(
    page_title="Asistente de Salud Rural",
    page_icon="🏥",
    layout="wide"
)

# File management functions (ensure_data_directory, load_user_profile, etc.)
# ... (These functions are unchanged)
def ensure_data_directory():
    """Create data directory if it doesn't exist"""
    if not os.path.exists('data'):
        os.makedirs('data')

def load_user_profile(user_id=None):
    """Load user profile from TXT file"""
    ensure_data_directory()
    if user_id is None:
        user_id = st.session_state.get('current_user_id', str(uuid.uuid4()))
    
    profile_file = f'data/perfil_usuario_{user_id}.txt'
    
    default_profile = {
        'user_id': user_id,
        'name': '',
        'age': '',
        'location': '',
        'phone': '',
        'emergency_contact': '',
        'chronic_conditions': [],
        'allergies': [],
        'current_medications': [],
        'created_at': datetime.now().isoformat(),
        'last_updated': datetime.now().isoformat()
    }
    
    try:
        if os.path.exists(profile_file):
            with open(profile_file, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
                return profile_data
        else:
            return default_profile
    except Exception as e:
        st.error(f"Error loading profile: {e}")
        return default_profile

def save_user_profile(profile_data):
    """Save user profile to TXT file"""
    ensure_data_directory()
    profile_file = f'data/perfil_usuario_{profile_data["user_id"]}.txt'
    
    try:
        profile_data['last_updated'] = datetime.now().isoformat()
        with open(profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Error saving profile: {e}")
        return False

def load_medical_history(user_id):
    """Load medical history from TXT file"""
    ensure_data_directory()
    history_file = f'data/historial_medico_{user_id}.txt'
    
    try:
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return []
    except Exception as e:
        st.error(f"Error loading medical history: {e}")
        return []

def save_medical_history(user_id, history_data):
    """Save medical history to TXT file"""
    ensure_data_directory()
    history_file = f'data/historial_medico_{user_id}.txt'
    
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Error saving medical history: {e}")
        return False

def load_herbal_medicines():
    """Load herbal medicines database from TXT file"""
    ensure_data_directory()
    herbal_file = 'data/plantas_medicinales.txt'
    
    default_herbs = {
        'manzanilla': {
            'name': 'Manzanilla (Chamomile)',
            'scientific_name': 'Matricaria chamomilla',
            'uses': ['Digestive problems', 'Anxiety', 'Sleep disorders', 'Skin irritation'],
            'preparation': 'Tea: 1 tsp dried flowers per cup of hot water, steep 5-10 minutes',
            'contraindications': ['Pregnancy (large amounts)', 'Allergy to asteraceae family'],
            'region': 'Available throughout South America'
        },
        'eucalipto': {
            'name': 'Eucalipto (Eucalyptus)',
            'scientific_name': 'Eucalyptus globulus',
            'uses': ['Respiratory problems', 'Cough', 'Congestion', 'Wound healing'],
            'preparation': 'Inhalation: 5-10 drops oil in hot water. Tea: 2-3 leaves per cup',
            'contraindications': ['Not for children under 2', 'Not for internal use in pregnancy'],
            'region': 'Common in Andean regions'
        },
        'hierba_buena': {
            'name': 'Hierbabuena (Spearmint)',
            'scientific_name': 'Mentha spicata',
            'uses': ['Digestive issues', 'Nausea', 'Headaches', 'Common cold'],
            'preparation': 'Tea: 1 tbsp fresh leaves or 1 tsp dried per cup, steep 5 minutes',
            'contraindications': ['GERD (may worsen symptoms)', 'Hiatal hernia'],
            'region': 'Grows well in most South American climates'
        },
        'aloe_vera': {
            'name': 'Sábila (Aloe Vera)',
            'scientific_name': 'Aloe barbadensis',
            'uses': ['Burns', 'Skin wounds', 'Constipation', 'Digestive inflammation'],
            'preparation': 'Topical: Apply gel directly. Internal: 1-2 tbsp gel (pure) in water',
            'contraindications': ['Pregnancy', 'Breastfeeding', 'Intestinal obstruction'],
            'region': 'Thrives in dry climates across South America'
        },
        'cola_de_caballo': {
            'name': 'Cola de Caballo (Horsetail)',
            'scientific_name': 'Equisetum arvense',
            'uses': ['Kidney problems', 'Urinary tract infections', 'Wound healing', 'Bone health'],
            'preparation': 'Tea: 2-3 tsp dried herb per cup, boil 5 minutes, steep 10 minutes',
            'contraindications': ['Pregnancy', 'Heart/kidney disease', 'Low potassium'],
            'region': 'Found in moist areas throughout South America'
        }
    }
    
    try:
        if os.path.exists(herbal_file):
            with open(herbal_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Create default file
            with open(herbal_file, 'w', encoding='utf-8') as f:
                json.dump(default_herbs, f, indent=2, ensure_ascii=False)
            return default_herbs
    except Exception as e:
        st.error(f"Error loading herbal medicines: {e}")
        return default_herbs

def generate_ai_patient_summary(user_profile, medical_history, ollama_host, model_name):
    """Generate AI summary of patient's current health status using Gemma 3"""
    try:
        # Prepare comprehensive data for AI analysis
        summary_data = {
            'patient_profile': user_profile,
            'total_consultations': len(medical_history),
            'recent_history': medical_history[-10:] if len(medical_history) > 10 else medical_history,
            'consultation_types': {}
        }
        
        # Count consultation types
        for entry in medical_history:
            entry_type = entry.get('type', 'general')
            summary_data['consultation_types'][entry_type] = summary_data['consultation_types'].get(entry_type, 0) + 1
        
        # Create comprehensive prompt for AI analysis
        analysis_prompt = f"""
        Como médico especialista, analiza el siguiente perfil completo del paciente y genera un resumen profesional de su estado de salud actual:

        DATOS DEL PACIENTE:
        - Nombre: {user_profile.get('name', 'No especificado')}
        - Edad: {user_profile.get('age', 'No especificado')} años
        - Ubicación: {user_profile.get('location', 'No especificado')}
        - Condiciones crónicas: {', '.join(user_profile.get('chronic_conditions', [])) or 'Ninguna reportada'}
        - Alergias: {', '.join(user_profile.get('allergies', [])) or 'Ninguna reportada'}
        - Medicamentos actuales: {', '.join(user_profile.get('current_medications', [])) or 'Ninguno reportado'}

        ESTADÍSTICAS DE CONSULTAS:
        - Total de consultas: {len(medical_history)}
        - Tipos de consultas: {json.dumps(summary_data['consultation_types'], ensure_ascii=False)}

        HISTORIAL MÉDICO RECIENTE:
        {json.dumps(summary_data['recent_history'], ensure_ascii=False, indent=2)}

        Por favor, proporciona un resumen médico profesional que incluya:
        1. ESTADO DE SALUD ACTUAL: Evaluación general basada en las consultas recientes
        2. PATRONES IDENTIFICADOS: Síntomas recurrentes, tendencias preocupantes o mejoras
        3. FACTORES DE RIESGO: Elementos que requieren atención o monitoreo
        4. RECOMENDACIONES PRIORITARIAS: Acciones inmediatas y seguimiento sugerido
        5. OBSERVACIONES CLÍNICAS: Notas importantes para el médico tratante

        Mantén un tono profesional y médico, pero accesible para el paciente.
        """

        system_prompt = """Eres un médico especialista experimentado que revisa historiales médicos para generar resúmenes clínicos precisos y útiles. Tu análisis debe ser profesional, basado en evidencia, y proporcionar insights valiosos tanto para el paciente como para otros profesionales de la salud."""

        # Call Ollama API for analysis
        result = call_ollama_api(
            ollama_host, model_name, analysis_prompt,
            temperature=0.2, max_tokens=1000,
            system_prompt=system_prompt
        )

        if result["success"]:
            return {
                "success": True,
                "summary": result["text"],
                "stats": summary_data['consultation_types']
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Error generating summary")
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error in AI analysis: {str(e)}"
        }


def load_generic_medicines():
    """Load generic medicines database from TXT file"""
    ensure_data_directory()
    generic_file = 'data/medicamentos_genericos.txt'
    
    default_generics = {
        'paracetamol': {
            'name': 'Paracetamol (Acetaminofén)',
            'uses': ['Fever', 'Mild to moderate pain', 'Headache'],
            'dosage': 'Adults: 500-1000mg every 4-6 hours (max 4g/day)',
            'contraindications': ['Severe liver disease', 'Alcohol abuse'],
            'side_effects': ['Rare: liver damage with overdose'],
            'availability': 'Widely available'
        },
        'ibuprofeno': {
            'name': 'Ibuprofeno',
            'uses': ['Pain', 'Inflammation', 'Fever'],
            'dosage': 'Adults: 200-400mg every 4-6 hours (max 1200mg/day)',
            'contraindications': ['Stomach ulcers', 'Kidney disease', 'Heart disease'],
            'side_effects': ['Stomach irritation', 'Nausea', 'Dizziness'],
            'availability': 'Common in pharmacies'
        },
        'omeprazol': {
            'name': 'Omeprazol',
            'uses': ['Stomach acid reduction', 'Gastritis', 'GERD'],
            'dosage': 'Adults: 20mg once daily before meals',
            'contraindications': ['Known allergy to proton pump inhibitors'],
            'side_effects': ['Headache', 'Nausea', 'Diarrhea'],
            'availability': 'Prescription or OTC'
        }
    }
    
    try:
        if os.path.exists(generic_file):
            with open(generic_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Create default file
            with open(generic_file, 'w', encoding='utf-8') as f:
                json.dump(default_generics, f, indent=2, ensure_ascii=False)
            return default_generics
    except Exception as e:
        st.error(f"Error loading generic medicines: {e}")
        return default_generics

def save_daily_checkin(user_id, checkin_data):
    """Save daily check-in data"""
    ensure_data_directory()
    checkin_file = f'data/checkin_diario_{user_id}.txt'
    
    try:
        # Load existing data
        if os.path.exists(checkin_file):
            with open(checkin_file, 'r', encoding='utf-8') as f:
                all_checkins = json.load(f)
        else:
            all_checkins = []
        
        # Add new check-in
        checkin_data['timestamp'] = datetime.now().isoformat()
        checkin_data['date'] = datetime.now().strftime('%Y-%m-%d')
        all_checkins.append(checkin_data)
        
        # Keep only last 30 days
        cutoff_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        all_checkins = [c for c in all_checkins if c['date'] >= cutoff_date]
        
        # Save updated data
        with open(checkin_file, 'w', encoding='utf-8') as f:
            json.dump(all_checkins, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        st.error(f"Error saving check-in: {e}")
        return False

def load_daily_checkins(user_id):
    """Load daily check-in history"""
    ensure_data_directory()
    checkin_file = f'data/checkin_diario_{user_id}.txt'
    
    try:
        if os.path.exists(checkin_file):
            with open(checkin_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return []
    except Exception as e:
        st.error(f"Error loading check-ins: {e}")
        return []

# --- UPDATED: Initialize session state ---
def initialize_session_state():
    """Initialize all session state variables"""
    if 'user_initialized' not in st.session_state:
        st.session_state.user_initialized = False
    if 'current_user_id' not in st.session_state:
        st.session_state.current_user_id = None
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {}
    if 'medical_history' not in st.session_state:
        st.session_state.medical_history = []
    if 'herbal_database' not in st.session_state:
        st.session_state.herbal_database = load_herbal_medicines()
    if 'generic_database' not in st.session_state:
        st.session_state.generic_database = load_generic_medicines()
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    # For handling voice input
    if 'voice_input' not in st.session_state:
        st.session_state.voice_input = ""
    # For controlling the dialog
    if 'run_voice_recorder' not in st.session_state:
        st.session_state.run_voice_recorder = False

# ... (show_user_profile_popup, get_system_prompts, Ollama functions are unchanged) ...
def show_user_profile_popup():
    """Show user profile creation popup"""
    with st.container():
        st.markdown("### 👤 Configuración del Perfil de Usuario")
        st.info("Para brindarte la mejor atención médica, necesitamos algunos datos básicos.")
        
        with st.form("user_profile_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Nombre completo *", value="")
                age = st.number_input("Edad *", min_value=0, max_value=120, value=25)
                location = st.text_input("Ubicación (Ciudad, País) *", value="")
                phone = st.text_input("Teléfono", value="")
            
            with col2:
                emergency_contact = st.text_input("Contacto de emergencia", value="")
                chronic_conditions = st.text_area(
                    "Condiciones médicas crónicas (separadas por comas)",
                    placeholder="Ej: Diabetes, Hipertensión, Asma"
                )
                allergies = st.text_area(
                    "Alergias conocidas (separadas por comas)",
                    placeholder="Ej: Penicilina, Mariscos, Polen"
                )
                current_medications = st.text_area(
                    "Medicamentos actuales (separadas por comas)",
                    placeholder="Ej: Metformina, Losartán"
                )
            
            submitted = st.form_submit_button("✅ Guardar Perfil", type="primary")
            
            if submitted:
                if name and age and location:
                    user_id = str(uuid.uuid4())
                    
                    profile_data = {
                        'user_id': user_id,
                        'name': name,
                        'age': str(age),
                        'location': location,
                        'phone': phone,
                        'emergency_contact': emergency_contact,
                        'chronic_conditions': [c.strip() for c in chronic_conditions.split(',') if c.strip()],
                        'allergies': [a.strip() for a in allergies.split(',') if a.strip()],
                        'current_medications': [m.strip() for m in current_medications.split(',') if m.strip()],
                        'created_at': datetime.now().isoformat(),
                        'last_updated': datetime.now().isoformat()
                    }
                    
                    if save_user_profile(profile_data):
                        st.session_state.current_user_id = user_id
                        st.session_state.user_profile = profile_data
                        st.session_state.user_initialized = True
                        st.session_state.medical_history = load_medical_history(user_id)
                        st.success("¡Perfil guardado exitosamente!")
                        st.rerun()
                    else:
                        st.error("Error al guardar el perfil. Inténtalo de nuevo.")
                else:
                    st.error("Por favor completa los campos obligatorios (*)")

def get_system_prompts():
    user_profile = st.session_state.get('user_profile', {})
    medical_history = st.session_state.get('medical_history', [])
    herbal_db = st.session_state.get('herbal_database', {})
    generic_db = st.session_state.get('generic_database', {})
    
    return {
        'health_assistant': f"""Eres un asistente de salud especializado para comunidades rurales de Sudamérica con acceso limitado a servicios médicos.

## Contexto del Usuario:
- Información personal: {json.dumps(user_profile, ensure_ascii=False)}
- Historial médico: {json.dumps(medical_history[-5:], ensure_ascii=False)}
- Plantas medicinales disponibles: {json.dumps(list(herbal_db.keys()), ensure_ascii=False)}
- Medicamentos genéricos disponibles: {json.dumps(list(generic_db.keys()), ensure_ascii=False)}

## Tu Rol Principal:
EVALUAR el estado de salud considerando el perfil completo del usuario
PROPORCIONAR orientación médica básica adaptada al contexto rural
RECOMENDAR tratamientos accesibles priorizando plantas medicinales locales
IDENTIFICAR niveles de urgencia médica
DOCUMENTAR cada consulta para seguimiento

## Principios:
- Usa español simple y claro
- Sé empático y culturalmente sensible
- Considera limitaciones de recursos
- NUNCA diagnostiques sin confirmación médica
- Prioriza la seguridad del paciente""",

        'emergency_assessment': """Eres un evaluador de emergencias médicas para áreas rurales.

## Protocolo de Evaluación Rápida:
🔴 EMERGENCIA VITAL: Instrucciones inmediatas + transporte urgente
🟡 URGENTE NO VITAL: Estabilización + atención en 24h
🟢 NO URGENTE: Cuidados en casa + seguimiento

En emergencias, sé directo y claro. Cada minuto cuenta.""",

        'daily_checkin': """Analiza los datos del check-in diario para identificar patrones y riesgos.

## Métricas a Evaluar:
1. Hidratación: Meta mínima 8 vasos/día
2. Actividad física: Recomendado 30 min/día  
3. Bienestar general: Tendencias emocionales

Identifica patrones preocupantes y da recomendaciones personalizadas con tono motivador."""
    }

def check_ollama_connection(host):
    """Check if Ollama is running and accessible"""
    try:
        response = requests.get(f"{host}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def call_ollama_api(host, model, prompt, image_base64=None, temperature=0.7, max_tokens=512, system_prompt=""):
    """Call the Ollama API with text and optional image"""
    url = f"{host}/api/generate"
    full_prompt = f"{system_prompt}\n\nUsuario: {prompt}" if system_prompt else prompt

    payload = {
        "model": model,
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }

    if image_base64:
        payload["images"] = [image_base64]

    try:
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=120)
        end_time = time.time()

        if response.status_code != 200:
            return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}

        result = response.json()
        response_time = end_time - start_time

        if "response" in result:
            return {
                "success": True,
                "text": result["response"],
                "response_time": response_time,
                "model": model
            }
        else:
            return {"success": False, "error": "No response in result"}

    except Exception as e:
        return {"success": False, "error": f"Error: {str(e)}"}

def save_consultation_to_history(user_input, ai_response, assessment_level="", consultation_type="general", chat_history=None):
    """Save consultation to medical history, now including chat history"""
    if 'current_user_id' not in st.session_state:
        return False
        
    user_id = st.session_state.current_user_id
    medical_history = load_medical_history(user_id)
    
    # Ensure chat history is serializable (no image objects)
    serializable_chat = []
    if chat_history:
        for msg in chat_history:
            new_msg = msg.copy()
            if "image" in new_msg:
                # Replace image object with a placeholder or filename for the history
                new_msg["image"] = "[Imagen adjunta]"
            serializable_chat.append(new_msg)

    consultation = {
        'id': str(uuid.uuid4()),
        'timestamp': datetime.now().isoformat(),
        'type': consultation_type,
        'user_input': user_input,
        'ai_response': ai_response,
        'assessment_level': assessment_level,
        'chat_history': serializable_chat if serializable_chat else []
    }
    
    medical_history.append(consultation)
    
    if save_medical_history(user_id, medical_history):
        st.session_state.medical_history = medical_history
        return True
    return False

# --- Main application starts here ---

initialize_session_state()

# Show user profile popup if not initialized
if not st.session_state.user_initialized or not st.session_state.current_user_id:
    # ... (This logic is unchanged)
    profile_files = [f for f in os.listdir('data') if f.startswith('perfil_usuario_') and f.endswith('.txt')] if os.path.exists('data') else []
    
    if profile_files:
        st.sidebar.header("👤 Usuario Existente")
        selected_profile = st.sidebar.selectbox("Seleccionar perfil:", 
                                               ["Crear nuevo perfil"] + profile_files)
        
        if selected_profile != "Crear nuevo perfil":
            try:
                user_id = selected_profile.replace('perfil_usuario_', '').replace('.txt', '')
                profile_data = load_user_profile(user_id)
                
                if st.sidebar.button("Cargar Perfil"):
                    st.session_state.current_user_id = user_id
                    st.session_state.user_profile = profile_data
                    st.session_state.user_initialized = True
                    st.session_state.medical_history = load_medical_history(user_id)
                    st.rerun()
            except Exception as e:
                st.sidebar.error(f"Error loading profile: {e}")
    
    if not st.session_state.user_initialized:
        show_user_profile_popup()
        st.stop()


# Main Application Layout
st.title("🏥 Asistente de Salud Rural")
st.markdown("Atención médica básica para comunidades rurales de Sudamérica")

user_profile = st.session_state.user_profile
st.info(f"👤 Usuario: {user_profile.get('name', 'No especificado')} | 📍 {user_profile.get('location', 'No especificado')}")

# Sidebar Configuration
st.sidebar.header("⚙️ Configuración")
ollama_host = st.sidebar.text_input("Ollama Host:", value="http://localhost:11434")
model_name = st.sidebar.selectbox("Modelo:", ["gemma3:4b"])

if check_ollama_connection(ollama_host):
    st.sidebar.success("✅ Conectado a Ollama")
else:
    st.sidebar.error("❌ Ollama desconectado")

# --- UPDATED: Voice Input Button in Sidebar ---
st.sidebar.markdown("---")
st.sidebar.header("🎤 Entrada de Voz")
if st.sidebar.button("Enviar mensaje de Voz al IA"):
    # Set the state to trigger the dialog on the next rerun
    st.session_state.run_voice_recorder = True

# --- NEW: Handle the voice recording dialog ---
if st.session_state.get("run_voice_recorder", False):
    @st.dialog("Grabar Mensaje de Voz")
    def voice_recorder_dialog():
        st.write("Haz clic en el ícono del micrófono para empezar a grabar tu consulta.")
        audio = audiorecorder("🎤 Grabar", "⏹️ Detener")

        if len(audio) > 0:
            st.audio(audio.export().read())
            
            with st.spinner("Transcribiendo audio..."):
                # Save audio to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
                    audio.export(temp_audio_file.name, format="wav")
                    temp_audio_file_path = temp_audio_file.name

                try:
                    r = sr.Recognizer()
                    with sr.AudioFile(temp_audio_file_path) as source:
                        audio_data = r.record(source)
                        # Transcribe using Google's free web API
                        text = r.recognize_google(audio_data, language='es-ES')
                        st.session_state.voice_input = text
                        st.success("Transcripción completada. Cierra esta ventana.")
                except sr.UnknownValueError:
                    st.error("No se pudo entender el audio. Inténtalo de nuevo.")
                except sr.RequestError as e:
                    st.error(f"Error en el servicio de reconocimiento de voz; {e}")
                finally:
                    # Clean up the temporary file
                    os.remove(temp_audio_file_path)

        if st.button("Cerrar"):
            st.session_state.run_voice_recorder = False
            st.rerun()
    
    # This will open the dialog
    voice_recorder_dialog()

# Main Interface Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💪 Consulta Diaria", "🩺 Evaluación Médica", "🌿 Plantas Medicinales", 
    "📋 Historial Médico", "📄 Reporte PDF"
])

# ... Tab 1 is unchanged ...
with tab1:
    st.header("💪 Check-in Diario de Salud")
    st.markdown("Registra tu estado de salud diario para un mejor seguimiento")
    
    # Daily check-in form
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💧 Hidratación")
            water_intake = st.slider(
                "¿Cuántos vasos de agua has tomado hoy?", 
                0, 15, 8, 
                help="Meta recomendada: 8 vasos por día"
            )
            st.progress(min(water_intake / 8, 1.0))
            
            st.subheader("🏃‍♂️ Actividad Física")
            exercise_minutes = st.slider(
                "¿Cuántos minutos de ejercicio/actividad física?", 
                0, 180, 30,
                help="Meta recomendada: 30 minutos por día"
            )
            st.progress(min(exercise_minutes / 30, 1.0))
        
        with col2:
            st.subheader("😊 Bienestar General")
            wellness_score = st.select_slider(
                "¿Cómo te sientes hoy? (1-10)",
                options=[1,2,3,4,5,6,7,8,9,10],
                value=7,
                format_func=lambda x: f"{x} {'😔' if x<=3 else '😐' if x<=6 else '😊' if x<=8 else '😄'}"
            )
            
            st.subheader("💤 Calidad del Sueño")
            sleep_quality = st.select_slider(
                "¿Cómo dormiste anoche?",
                options=["Muy mal", "Mal", "Regular", "Bien", "Muy bien"],
                value="Bien"
            )
            
            st.subheader("📝 Notas Adicionales")
            daily_notes = st.text_area(
                "¿Algo más que quieras registrar?",
                placeholder="Síntomas, molestias, observaciones...",
                height=100
            )
    
    if st.button("💾 Guardar Check-in Diario", type="primary"):
        checkin_data = {
            'water_intake': water_intake,
            'exercise_minutes': exercise_minutes,
            'wellness_score': wellness_score,
            'sleep_quality': sleep_quality,
            'daily_notes': daily_notes
        }
        
        if save_daily_checkin(st.session_state.current_user_id, checkin_data):
            st.success("✅ Check-in guardado exitosamente!")
            
            # Analyze check-in data
            system_prompts = get_system_prompts()
            analysis_prompt = f"""
            Datos del check-in diario:
            - Hidratación: {water_intake} vasos (meta: 8)
            - Ejercicio: {exercise_minutes} minutos (meta: 30)
            - Bienestar: {wellness_score}/10
            - Sueño: {sleep_quality}
            - Notas: {daily_notes}
            
            Analiza estos datos y proporciona recomendaciones personalizadas.
            """
            
            with st.spinner("Analizando tu check-in..."):
                result = call_ollama_api(
                    ollama_host, model_name, analysis_prompt,
                    temperature=0.3, max_tokens=600,
                    system_prompt=system_prompts['daily_checkin']
                )
            
            if result["success"]:
                st.info("🤖 Análisis de tu check-in diario:")
                st.write(result["text"])
                
                # Save analysis to history
                save_consultation_to_history(
                    f"Check-in diario: Agua:{water_intake}, Ejercicio:{exercise_minutes}min, Bienestar:{wellness_score}/10",
                    result["text"],
                    consultation_type="daily_checkin"
                )

# --- UPDATED: Tab 2 with voice input handling ---
with tab2:
    st.header("🩺 Evaluación Médica Avanzada")
    st.markdown("Chat interactivo para evaluación de síntomas con soporte de imágenes")
    
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_messages:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
                    if "image" in message and message["image"]:
                        st.image(message["image"], width=200)
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])
    
    # Input area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # The key ensures that the text_area updates when voice_input changes
        user_message = st.text_area(
            "Describe tus síntomas o preguntas médicas:",
            key=f"user_message_input_{st.session_state.voice_input}",
            height=100,
            placeholder="Escribe aquí o usa el botón 'Grabar Audio' en el menú lateral.",
            value=st.session_state.get("voice_input", "")
        )
        # Clear voice input from state after it has been used
        if st.session_state.voice_input:
            st.session_state.voice_input = ""

    # ... The rest of Tab 2 and other tabs are mostly unchanged ...
    with col2:
        uploaded_image = st.file_uploader(
            "Subir imagen médica:",
            type=['png', 'jpg', 'jpeg'],
            help="Heridas, erupciones, medicamentos, etc."
        )
        
        if uploaded_image:
            image = Image.open(uploaded_image)
            st.image(image, width=150)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("💬 Enviar Consulta", type="primary"):
            if user_message.strip():
                user_msg = {"role": "user", "content": user_message}
                image_base64 = None
                
                if uploaded_image:
                    img_bytes = uploaded_image.getvalue()
                    user_msg["image"] = img_bytes # Store bytes for display
                    image_base64 = base64.b64encode(img_bytes).decode('utf-8')

                st.session_state.chat_messages.append(user_msg)
                
                system_prompts = get_system_prompts()
                with st.spinner("Analizando consulta médica..."):
                    result = call_ollama_api(
                        ollama_host, model_name, user_message, image_base64,
                        temperature=0.3, max_tokens=800,
                        system_prompt=system_prompts['health_assistant']
                    )
                
                if result["success"]:
                    st.session_state.chat_messages.append({
                        "role": "assistant", 
                        "content": result["text"]
                    })
                    
                    save_consultation_to_history(
                        user_message, result["text"], 
                        consultation_type="medical_evaluation",
                        chat_history=st.session_state.chat_messages
                    )
                    
                    st.rerun()
                else:
                    st.error(f"Error en la consulta: {result['error']}")
    
    with col2:
        if st.button("🗑️ Limpiar Chat"):
            st.session_state.chat_messages = []
            st.rerun()
    
    # Emergency Assessment Box
    st.markdown("---")
    st.error("🚨 **EVALUACIÓN DE EMERGENCIA**")
    
    emergency_symptoms = st.text_area(
        "¿Presentas alguno de estos síntomas de emergencia?",
        placeholder="Dolor en el pecho, dificultad para respirar, pérdida de consciencia, sangrado abundante...",
        height=80
    )
    
    if st.button("🚨 EVALUAR EMERGENCIA", type="primary"):
        if emergency_symptoms.strip():
            system_prompts = get_system_prompts()
            emergency_prompt = f"""
            SÍNTOMAS DE EMERGENCIA REPORTADOS: {emergency_symptoms}
            
            Evalúa INMEDIATAMENTE el nivel de urgencia y proporciona instrucciones de primeros auxilios.
            """
            
            with st.spinner("🚨 Evaluando emergencia..."):
                result = call_ollama_api(
                    ollama_host, model_name, emergency_prompt,
                    temperature=0.1, max_tokens=600,
                    system_prompt=system_prompts['emergency_assessment']
                )
            
            if result["success"]:
                response = result["text"]
                if "🔴" in response or "EMERGENCIA" in response.upper():
                    st.error("🔴 **EMERGENCIA MÉDICA DETECTADA**")
                    st.error(response)
                elif "🟡" in response or "URGENTE" in response.upper():
                    st.warning("🟡 **ATENCIÓN MÉDICA URGENTE REQUERIDA**")
                    st.warning(response)
                else:
                    st.info("🟢 **SEGUIMIENTO RECOMENDADO**")
                    st.info(response)
                
                # Save emergency assessment
                save_consultation_to_history(
                    f"EMERGENCIA: {emergency_symptoms}", 
                    response, 
                    assessment_level="EMERGENCY",
                    consultation_type="emergency"
                )

# --- The rest of the tabs (3, 4, 5) and the footer remain the same. ---
# ... Code for tabs 3, 4, 5, and footer ...
with tab3:
    st.header("🌿 Base de Datos de Plantas Medicinales")
    st.markdown("Plantas medicinales tradicionales de Sudamérica con información científica")
    
    # Search and filter
    col1, col2 = st.columns([2, 1])
    with col1:
        search_term = st.text_input("🔍 Buscar por nombre o síntoma:", placeholder="Ej: dolor de cabeza, manzanilla...")
    with col2:
        show_all = st.checkbox("Mostrar todas las plantas", value=False)
    
    herbal_db = st.session_state.herbal_database
    
    # Filter plants based on search
    filtered_plants = {}
    if show_all or not search_term:
        filtered_plants = herbal_db
    else:
        search_lower = search_term.lower()
        for plant_key, plant_data in herbal_db.items():
            if (search_lower in plant_data['name'].lower() or 
                search_lower in plant_data['scientific_name'].lower() or
                any(search_lower in use.lower() for use in plant_data['uses'])):
                filtered_plants[plant_key] = plant_data
    
    # Display plants in expandable cards
    if filtered_plants:
        for plant_key, plant_data in filtered_plants.items():
            with st.expander(f"🌱 {plant_data['name']}", expanded=len(filtered_plants) <= 3):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Nombre científico:** {plant_data['scientific_name']}")
                    st.markdown(f"**Región:** {plant_data['region']}")
                    st.markdown("**Usos tradicionales:**")
                    for use in plant_data['uses']:
                        st.markdown(f"• {use}")
                
                with col2:
                    st.markdown(f"**Preparación:** {plant_data['preparation']}")
                    st.markdown("**⚠️ Contraindicaciones:**")
                    for contra in plant_data['contraindications']:
                        st.markdown(f"• {contra}")
                
                # Quick consultation button
                if st.button(f"💬 Consultar sobre {plant_data['name']}", key=f"consult_{plant_key}"):
                    plant_question = f"Cuéntame más sobre los usos medicinales de {plant_data['name']} para mi condición de salud actual."
                    
                    system_prompts = get_system_prompts()
                    with st.spinner(f"Consultando sobre {plant_data['name']}..."):
                        result = call_ollama_api(
                            ollama_host, model_name, plant_question,
                            temperature=0.3, max_tokens=600,
                            system_prompt=system_prompts['health_assistant']
                        )
                    
                    if result["success"]:
                        st.success(f"Información sobre {plant_data['name']}:")
                        st.write(result["text"])
                        
                        save_consultation_to_history(
                            plant_question, result["text"], 
                            consultation_type="herbal_consultation"
                        )
    else:
        st.info("No se encontraron plantas medicinales que coincidan con tu búsqueda.")
    
    # Add new plant (for healthcare providers)
    with st.expander("➕ Agregar Nueva Planta Medicinal"):
        st.markdown("*Solo para profesionales de la salud*")
        
        with st.form("new_plant_form"):
            new_name = st.text_input("Nombre común:")
            new_scientific = st.text_input("Nombre científico:")
            new_uses = st.text_area("Usos medicinales (separados por comas):")
            new_preparation = st.text_area("Método de preparación:")
            new_contraindications = st.text_area("Contraindicaciones (separadas por comas):")
            new_region = st.text_input("Región de disponibilidad:")
            
            if st.form_submit_button("Agregar Planta"):
                if new_name and new_scientific and new_uses:
                    plant_key = new_name.lower().replace(' ', '_')
                    
                    new_plant_data = {
                        'name': new_name,
                        'scientific_name': new_scientific,
                        'uses': [u.strip() for u in new_uses.split(',') if u.strip()],
                        'preparation': new_preparation,
                        'contraindications': [c.strip() for c in new_contraindications.split(',') if c.strip()],
                        'region': new_region
                    }
                    
                    herbal_db[plant_key] = new_plant_data
                    
                    # Save to file
                    try:
                        with open('data/plantas_medicinales.txt', 'w', encoding='utf-8') as f:
                            json.dump(herbal_db, f, indent=2, ensure_ascii=False)
                        
                        st.session_state.herbal_database = herbal_db
                        st.success(f"✅ Planta {new_name} agregada exitosamente!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al guardar: {e}")
                else:
                    st.error("Por favor completa los campos obligatorios.")

with tab4:
    st.header("📋 Historial Médico Completo")
    st.markdown("Registro completo de consultas, check-ins y evaluaciones")
    
    medical_history = st.session_state.medical_history
    
    # Summary statistics
    if medical_history:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total Consultas", len(medical_history))
        
        with col2:
            emergency_count = sum(1 for entry in medical_history 
                                if entry.get('assessment_level') == 'EMERGENCY' or 
                                   entry.get('type') == 'emergency')
            st.metric("🚨 Emergencias", emergency_count)
        
        with col3:
            recent_count = sum(1 for entry in medical_history 
                             if datetime.fromisoformat(entry['timestamp']) > 
                             datetime.now() - timedelta(days=7))
            st.metric("📅 Última Semana", recent_count)
        
        with col4:
            checkin_count = sum(1 for entry in medical_history 
                              if entry.get('type') == 'daily_checkin')
            st.metric("💪 Check-ins", checkin_count)
        
        st.markdown("---")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            filter_type = st.selectbox(
                "Filtrar por tipo:",
                ["Todas", "general", "medical_evaluation", "daily_checkin", "emergency", "herbal_consultation"]
            )
        
        with col2:
            date_range = st.selectbox(
                "Período:",
                ["Todos", "Última semana", "Último mes", "Últimos 3 meses"]
            )
        
        # Apply filters
        filtered_history = medical_history.copy()
        
        if filter_type != "Todas":
            filtered_history = [entry for entry in filtered_history 
                              if entry.get('type') == filter_type]
        
        if date_range != "Todos":
            days_map = {"Última semana": 7, "Último mes": 30, "Últimos 3 meses": 90}
            cutoff_date = datetime.now() - timedelta(days=days_map[date_range])
            filtered_history = [entry for entry in filtered_history 
                              if datetime.fromisoformat(entry['timestamp']) > cutoff_date]
        
        # Display filtered history
        if filtered_history:
            for i, entry in enumerate(reversed(filtered_history), 1):
                entry_date = datetime.fromisoformat(entry['timestamp'])
                
                # Determine entry type icon and color
                type_info = {
                    'general': ('💬', 'blue'),
                    'medical_evaluation': ('🩺', 'green'),
                    'daily_checkin': ('💪', 'orange'),
                    'emergency': ('🚨', 'red'),
                    'herbal_consultation': ('🌿', 'purple')
                }
                
                icon, color = type_info.get(entry.get('type', 'general'), ('💬', 'blue'))
                
                with st.expander(
                    f"{icon} {entry_date.strftime('%d/%m/%Y %H:%M')} - {entry.get('type', 'general').replace('_', ' ').title()}",
                    expanded=i <= 3
                ):
                    col1, col2 = st.columns([2, 3])
                    
                    with col1:
                        st.markdown("**Consulta/Síntomas:**")
                        st.write(entry['user_input'][:200] + "..." if len(entry['user_input']) > 200 else entry['user_input'])
                        
                        if entry.get('assessment_level'):
                            level_colors = {
                                'EMERGENCY': '🔴',
                                'URGENTE': '🟡',
                                'MODERADO': '🟡',
                                'LEVE': '🟢'
                            }
                            level_icon = level_colors.get(entry['assessment_level'], '⚪')
                            st.markdown(f"**Nivel:** {level_icon} {entry['assessment_level']}")
                    
                    with col2:
                        st.markdown("**Respuesta/Recomendaciones:**")
                        st.write(entry['ai_response'][:300] + "..." if len(entry['ai_response']) > 300 else entry['ai_response'])
        else:
            st.info("No hay registros que coincidan con los filtros seleccionados.")
        
        # Export options
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Exportar Historial (JSON)"):
                export_data = {
                    'user_profile': st.session_state.user_profile,
                    'medical_history': medical_history,
                    'export_date': datetime.now().isoformat(),
                    'total_entries': len(medical_history)
                }
                
                st.download_button(
                    label="💾 Descargar Historial JSON",
                    data=json.dumps(export_data, indent=2, ensure_ascii=False),
                    file_name=f"historial_medico_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("📈 Análisis de Tendencias"):
                # Simple trend analysis
                if len(medical_history) > 5:
                    trend_prompt = f"""
                    Analiza las siguientes consultas médicas de los últimos registros:
                    {json.dumps(medical_history[-10:], ensure_ascii=False)}
                    
                    Identifica patrones, tendencias preocupantes y mejoras en la salud del usuario.
                    """
                    
                    system_prompts = get_system_prompts()
                    with st.spinner("Analizando tendencias de salud..."):
                        result = call_ollama_api(
                            ollama_host, model_name, trend_prompt,
                            temperature=0.3, max_tokens=800,
                            system_prompt=system_prompts['health_assistant']
                        )
                    
                    if result["success"]:
                        st.success("📈 Análisis de Tendencias de Salud:")
                        st.write(result["text"])
                else:
                    st.info("Se necesitan más consultas para analizar tendencias.")
    
    else:
        st.info("📝 No hay registros médicos todavía. Comienza con un check-in diario o una consulta médica.")

with tab5:
    st.header("📄 Reporte Médico Profesional")
    st.markdown("Genera reportes detallados para compartir con profesionales de la salud")
    
    if st.session_state.medical_history:
        # Report configuration
        # Enhanced report configuration with AI options
        st.markdown("### 🤖 Configuración del Reporte Inteligente")
        
        col1, col2 = st.columns(2)
        
        with col1:
            report_period = st.selectbox(
                "Período del reporte:",
                ["Última semana", "Último mes", "Últimos 3 meses", "Todo el historial"]
            )
            
            include_checkins = st.checkbox("Incluir check-ins diarios", value=True)
            include_emergency = st.checkbox("Incluir evaluaciones de emergencia", value=True)
        
        with col2:
            report_format = st.selectbox(
                "Formato del reporte:",
                ["PDF Completo", "PDF Resumido", "Datos JSON"]
            )
            
            include_trends = st.checkbox("🤖 Incluir análisis médico con IA", value=True, 
                                       help="Genera un resumen profesional usando Gemma 3")
            include_recommendations = st.checkbox("Incluir recomendaciones detalladas", value=True)
        
        # Show AI analysis status
        if include_trends:
            if check_ollama_connection(ollama_host):
                st.success("✅ Análisis con IA disponible - Se generará resumen médico profesional")
            else:
                st.warning("⚠️ Ollama desconectado - El análisis con IA no estará disponible")
        
        # Show data summary before generation
        filtered_preview = st.session_state.medical_history.copy()
        if report_period != "Todo el historial":
            days_map = {"Última semana": 7, "Último mes": 30, "Últimos 3 meses": 90}
            cutoff_date = datetime.now() - timedelta(days=days_map[report_period])
            filtered_preview = [entry for entry in filtered_preview 
                              if datetime.fromisoformat(entry['timestamp']) > cutoff_date]
        
        st.info(f"📊 Este reporte incluirá {len(filtered_preview)} consultas del período seleccionado")
        
        if st.button("📄 Generar Reporte", type="primary"):
            try:
                # Filter history based on period
                history_to_include = st.session_state.medical_history.copy()
                
                if report_period != "Todo el historial":
                    days_map = {"Última semana": 7, "Último mes": 30, "Últimos 3 meses": 90}
                    cutoff_date = datetime.now() - timedelta(days=days_map[report_period])
                    history_to_include = [entry for entry in history_to_include 
                                        if datetime.fromisoformat(entry['timestamp']) > cutoff_date]
                
                # Apply additional filters
                if not include_checkins:
                    history_to_include = [entry for entry in history_to_include 
                                        if entry.get('type') != 'daily_checkin']
                
                if not include_emergency:
                    history_to_include = [entry for entry in history_to_include 
                                        if entry.get('type') != 'emergency']

                # Generate AI summary first
                ai_summary = None
                if include_trends and check_ollama_connection(ollama_host):
                    with st.spinner("🤖 Generando análisis médico con IA..."):
                        ai_result = generate_ai_patient_summary(
                            st.session_state.user_profile, 
                            history_to_include, 
                            ollama_host, 
                            model_name
                        )
                        
                        if ai_result["success"]:
                            ai_summary = ai_result["summary"]
                            st.success("✅ Análisis médico completado")
                            
                            # Show preview of AI summary
                            with st.expander("👁️ Vista previa del análisis médico", expanded=True):
                                st.write(ai_summary)
                        else:
                            st.warning(f"⚠️ No se pudo generar el análisis IA: {ai_result['error']}")
                
                if report_format == "Datos JSON":
                    # Enhanced JSON export with AI summary
                    report_data = {
                        'patient_info': st.session_state.user_profile,
                        'ai_medical_summary': ai_summary,
                        'medical_history': history_to_include,
                        'report_config': {
                            'period': report_period,
                            'generated_date': datetime.now().isoformat(),
                            'total_entries': len(history_to_include),
                            'ai_analysis_included': ai_summary is not None
                        }
                    }
                    
                    st.download_button(
                        label="📁 Descargar Reporte JSON con Análisis IA",
                        data=json.dumps(report_data, indent=2, ensure_ascii=False),
                        file_name=f"reporte_medico_ia_{datetime.now().strftime('%Y%m%d')}.json",
                        mime="application/json"
                    )
                
                else:
                    # Enhanced PDF report generation with AI summary
                    def generate_enhanced_pdf_report_with_ai(user_profile, medical_history, config, ai_summary=None):
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                        doc = SimpleDocTemplate(temp_file.name, pagesize=letter)
                        styles = getSampleStyleSheet()
                        story = []

                        # Title
                        title_style = ParagraphStyle(
                            'CustomTitle',
                            parent=styles['Heading1'],
                            fontSize=18,
                            textColor=colors.darkblue,
                            alignment=1
                        )
                        story.append(Paragraph("REPORTE MÉDICO - ASISTENTE DE SALUD RURAL", title_style))
                        if ai_summary:
                            story.append(Paragraph("Incluye Análisis Médico con Inteligencia Artificial", styles['Normal']))
                        story.append(Spacer(1, 20))

                        # Patient information (same as before)
                        story.append(Paragraph("INFORMACIÓN DEL PACIENTE", styles['Heading2']))
                        patient_data = [
                            ['Nombre:', user_profile.get('name', 'No especificado')],
                            ['Edad:', user_profile.get('age', 'No especificado')],
                            ['Ubicación:', user_profile.get('location', 'No especificado')],
                            ['Teléfono:', user_profile.get('phone', 'No especificado')],
                            ['Contacto de emergencia:', user_profile.get('emergency_contact', 'No especificado')],
                            ['Período del reporte:', config['period']],
                            ['Fecha de generación:', datetime.now().strftime('%d/%m/%Y %H:%M')]
                        ]

                        patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
                        patient_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 0), (-1, -1), 10),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ]))
                        story.append(patient_table)
                        story.append(Spacer(1, 20))

                        # NEW: AI Medical Summary Section
                        if ai_summary:
                            story.append(Paragraph("ANÁLISIS MÉDICO CON INTELIGENCIA ARTIFICIAL", styles['Heading2']))
                            
                            # Create a highlighted box for AI summary
                            ai_style = ParagraphStyle(
                                'AIAnalysis',
                                parent=styles['Normal'],
                                fontSize=10,
                                textColor=colors.darkblue,
                                leftIndent=10,
                                rightIndent=10,
                                spaceAfter=10,
                                borderColor=colors.lightblue,
                                borderWidth=1,
                                borderPadding=10
                            )
                            
                            story.append(Paragraph(ai_summary.replace('\n', '<br/>'), ai_style))
                            story.append(Spacer(1, 20))

                        # Medical conditions (same as before)
                        if user_profile.get('chronic_conditions') or user_profile.get('allergies'):
                            story.append(Paragraph("CONDICIONES MÉDICAS", styles['Heading2']))
                            
                            if user_profile.get('chronic_conditions'):
                                story.append(Paragraph(f"<b>Condiciones crónicas:</b> {', '.join(user_profile['chronic_conditions'])}", styles['Normal']))
                            
                            if user_profile.get('allergies'):
                                story.append(Paragraph(f"<b>Alergias:</b> {', '.join(user_profile['allergies'])}", styles['Normal']))
                            
                            if user_profile.get('current_medications'):
                                story.append(Paragraph(f"<b>Medicamentos actuales:</b> {', '.join(user_profile['current_medications'])}", styles['Normal']))
                            
                            story.append(Spacer(1, 15))

                        # Enhanced consultation summary
                        story.append(Paragraph("RESUMEN DE CONSULTAS", styles['Heading2']))
                        
                        # Statistics
                        total_consultations = len(medical_history)
                        emergency_count = sum(1 for entry in medical_history if entry.get('type') == 'emergency')
                        checkin_count = sum(1 for entry in medical_history if entry.get('type') == 'daily_checkin')
                        medical_eval_count = sum(1 for entry in medical_history if entry.get('type') == 'medical_evaluation')
                        
                        summary_data = [
                            ['Total de consultas:', str(total_consultations)],
                            ['Evaluaciones médicas:', str(medical_eval_count)],
                            ['Evaluaciones de emergencia:', str(emergency_count)],
                            ['Check-ins diarios:', str(checkin_count)],
                            ['Análisis IA incluido:', 'Sí' if ai_summary else 'No']
                        ]
                        
                        summary_table = Table(summary_data, colWidths=[3*inch, 1*inch])
                        summary_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 0), (-1, -1), 10)
                        ]))
                        story.append(summary_table)
                        story.append(Spacer(1, 15))

                        # Rest of the consultation details (same as before but limit to recent ones if AI summary is included)
                        story.append(Paragraph("DETALLE DE CONSULTAS", styles['Heading2']))
                        
                        consultations = sorted(medical_history, key=lambda x: x['timestamp'], reverse=True)
                        
                        # If AI summary is included, limit detailed consultations to most recent 5
                        max_consultations = 5 if ai_summary else len(consultations)
                        
                        for i, consultation in enumerate(consultations[:max_consultations], 1):
                            entry_date = datetime.fromisoformat(consultation['timestamp'])
                            story.append(Paragraph(f"Consulta {i} - {entry_date.strftime('%d/%m/%Y %H:%M')}", styles['Heading3']))
                            
                            consultation_type = consultation.get('type', 'general').replace('_', ' ').title()
                            story.append(Paragraph(f"<b>Tipo:</b> {consultation_type}", styles['Normal']))
                            
                            if consultation.get('assessment_level'):
                                story.append(Paragraph(f"<b>Nivel de urgencia:</b> {consultation['assessment_level']}", styles['Normal']))
                            
                            # Shortened version for space efficiency when AI summary is included
                            if ai_summary and len(consultation['user_input']) > 200:
                                story.append(Paragraph(f"<b>Consulta:</b> {consultation['user_input'][:200]}...", styles['BodyText']))
                                story.append(Paragraph(f"<b>Respuesta:</b> {consultation['ai_response'][:200]}...", styles['BodyText']))
                            else:
                                story.append(Paragraph(f"<b>Síntomas/Consulta:</b>", styles['Normal']))
                                story.append(Paragraph(consultation['user_input'], styles['BodyText']))
                                story.append(Paragraph(f"<b>Evaluación y recomendaciones:</b>", styles['Normal']))
                                story.append(Paragraph(consultation['ai_response'], styles['BodyText']))

                            story.append(Spacer(1, 12))
                        
                        if ai_summary and len(consultations) > max_consultations:
                            story.append(Paragraph(f"... y {len(consultations) - max_consultations} consultas adicionales (ver historial completo para más detalles)", styles['Normal']))

                        doc.build(story)
                        return temp_file.name

                    config = {
                        'period': report_period,
                        'include_checkins': include_checkins,
                        'include_emergency': include_emergency,
                        'format': report_format
                    }
                    
                    with st.spinner("📄 Generando reporte PDF..."):
                        pdf_path = generate_enhanced_pdf_report_with_ai(
                            st.session_state.user_profile,
                            history_to_include,
                            config,
                            ai_summary
                        )
                    
                    with open(pdf_path, 'rb') as pdf_file:
                        filename_suffix = "_con_ia" if ai_summary else ""
                        st.download_button(
                            label="📄 Descargar Reporte PDF con Análisis IA" if ai_summary else "📄 Descargar Reporte PDF",
                            data=pdf_file.read(),
                            file_name=f"reporte_medico{filename_suffix}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf"
                        )
                    
                    os.unlink(pdf_path)
                    st.success("✅ ¡Reporte generado exitosamente!" + (" (incluye análisis médico con IA)" if ai_summary else ""))
                    
            except Exception as e:
                st.error(f"Error generando reporte: {str(e)}")
                st.info("Asegúrate de tener instaladas las dependencias: pip install reportlab")
    else:
        st.warning("📝 No hay datos suficientes para generar un reporte. Realiza algunas consultas primero.")

# Footer and emergency contacts
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **⚠️ Descargo de responsabilidad:** 
    Este asistente proporciona información general de salud y no reemplaza la consulta médica profesional. 
    En caso de emergencia, busque atención médica inmediata.
    """)

with col2:
    st.error("""
    **🚨 NÚMEROS DE EMERGENCIA:**
    - Ecuador: 911
    - Colombia: 123  
    - Perú: 116
    - Bolivia: 911
    """)

# Sidebar user management
st.sidebar.markdown("---")
st.sidebar.header("👤 Gestión de Usuario")

if st.sidebar.button("👤 Editar Perfil"):
    st.session_state.user_initialized = False
    st.rerun()

if st.sidebar.button("🗑️ Limpiar Historial"):
    if save_medical_history(st.session_state.current_user_id, []):
        st.session_state.medical_history = []
        st.sidebar.success("Historial limpiado")
    else:
        st.sidebar.error("Error al limpiar historial")

if st.sidebar.button("🔄 Cambiar Usuario"):
    st.session_state.user_initialized = False
    st.session_state.current_user_id = None
    st.rerun()

# Display current data directory info
st.sidebar.markdown("---")
if os.path.exists('data'):
    file_count = len([f for f in os.listdir('data') if f.endswith('.txt')])
    st.sidebar.info(f"📁 Archivos de datos: {file_count}")
else:
    st.sidebar.info("📁 Directorio de datos: No creado")