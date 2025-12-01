# Entorno Virtual para la Enseñanza de la Biofísica

<p align="center">
  <img src="data/img/bia_logo.png" alt="BIA Logo" width="200"/>
</p>

<p align="center">
  <strong>Herramienta Interactiva para la Resolución de Problemas de Biofísica</strong><br>
  <em>Versión 1.0.0</em>
</p>

<p align="center">
  <a href="#-descripción">Descripción</a> •
  <a href="#-módulos">Módulos</a> •
  <a href="#-instalación">Instalación</a> •
  <a href="#-uso">Uso</a> •
  <a href="#-arquitectura">Arquitectura</a>
</p>

---

## 📋 Descripción

El **Entorno Virtual de Biofísica (BIA)** es una aplicación de escritorio desarrollada en Python que proporciona una plataforma integrada para el estudio de la Biofísica. Diseñada específicamente para estudiantes de Bioquímica, la herramienta combina:

- **Contenido teórico organizado** (conferencias digitales)
- **Bibliografía de referencia** (libros y artículos científicos)
- **Problemas propuestos con soluciones** (banco de ejercicios)
- **Seminarios del curso** (ejercicios prácticos en PDF)
- **Calculadoras interactivas** con retroalimentación inmediata

### Motivación

La Biofísica es una disciplina que requiere la integración de conceptos físicos, químicos y biológicos. Su aprendizaje frecuentemente se dificulta por:

- La abstracción de los fenómenos estudiados
- La necesidad de aplicar modelos matemáticos complejos
- La dificultad para visualizar procesos a escala celular

Este entorno virtual aborda estas dificultades mediante algoritmos que calculan y explican paso a paso los fenómenos biofísicos, proporcionando retroalimentación educativa inmediata.

---

## 🧬 Módulos Principales

La aplicación está organizada en **seis módulos** accesibles desde la barra lateral:

### 1. 🏠 Inicio
Pantalla de bienvenida con acceso rápido a los módulos principales y descripción general de la herramienta.

### 2. 📖 Conferencias Digitales
Repositorio organizado de contenido teórico del curso, estructurado en **7 temas**:

| Tema | Contenido |
|------|-----------|
| Tema 1 | Difusión y Ósmosis |
| Tema 2 | Equilibrio Iónico Celular |
| Tema 3 | Transporte Mediado |
| Tema 4 | Canales Iónicos y Patch Clamp |
| Tema 5 | Excitabilidad |
| Tema 6 | Movimiento Mecánico Celular |
| Tema 7 | Procesos Fotobiológicos |

Cada tema contiene conferencias en formato PDF con acceso directo desde la aplicación.

### 3. 📚 Bibliografía Recomendada
Sección dividida en dos pestañas:

- **📕 Libros**: 10 libros de referencia incluyendo Blaustein, Kandel, Sperelakis, entre otros
- **📄 Artículos**: Artículos científicos relevantes con acceso a PDFs locales

Cada entrada muestra autor, año, editorial y permite abrir el PDF directamente.

### 4. 📝 Problemas y Seminarios
Módulo dividido en dos pestañas:

- **📋 Problemas**: Banco de ejercicios organizados por categoría y dificultad
  - Filtros por categoría (ósmosis, patch clamp)
  - Filtros por dificultad (1-5 estrellas)
  - Panel de detalle con enunciado, datos y solución paso a paso
  
- **📚 Seminarios**: 4 seminarios del curso en PDF
  - Seminario 1: Difusión y Ósmosis
  - Seminario 2: Equilibrio Iónico
  - Seminario 3: Canales Iónicos y Patch Clamp
  - Seminario 4: Excitabilidad

### 5. 💧 Módulo Interactivo de Ósmosis
Calculadora interactiva para análisis osmótico que incluye:

#### Comparación de Osmolaridades
- Ingreso de múltiples solutos para medio intracelular y extracelular
- Solutos predefinidos: NaCl, KCl, CaCl₂, MgCl₂, Glucosa, Urea, Sacarosa, Manitol
- Soporte para solutos penetrantes y no penetrantes

**Resultados generados:**

| Parámetro | Descripción |
|-----------|-------------|
| Osmolaridad intracelular | Suma de contribuciones osmóticas internas (mOsm/L) |
| Osmolaridad extracelular | Suma de contribuciones osmóticas externas (mOsm/L) |
| Osmolaridad efectiva | Solo solutos no penetrantes (determina tonicidad) |
| Clasificación osmótica | Isosmótica / Hiperosmótica / Hiposmótica |
| Clasificación tónica | Isotónica / Hipertónica / Hipotónica |
| Respuesta celular | Equilibrio / Hinchazón / Disecación / Lisis |
| Cambio de volumen | Porcentaje respecto al volumen inicial |

