# 🗺️ Roadmap de Mejoras y Revisiones

**Entorno Virtual para la Enseñanza de la Biofísica**  
*Última actualización: 28 de noviembre de 2025*

---

## 📊 Estado Actual de la Aplicación

La aplicación está **funcional** en su versión 1.0.0 con los siguientes módulos operativos:

| Módulo | Estado | Observaciones |
|--------|--------|---------------|
| 🏠 Vista de Inicio | ✅ Completo | Navegación y accesos rápidos |
| 📖 Conferencias | ✅ Funcional | Requiere contenido (PDFs) |
| 📚 Bibliografía | ✅ Funcional | Libros y artículos con hover |
| 📝 Problemas | ✅ Funcional | Requiere más ejercicios |
| 💧 Ósmosis | ✅ Completo | 3 calculadoras operativas |
| ⚡ Patch Clamp | ✅ Completo | 3 calculadoras operativas |

---

## 🔴 Prioridad Alta — Correcciones Necesarias

### 1. Validación de Entrada de Datos
**Problema**: Los formularios no validan completamente los datos antes de enviarlos a los solvers.

**Tareas**:
- [ ] Añadir validación de rangos numéricos en `InputForm`
- [ ] Mostrar mensajes de error específicos por campo
- [ ] Prevenir concentraciones negativas o cero
- [ ] Validar que la temperatura esté en rangos fisiológicos

**Archivos afectados**: `src/desktop/components/input_form.py`

---

### 2. Manejo de Errores en Solvers
**Problema**: Algunos errores de cálculo no se capturan correctamente.

**Tareas**:
- [ ] Envolver todos los cálculos en try-except
- [ ] Retornar mensajes de error descriptivos en español
- [ ] Registrar errores en log para debugging

**Archivos afectados**: `src/core/solvers/**/*.py`

---

### 3. Persistencia de Configuración de Usuario
**Problema**: Los cambios de tema o preferencias no se guardan.

**Tareas**:
- [ ] Implementar guardado de preferencias en `data/user_data/`
- [ ] Recordar última vista visitada
- [ ] Guardar historial de cálculos recientes

**Archivos afectados**: `src/infrastructure/file_manager.py`, `src/desktop/app.py`

---

## 🟡 Prioridad Media — Mejoras Funcionales

### 4. Añadir Más Solutos Predefinidos
**Ubicación**: `src/core/solvers/osmosis/osmolarity.py`

**Solutos a añadir**:
- [ ] Manitol (20%, diurético osmótico)
- [ ] NaHCO₃ (bicarbonato)
- [ ] Albúmina (presión oncótica)
- [ ] Lactato de Ringer (composición completa)
- [ ] Dextrosa en diferentes concentraciones

---

### 5. Calculadora de Presión Osmótica (π)
**Estado**: No implementada

**Funcionalidad propuesta**:
- Ecuación de Van't Hoff: π = iMRT
- Comparación con presión oncótica del plasma
- Predicción de flujo de agua

**Archivos a crear**: `src/core/solvers/osmosis/osmotic_pressure.py`

---

### 6. Exportación de Resultados
**Estado**: No implementada

**Funcionalidades propuestas**:
- [ ] Exportar resultados a PDF
- [ ] Exportar gráficos como imágenes (PNG/SVG)
- [ ] Generar reportes con interpretación completa
- [ ] Copiar resultados al portapapeles

**Archivos a crear**: `src/infrastructure/export_manager.py`

---

### 7. Mejoras en Gráficos
**Ubicación**: `src/desktop/components/plot_canvas.py`

**Mejoras propuestas**:
- [ ] Zoom interactivo en gráficos
- [ ] Tooltips al pasar el cursor sobre puntos
- [ ] Opción de guardar gráfico
- [ ] Personalización de colores/estilos
- [ ] Animación de cambio de volumen celular

---

### 8. Calculadora de Canales Rectificadores
**Estado**: Parcialmente implementada en `iv_curve.py`

**Mejoras**:
- [ ] Añadir modelos de rectificación inward/outward a la GUI
- [ ] Comparación visual con canal óhmico
- [ ] Ejemplos de canales Kir, Kv

---

## 🟢 Prioridad Baja — Mejoras de UX/UI

### 9. Modo Oscuro/Claro Dinámico
**Estado**: Solo modo oscuro

**Tareas**:
- [ ] Añadir toggle de tema en sidebar
- [ ] Guardar preferencia de tema
- [ ] Asegurar legibilidad en ambos modos

---

### 10. Internacionalización (i18n)
**Estado**: Solo español

**Tareas**:
- [ ] Extraer strings a archivos de traducción
- [ ] Añadir soporte para inglés
- [ ] Selector de idioma en configuración

---

### 11. Tooltips y Ayuda Contextual
**Estado**: Mínimo

**Tareas**:
- [ ] Añadir tooltips explicativos a todos los campos
- [ ] Crear panel de ayuda con fórmulas
- [ ] Añadir enlaces a recursos externos

---

### 12. Atajos de Teclado
**Estado**: No implementado

**Atajos propuestos**:
- `Ctrl+1-4`: Cambiar entre módulos
- `Ctrl+Enter`: Calcular
- `Ctrl+R`: Resetear formulario
- `Ctrl+E`: Exportar resultados

---

## 📚 Contenido a Añadir

### 13. Banco de Problemas
**Ubicación**: `data/problems/`

