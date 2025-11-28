# Entorno Virtual para la Enseñanza de la Biofísica

<p align="center">
  <strong>Herramienta Interactiva para la Resolución de Problemas</strong>
</p>

---

## 📋 Descripción

Este proyecto presenta el desarrollo de un **entorno virtual** diseñado específicamente para facilitar la enseñanza y el aprendizaje de la Biofísica, centrándose en la práctica activa mediante la resolución de ejercicios.

La Biofísica es una asignatura fundamental en la formación de un bioquímico. Su aprendizaje se ve dificultado frecuentemente por la abstracción de sus conceptos y la necesidad de aplicar modelos matemáticos. La resolución de problemas es una estrategia pedagógica esencial para superar estas dificultades.

### Objetivos

- Proporcionar una plataforma centralizada e interactiva para el estudio de la Biofísica
- Facilitar la comprensión de conceptos biofísicos complejos a través de la práctica guiada
- Ofrecer retroalimentación inmediata mediante algoritmos personalizados
- Incrementar la motivación del estudiante promoviendo un aprendizaje activo y autónomo

---

## 🏗️ Arquitectura del Sistema

La aplicación está diseñada siguiendo una **arquitectura hexagonal (Ports & Adapters)**, lo que permite una separación clara entre la lógica de negocio y las interfaces de usuario. Esta decisión arquitectónica facilita:

- **Mantenibilidad**: Código organizado en capas con responsabilidades bien definidas
- **Testabilidad**: Componentes independientes que pueden probarse de forma aislada
- **Extensibilidad**: Posibilidad de añadir nuevos módulos sin afectar los existentes
- **Portabilidad futura**: El núcleo puede reutilizarse para una versión web sin modificaciones

```
┌─────────────────────────────────────────────────────────────────┐
│                        CAPA DE PRESENTACIÓN                     │
│                    (CustomTkinter - Desktop GUI)                │
├─────────────────────────────────────────────────────────────────┤
│                        CAPA DE SERVICIOS                        │
│              (Lógica de negocio - 100% independiente)           │
├─────────────────────────────────────────────────────────────────┤
│                        CAPA DE DOMINIO                          │
│         (Modelos de datos, Entidades, Solvers algorítmicos)     │
├─────────────────────────────────────────────────────────────────┤
│                        CAPA DE DATOS                            │
│              (Repositorios JSON, Gestión de archivos)           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📚 Módulos Principales

La plataforma contiene **cuatro módulos principales**:

### 1. Conferencias Digitales 📖

Repositorio organizado de contenido teórico que permite acceder a las conferencias de la asignatura en formato digital (PDF). Los materiales están organizados por temas para facilitar la navegación y el estudio secuencial.

### 2. Bibliografía Recomendada 📚

Apartado dedicado a las referencias bibliográficas del curso, incluyendo:
- Libros de texto principales
- Artículos científicos relevantes
- Recursos complementarios

Los documentos pueden almacenarse localmente en formato PDF para acceso sin conexión.

### 3. Problemas Propuestos 📝

Banco de ejercicios organizados por tema de la asignatura, que incluye:
- Enunciados detallados
- Datos proporcionados
- Soluciones paso a paso
- Clasificación por nivel de dificultad

### 4. Módulos Interactivos 🧮

**Núcleo innovador de la herramienta.** Los estudiantes, mediante algoritmos personalizados en Python, pueden introducir variables específicas y obtener retroalimentación inmediata.

#### 4.1 Módulo de Ósmosis

| Funcionalidad | Descripción |
|---------------|-------------|
| Cálculo de osmolaridad | Determina la osmolaridad a partir de concentración y coeficientes |
| Clasificación de tonicidad | Clasifica soluciones como hipotónicas, isotónicas o hipertónicas |
| Predicción de volumen celular | Genera gráficos del comportamiento del volumen celular |
| Análisis de respuesta celular | Predice lisis, crenación o equilibrio |

#### 4.2 Módulo de Patch Clamp

| Funcionalidad | Descripción |
|---------------|-------------|
| Ecuación de Nernst | Calcula potenciales de equilibrio iónico |
| Ecuación de Goldman-Hodgkin-Katz | Determina el potencial de membrana |
| Curvas I-V | Genera gráficos de corriente vs. voltaje |
| Simulación de experimentos | Interpreta resultados experimentales de Patch Clamp |

---

## 🛠️ Instalación y Configuración

### Requisitos Previos

- **Python 3.10 o superior**
- **pip** (gestor de paquetes de Python)
- **Git** (opcional, para clonar el repositorio)

### Paso 1: Clonar o Descargar el Proyecto

```bash
# Opción A: Clonar con Git
git clone <url-del-repositorio>
cd biofisica_entorno_virtual