**Gráficos generados:**
- Comparación de barras de osmolaridades
- Dinámica de volumen celular en el tiempo (modelo Boyle-van't Hoff)
- Indicación de umbrales de lisis celular

### 6. ⚖️ Módulo de Equilibrio Iónico
Calculadora para potenciales de equilibrio iónico:

#### Ecuación de Nernst

$$E_{ion} = \frac{RT}{zF} \ln\left(\frac{[Ion]_{ext}}{[Ion]_{int}}\right)$$

**Iones predefinidos con concentraciones fisiológicas:**

| Ion | [Intracelular] mM | [Extracelular] mM | Valencia |
|-----|-------------------|-------------------|----------|
| K⁺ | 140 | 5 | +1 |
| Na⁺ | 12 | 145 | +1 |
| Cl⁻ | 4 | 110 | -1 |
| Ca²⁺ | 0.0001 | 2 | +2 |
| H⁺ | 0.0001 | 0.00004 | +1 |
| Mg²⁺ | 0.5 | 1.5 | +2 |
| HCO₃⁻ | 10 | 24 | -1 |

**Resultados:**
- Potencial de equilibrio en mV
- Interpretación fisiológica del resultado
- Gráfico de barras comparativo entre iones

### 7. ⚡ Módulo de Patch Clamp
Herramientas para análisis electrofisiológico:

#### Curvas I-V (Corriente-Voltaje)
- Generación de curvas teóricas a partir de conductancia y potencial de reversión
- Análisis de datos experimentales con ajuste lineal
- Cálculo de conductancia (nS) y potencial de reversión (mV)

#### Registro de Canal Único
- Análisis de registros de corriente
- Cálculo de conductancia de canal único
- Probabilidad de apertura

**Gráficos interactivos:**
- Curva I-V con línea de regresión
- Identificación del potencial de reversión
- Paneles redimensionables con barras de desplazamiento

---

## 🏗️ Arquitectura del Sistema

La aplicación implementa una **arquitectura hexagonal** (Ports & Adapters) que garantiza:

- **Separación de responsabilidades**: Lógica de negocio independiente de la interfaz
- **Testabilidad**: Componentes aislados que pueden probarse unitariamente
- **Extensibilidad**: Nuevos módulos sin modificar el núcleo existente
- **Portabilidad**: El core puede reutilizarse para versión web futura

```
┌─────────────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN                         │
│              CustomTkinter Desktop GUI                          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │ Sidebar │ │  Views  │ │  Forms  │ │ Panels  │ │ Plots   │   │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                    CAPA DE SERVICIOS                            │
│              SolverService (Orquestador)                        │
├─────────────────────────────────────────────────────────────────┤
│                    CAPA DE DOMINIO                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Solvers Ósmosis │  │ Solvers Nernst  │  │ Solvers Patch   │ │
│  │ - Osmolarity    │  │ - Nernst        │  │ - I-V Curve     │ │
│  │ - Tonicity      │  │ - Goldman       │  │ - SingleChannel │ │
│  │ - Volume        │  │                 │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                  CAPA DE INFRAESTRUCTURA                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ JSON Repository │  │  File Manager   │  │    Config       │ │
│  │ - Conferences   │  │  - PDF Opener   │  │    Loader       │ │
│  │ - Bibliography  │  │  - Path Manager │  │                 │ │
│  │ - Problems      │  │                 │  │                 │ │
│  │ - Seminars      │  │                 │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura del Proyecto

```
biofisica_entorno_virtual/
│
├── src/                              # Código fuente
│   ├── main.py                       # Punto de entrada
│   ├── config.py                     # Configuración global
│   │
│   ├── core/                         # Núcleo de la aplicación
│   │   ├── domain/                   # Modelos de datos
│   │   │   ├── bibliography.py
│   │   │   ├── conference.py
│   │   │   ├── problem.py
│   │   │   └── solver_result.py
│   │   │
│   │   ├── services/                 # Lógica de negocio
│   │   │   └── solver_service.py
│   │   │
│   │   └── solvers/                  # Algoritmos matemáticos
│   │       ├── base_solver.py
│   │       ├── osmosis/
│   │       │   ├── osmolarity.py
│   │       │   ├── osmolarity_comparison.py
│   │       │   ├── tonicity.py
│   │       │   ├── cell_volume.py
│   │       │   └── volume_dynamics.py
│   │       ├── ionic_equilibrium/
│   │       │   └── nernst.py
│   │       └── patch_clamp/
│   │           ├── nernst.py
│   │           ├── goldman.py
│   │           ├── iv_curve.py
│   │           └── single_channel.py
│   │
│   ├── infrastructure/               # Acceso a datos
│   │   ├── json_repository.py        # Repositorios JSON
│   │   └── file_manager.py           # Gestión de archivos
│   │
│   └── desktop/                      # Interfaz gráfica
│       ├── app.py                    # Aplicación principal
│       ├── components/               # Widgets reutilizables
│       │   ├── sidebar.py
│       │   ├── input_form.py
│       │   ├── result_panel.py
│       │   ├── plot_canvas.py
│       │   └── solute_widgets.py
│       └── views/                    # Vistas de cada módulo
│           ├── home_view.py
│           ├── conferences_view.py
│           ├── bibliography_view.py
│           ├── problems_view.py
│           └── interactive/
│               ├── osmosis_view.py
│               ├── osmosis_plotting.py
│               ├── ionic_equilibrium_view.py
│               └── patch_clamp_view.py
│
├── data/                             # Datos de la aplicación
│   ├── config.json                   # Configuración de usuario
│   ├── img/                          # Imágenes y logos
│   ├── conferences/                  # Conferencias digitales
│   │   ├── _index.json
│   │   └── pdfs/
│   │       ├── Tema #1/
│   │       ├── Tema #2/
│   │       └── ...
│   ├── bibliography/                 # Referencias bibliográficas
│   │   ├── index.json
│   │   ├── books.json
│   │   ├── papers.json
│   │   └── pdfs/
│   └── problems/                     # Banco de ejercicios
│       ├── osmosis/
│       ├── patch_clamp/
│       └── seminars/
│           ├── _index.json
│           └── *.pdf
│
├── docs/                             # Documentación
│   ├── README.html
│   └── ROADMAP.md
│
├── requirements.txt                  # Dependencias de producción
├── requirements-dev.txt              # Dependencias de desarrollo
├── pyrightconfig.json                # Configuración de tipo
└── README.md                         # Este archivo
```

---

## 🛠️ Instalación y Configuración

### Requisitos Previos

- **Python 3.10+** (probado con Python 3.11, 3.12)
- **pip** (gestor de paquetes)
- **Git** (opcional)

### Paso 1: Obtener el Proyecto

```bash
# Clonar repositorio
git clone https://github.com/sebagonz106/biophysics-virtual-environment.git
cd biofisica_entorno_virtual

# O descargar y extraer el ZIP
```

### Paso 2: Crear Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activar (Windows CMD)
.\venv\Scripts\activate.bat

# Activar (Linux/macOS)
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Ejecutar la Aplicación

```bash
python -m src.main
```

---

## 📦 Dependencias

### Producción

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| `customtkinter` | ≥5.2.0 | Interfaz gráfica moderna |
| `pillow` | ≥10.0.0 | Procesamiento de imágenes |
| `numpy` | ≥1.24.0 | Computación numérica |
| `scipy` | ≥1.11.0 | Funciones científicas |
| `matplotlib` | ≥3.7.0 | Generación de gráficos |
| `pydantic` | ≥2.0.0 | Validación de datos |

### Desarrollo

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| `pytest` | ≥7.0.0 | Framework de pruebas |
| `pyinstaller` | ≥6.0.0 | Empaquetado ejecutable |

---

## 📖 Guía de Uso

### Navegación General
1. Use la **barra lateral izquierda** para acceder a los módulos
2. El módulo activo se resalta visualmente
3. El área central muestra el contenido del módulo seleccionado

### Módulos Interactivos
1. Seleccione el módulo deseado (Ósmosis, Equilibrio Iónico o Patch Clamp)
2. Complete los campos del formulario con los datos del problema
3. Pulse **"Calcular"** para obtener resultados
4. Analice la **interpretación** y **retroalimentación** generada
5. Los paneles son **redimensionables** arrastrando los separadores

### Abrir PDFs
- En Conferencias, Bibliografía o Seminarios, haga clic en **"Abrir"** o **"Abrir PDF"**
- El archivo se abrirá con el visor de PDF predeterminado del sistema

### Añadir Contenido
- **Conferencias**: Añada PDFs a `data/conferences/pdfs/Tema #X/` y actualice `_index.json`
- **Bibliografía**: Edite `data/bibliography/index.json` y añada PDFs a `pdfs/`
- **Seminarios**: Añada PDFs a `data/problems/seminars/` y actualice `_index.json`

---

## 🚀 Distribución como Ejecutable

```bash
# Instalar PyInstaller
pip install pyinstaller

# Generar ejecutable
pyinstaller --onefile --windowed --icon=data/img/bia_icon.ico --name="BiofisicaApp" src/main.py
```

El ejecutable se genera en `dist/`. Incluya la carpeta `data/` junto al ejecutable.

---

## 🔮 Desarrollo Futuro

- [ ] Módulo de Goldman-Hodgkin-Katz completo
- [ ] Exportación de resultados a PDF
- [ ] Sistema de progreso del estudiante
- [ ] Modo claro/oscuro configurable
- [ ] Migración a versión web (FastAPI + React)
- [ ] Módulo de cinética enzimática
- [ ] Soporte multiidioma

---

## 👥 Autores

- **Ana Gabriela Zaragoza Palmarola** - anagabrielazaragozapalmarola@gmail.com
- **Sebastián González** - sebagonz106@gmail.com

---

## 📄 Licencia

Proyecto desarrollado con fines educativos para la enseñanza de la Biofísica en la carrera de Bioquímica. Consulte con los autores antes de cualquier uso comercial.

---

<p align="center">
  <em>Universidad de La Habana — Facultad de Biología</em><br>
  <em>Recurso educativo complementario para la asignatura de Biofísica</em>
</p>