**Temas pendientes**:
- [ ] Problemas de transporte activo
- [ ] Ejercicios de potencial de acción completo
- [ ] Casos clínicos de alteraciones electrolíticas
- [ ] Problemas de permeabilidad selectiva

**Formato sugerido por problema**:
```json
{
  "id": "osm_003",
  "title": "Título del problema",
  "topic": "osmosis",
  "difficulty": 1-5,
  "points": 10,
  "statement": "Enunciado completo...",
  "given_data": {"variable": "valor"},
  "solution_steps": ["Paso 1...", "Paso 2..."],
  "answer": "Respuesta final",
  "hints": ["Pista 1", "Pista 2"]
}
```

---

### 14. Conferencias Digitales
**Ubicación**: `data/conferences/`

**Temas sugeridos**:
1. Introducción a la Biofísica
2. Propiedades del agua y soluciones
3. Membranas biológicas
4. Transporte pasivo y activo
5. Potenciales de membrana
6. Potencial de acción
7. Sinapsis y neurotransmisión
8. Técnicas de Patch Clamp

---

### 15. Bibliografía Adicional
**Ubicación**: `data/bibliography/`

**Añadir**:
- [ ] Más artículos seminales (Hodgkin-Huxley originales)
- [ ] Reviews modernos de canales iónicos
- [ ] Libros de problemas resueltos
- [ ] Videos y recursos multimedia (enlaces)

---

## 🔬 Módulos Futuros (Versión 2.0)

### 16. Módulo de Cinética Enzimática
**Funcionalidades propuestas**:
- Ecuación de Michaelis-Menten
- Gráficos de Lineweaver-Burk
- Tipos de inhibición (competitiva, no competitiva, etc.)
- Simulación de reacciones enzimáticas

---

### 17. Módulo de Termodinámica
**Funcionalidades propuestas**:
- Energía libre de Gibbs (ΔG)
- Equilibrio químico
- Acoplamiento energético
- ATP y trabajo celular

---

### 18. Módulo de Biofísica de Radiaciones
**Funcionalidades propuestas**:
- Decaimiento radiactivo
- Dosis y exposición
- Efectos biológicos de la radiación

---

### 19. Sistema de Progreso del Estudiante
**Funcionalidades propuestas**:
- [ ] Registro de problemas resueltos
- [ ] Estadísticas de uso
- [ ] Logros y medallas
- [ ] Modo de práctica con tiempo
- [ ] Comparación con pares (anónima)

---

## 🛠️ Mejoras Técnicas

### 20. Testing Automatizado
**Estado**: No implementado

**Tareas**:
- [ ] Tests unitarios para todos los solvers
- [ ] Tests de integración para la GUI
- [ ] CI/CD con GitHub Actions
- [ ] Cobertura de código > 80%

**Archivos a crear**: `tests/`

---

### 21. Documentación del Código
**Estado**: Docstrings básicos

**Tareas**:
- [ ] Generar documentación con Sphinx
- [ ] Añadir ejemplos de uso en docstrings
- [ ] Crear guía de contribución

---

### 22. Optimización de Rendimiento
**Tareas**:
- [ ] Lazy loading de módulos
- [ ] Caché de cálculos frecuentes
- [ ] Optimizar gráficos grandes

---

### 23. Empaquetado Mejorado
**Estado**: PyInstaller básico

**Tareas**:
- [ ] Crear instalador para Windows (NSIS o Inno Setup)
- [ ] Añadir icono y metadatos de aplicación
- [ ] Crear versión portable sin instalación
- [ ] Firmar digitalmente el ejecutable

---

## 🌐 Migración Web (Versión 3.0)

### 24. API REST Backend
**Tecnología propuesta**: FastAPI

**Endpoints**:
- `POST /api/osmosis/osmolarity`
- `POST /api/osmosis/volume`
- `POST /api/patch-clamp/nernst`
- `POST /api/patch-clamp/goldman`
- `POST /api/patch-clamp/iv-curve`

---

### 25. Frontend Web
**Tecnología propuesta**: React + TypeScript + Tailwind

**Ventajas**:
- Acceso desde cualquier dispositivo
- No requiere instalación
- Actualizaciones automáticas
- Posibilidad de modo colaborativo

---

## ✅ Checklist de Revisión Pre-Release

Antes de distribuir una nueva versión, verificar:

- [ ] Todos los solvers retornan resultados correctos
- [ ] La GUI no tiene errores visibles
- [ ] Los PDFs de ejemplo se abren correctamente
- [ ] El empaquetado con PyInstaller funciona
- [ ] El README está actualizado
- [ ] Se han actualizado los números de versión
- [ ] Se ha probado en Windows 10/11
- [ ] Los datos de ejemplo están incluidos

---

## 📝 Notas de Implementación

### Convenciones de Código
- Usar type hints en todas las funciones
- Docstrings en español (formato Google)
- Nombres de variables en inglés
- Mensajes de usuario en español

### Estructura de Commits
```
feat: añadir nueva funcionalidad
fix: corregir error
docs: actualizar documentación
style: cambios de formato
refactor: reestructurar código
test: añadir tests
```

---

## 🤝 Contribución

Para contribuir al proyecto:

1. Fork del repositorio
2. Crear rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -m 'feat: descripción'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

---

*Este documento debe actualizarse conforme se implementen mejoras.*