# Opción B: Descargar y extraer el archivo ZIP
```

### Paso 2: Crear un Entorno Virtual (Recomendado)

Es altamente recomendable utilizar un entorno virtual para aislar las dependencias del proyecto:

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# En Windows (CMD):
.\venv\Scripts\activate.bat

# En Linux/macOS:
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Ejecutar la Aplicación

```bash
python src/main.py
```

---

## 📦 Dependencias

### Dependencias Principales

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| `customtkinter` | ≥5.2.0 | Interfaz gráfica moderna basada en Tkinter |
| `pillow` | ≥10.0.0 | Procesamiento de imágenes |
| `numpy` | ≥1.24.0 | Computación numérica |
| `scipy` | ≥1.11.0 | Funciones científicas avanzadas |
| `matplotlib` | ≥3.7.0 | Generación de gráficos |
| `pydantic` | ≥2.0.0 | Validación de datos y modelos |
| `pypdf` | ≥3.0.0 | Manejo de archivos PDF |
| `pyyaml` | ≥6.0 | Lectura de archivos de configuración |

### Dependencias de Desarrollo

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| `pytest` | ≥7.0.0 | Framework de pruebas |
| `pyinstaller` | ≥6.0.0 | Empaquetado como ejecutable |

---

## 📁 Estructura del Proyecto

```
biofisica_entorno_virtual/
│
├── src/                            # Código fuente
│   ├── main.py                     # Punto de entrada
│   ├── config.py                   # Configuraciones globales
│   │
│   ├── core/                       # Núcleo de la aplicación
│   │   ├── domain/                 # Modelos de datos
│   │   ├── services/               # Lógica de negocio
│   │   └── solvers/                # Algoritmos matemáticos
│   │       ├── osmosis/            # Módulo de ósmosis
│   │       └── patch_clamp/        # Módulo de Patch Clamp
│   │
│   ├── infrastructure/             # Acceso a datos
│   │   ├── json_repository.py      # Repositorio basado en JSON
│   │   └── file_manager.py         # Gestión de archivos
│   │
│   └── desktop/                    # Interfaz gráfica
│       ├── app.py                  # Aplicación principal
│       ├── components/             # Widgets reutilizables
│       └── views/                  # Vistas de cada módulo
│
├── data/                           # Datos de la aplicación
│   ├── conferences/                # Conferencias digitales
│   ├── bibliography/               # Referencias bibliográficas
│   ├── problems/                   # Banco de ejercicios
│   └── config.json                 # Configuración de usuario
│
├── assets/                         # Recursos estáticos
│   ├── icons/                      # Iconos de la aplicación
│   └── images/                     # Imágenes y diagramas
│
├── tests/                          # Pruebas unitarias
│
├── requirements.txt                # Dependencias de producción
├── requirements-dev.txt            # Dependencias de desarrollo
└── README.md                       # Este archivo
```

---

## 🚀 Distribución como Ejecutable Portable

Para crear un ejecutable portable que no requiera instalación de Python:

```bash
# Instalar PyInstaller (si no está instalado)
pip install pyinstaller

# Generar ejecutable
pyinstaller --onefile --windowed --icon=assets/icons/app_icon.ico --name="BiofisicaApp" src/main.py
```

El ejecutable se generará en la carpeta `dist/`.

### Estructura de Distribución

```
BiofisicaApp_v1.0/
├── BiofisicaApp.exe          # Ejecutable principal
├── data/                      # Carpeta de datos (copiar junto al .exe)
│   ├── conferences/
│   ├── bibliography/
│   └── problems/
└── README.txt                 # Instrucciones de uso
```

---

## 📖 Guía de Uso

### Navegación

La aplicación presenta una barra lateral izquierda con acceso a los cuatro módulos principales. El área central muestra el contenido del módulo seleccionado.

### Módulos Interactivos

1. **Seleccione el módulo** (Ósmosis o Patch Clamp) desde el menú lateral
2. **Introduzca los parámetros** en los campos correspondientes
3. **Pulse "Calcular"** para obtener los resultados
4. **Analice la retroalimentación** proporcionada, incluyendo gráficos si aplica

### Añadir Contenido

- **Conferencias**: Copie archivos PDF a `data/conferences/pdfs/`
- **Bibliografía**: Edite `data/bibliography/books.json` y añada PDFs a `data/bibliography/pdfs/`
- **Problemas**: Cree archivos JSON siguiendo la plantilla en `data/problems/`

---

## 🧪 Pruebas

Para ejecutar las pruebas unitarias:

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con cobertura
pytest --cov=src

# Ejecutar pruebas específicas
pytest tests/test_osmosis_solver.py -v
```

---

## 🔮 Desarrollo Futuro

La arquitectura del proyecto permite las siguientes extensiones:

- [ ] Añadir nuevos módulos interactivos (cinética enzimática, termodinámica)
- [ ] Implementar sistema de progreso del estudiante
- [ ] Exportar resultados a PDF
- [ ] Migración a versión web (FastAPI + React)
- [ ] Modo oscuro/claro configurable
- [ ] Soporte multiidioma

---

## 👥 Contribución

Este proyecto ha sido desarrollado como parte de una innovación didáctica para la enseñanza de la Biofísica. Las contribuciones son bienvenidas siguiendo las guías de estilo del proyecto.

---

## 📄 Licencia

Este proyecto está destinado a fines educativos. Consulte con los autores antes de cualquier uso comercial.

---

## 📞 Contacto

Para consultas académicas o técnicas relacionadas con este proyecto, contacte al equipo de desarrollo a través anagabrielazaragozapalmarola@gmail.com o sebagonz106@gmail.com

---

<p align="center">
  <em>Desarrollado como recurso educativo complementario para la enseñanza de la Biofísica</em>
</p>
