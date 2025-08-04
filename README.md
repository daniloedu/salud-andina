# 🏥 Asistente de Salud Rural

Una aplicación de asistente médico inteligente diseñada específicamente para comunidades rurales de Sudamérica con acceso limitado a servicios de salud. Utiliza inteligencia artificial local (Ollama + Gemma 3) para proporcionar orientación médica básica, evaluaciones de emergencia y recomendaciones de plantas medicinales.

---

## 🌟 Características Principales

### 🤖 Asistente Médico Inteligente
*   Evaluación de síntomas con análisis de imágenes médicas.
*   Identificación automática de niveles de emergencia médica.
*   Recomendaciones personalizadas basadas en el perfil del usuario.
*   Soporte para entrada de voz en español.

### 🌿 Base de Datos de Plantas Medicinales
*   Amplia biblioteca de plantas medicinales sudamericanas.
*   Información científica sobre usos, preparación y contraindicaciones.
*   Búsqueda inteligente por síntomas o nombres de plantas.
*   Capacidad de agregar nuevas plantas (para profesionales de salud).

### 📊 Seguimiento de Salud
*   Check-ins diarios de salud (hidratación, ejercicio, bienestar).
*   Historial médico completo con análisis de tendencias.
*   Métricas visuales de progreso de salud.

### 📄 Reportes Médicos Profesionales
*   Generación automática de reportes PDF.
*   Análisis médico inteligente con IA (Gemma 3).
*   Resúmenes profesionales para compartir con médicos.
*   Exportación de datos en formato JSON.

### 🔐 Privacidad y Seguridad
*   Todos los datos se almacenan localmente en el dispositivo del usuario.
*   Sin conexión a internet requerida para el funcionamiento básico (excepto transcripción de voz).
*   Control total del usuario sobre sus datos médicos.

---

## 🛠️ Instalación

### Prerrequisitos
*   Python 3.8 o superior.
*   Ollama instalado y ejecutándose localmente.
*   El modelo `gemma3:4b` descargado en Ollama.
*   FFmpeg instalado en tu sistema (para la grabación de audio).

### Paso 1: Instalar Ollama
*   **En Linux/macOS:**
    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
    ```
*   **En Windows:** Descargar el instalador desde [https://ollama.com/download](https://ollama.com/download).

### Paso 2: Descargar el modelo Gemma 3
```bash
ollama pull gemma3:4b
```

### Paso 3: Clonar el Repositorio
```bash
git clone https://github.com/daniloedu/salud-andina.git
cd asistente-salud-rural
Use code with caution.
```

### Paso 4: Instalar Dependencias de Python
```bash
pip install -r requirements.txt
```
### Paso 5: Ejecutar la Aplicación
```bash
streamlit run saludv2.py
```

## 📋 Dependencias
Crea un archivo requirements.txt con el siguiente contenido:
```text
streamlit>=1.33.0
requests>=2.31.0
Pillow>=10.0.0
reportlab>=4.0.0
pandas>=2.0.0
streamlit-audiorecorder>=0.0.5
SpeechRecognition>=3.10.0
pydub
```
## 🚀 Uso de la Aplicación

### 1. Configuración Inicial
Al abrir la aplicación por primera vez, completa tu perfil médico.
Incluye información sobre condiciones crónicas, alergias y medicamentos actuales. Esta información se usa para personalizar las recomendaciones.
### 2. Check-in Diario 💪
Registra tu hidratación diaria, minutos de actividad física, bienestar general y calidad del sueño.
### 3. Evaluación Médica 🩺
Chat interactivo: Describe tus síntomas en lenguaje natural.
Soporte de imágenes: Sube fotos de heridas, erupciones, o medicamentos.
Entrada de voz: Usa el botón de micrófono en el menú lateral para consultas habladas.
Evaluación de emergencias: Utiliza la sección especializada para situaciones críticas.
### 4. Plantas Medicinales 🌿
Busca plantas por nombre o síntoma.
Consulta información detallada sobre preparación, usos y contraindicaciones.
### 5. Historial Médico 📋
Revisa todas tus consultas anteriores, filtra por tipo o fecha, y analiza tendencias de salud con IA.
### 6. Reportes PDF 📄
Genera reportes profesionales para compartir con un médico. Personaliza el período y contenido del reporte y descárgalo en formato PDF o JSON.

## ⚙️ Configuración
Configuración de Ollama
Host predeterminado: http://localhost:11434
Modelo recomendado: gemma3:4b
Asegúrate de que Ollama esté ejecutándose antes de iniciar la aplicación.
Configuración de Voz
La aplicación usa la API de Google Web Speech para el reconocimiento de voz.
Requiere una conexión a internet activa solo para la transcripción de audio.
Está pre-configurado para español (es-ES).

## 📁 Estructura de Archivos
```
asistente-salud-rural/
├── saludv2.py                 # Aplicación principal de Streamlit
├── requirements.txt           # Dependencias de Python
├── README.md                  # Este archivo
└── data/                      # Directorio de datos (creado automáticamente)
    ├── perfil_usuario_*.txt   # Perfiles de usuario
    ├── historial_medico_*.txt # Historiales médicos
    ├── checkin_diario_*.txt   # Check-ins diarios
    ├── plantas_medicinales.txt  # Base de datos de plantas
    └── medicamentos_genericos.txt # Base de datos de medicamentos

```

## 🚨 Importante - Descargo de Responsabilidad
**⚠️ AVISO MÉDICO IMPORTANTE:**
Este asistente de salud es una herramienta de apoyo informativo y NO reemplaza la consulta, el diagnóstico o el tratamiento médico profesional.
- NO es un dispositivo médico certificado.
- NO debe usarse para diagnósticos definitivos.
- Las recomendaciones son puramente orientativas y educativas.
- En caso de una emergencia médica real, contacta a tus servicios locales de inmediato.

## 🤝 Contribuciones
Las contribuciones son bienvenidas, especialmente para:
- Añadir nuevas plantas medicinales regionales.
- Mejorar la interfaz de usuario y la accesibilidad.
- Traducir la aplicación a lenguas indígenas.
- Optimizar el rendimiento.

**Para contribuir:**
Haz un Fork del repositorio.
Crea una nueva rama (git checkout -b feature/nueva-funcionalidad).
Haz commit de tus cambios (git commit -am 'Agrega nueva funcionalidad').
Haz push a la rama (git push origin feature/nueva-funcionalidad).
Abre un Pull Request.

## 📄 Licencia
<<<<<<< HEAD
Este proyecto está bajo la Licencia MIT. Ver el archivo LICENSE para más detalles.
=======
Este proyecto está bajo la Licencia MIT. Ver el archivo LICENSE para más detalles.
>>>>>>> 80790d4 (First Commit)
