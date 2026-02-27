# 📄 DocFlow AI - Intelligent OCR & ERP Sync

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-lightgrey.svg)
![MariaDB](https://img.shields.io/badge/MariaDB-Database-blue.svg)
![Architecture](https://img.shields.io/badge/Architecture-Clean%20%26%20Modular-success.svg)

DocFlow AI es una plataforma web orientada al procesamiento inteligente de documentos (facturas, albaranes, presupuestos) mediante Inteligencia Artificial. 

Su principal fortaleza es su **arquitectura agnóstica**: está diseñada utilizando el **Patrón Estrategia (Strategy Pattern)**, lo que permite intercambiar motores de IA (OpenAI, Gemini), reglas de validación y conectores de ERP (Odoo, SAP) sin modificar el núcleo de la aplicación.



[Image of OCR document processing flow diagram]


## 🚀 Características Principales

* 🧠 **IA Agnóstica:** Abstracción completa del motor de IA. Soporta múltiples proveedores de LLM/VLM para extracción de datos (OCR inteligente).
* 🏗️ **Validación Modular:** Reglas matemáticas y de negocio aisladas por tipo de documento (cuadre de impuestos en facturas, validación de líneas en albaranes).
* 🔄 **Sincronización Universal:** Módulos conectables para exportar los documentos validados a cualquier ERP central.
* ✏️ **Revisión Humana Reactiva:** Interfaz de usuario dinámica que permite editar cabeceras, recalcular totales en tiempo real y añadir líneas manualmente antes de la exportación final.
* 🔒 **Seguridad y Autenticación:** Gestión de usuarios, sesiones y protección de rutas.

## 🛠 Stack Tecnológico

* **Backend:** Python, Flask, Application Factory pattern.
* **Base de Datos:** MariaDB, SQLAlchemy (ORM), Flask-Migrate (Alembic).
* **Frontend:** Jinja2 (Templates), Bootstrap 5 / Tailwind, Alpine.js / HTMX (Interactividad).
* **Librerías Clave:** `openai`, `google-generativeai`, `pdf2image`, `requests`.

## 📂 Estructura del Proyecto (Clean Architecture)

El proyecto separa estrictamente las rutas web de la lógica de negocio externa:

```text
/app
 ├── /blueprints       # Rutas web (Controladores)
 ├── /models           # Modelos de base de datos (SQLAlchemy)
 ├── /services         # LÓGICA DE NEGOCIO Y ABSTRACCIONES
 │   ├── /ai_provider  # Interfaces y conectores de IA (OpenAI, Gemini...)
 │   ├── /erp_provider # Interfaces y conectores de ERP (Odoo, SAP...)
 │   └── /validators   # Reglas de negocio (Facturas, Presupuestos...)
 ├── /templates        # Vistas HTML (Jinja2)
 └── /utils            # Herramientas (Procesamiento de PDF a Imagen, etc.)
