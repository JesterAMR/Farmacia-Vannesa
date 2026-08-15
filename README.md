# Sistema de Farmacia Vannesa

El **Sistema de Farmacia Vannesa** es una aplicación web robusta y segura para la gestión integral de una farmacia. Está construida utilizando **Python** y **Flask**, empleando una arquitectura por capas basada en los **principios SOLID** para asegurar un código mantenible, escalable y limpio. Utiliza **SQLite** como base de datos local.

## Características Principales

1. **Autenticación y Seguridad**:

   * Gestión de inicio de sesión seguro.
   * Hasheo de contraseñas utilizando Werkzeug para proteger el acceso a los módulos principales.
2. **Gestión de Inventario**:

   * Control completo de productos (creación, lectura, actualización y eliminación).
   * **Análisis de bajo rendimiento**: Identificación visual de productos con bajas ventas para poder tomar decisiones comerciales.
   * **Corte de inventario mensual**: Funcionalidad para realizar la conciliación formal del inventario a fin de mes.
   * **Reposición de inventario**: Mecanismos para monitorizar el nivel de stock y sugerir productos para ser reabastecidos.
3. **Módulo de Ventas**:

   * Registro y procesamiento de ventas de productos.
   * Actualización del inventario en tiempo real al finalizar una transacción.
4. **Dashboard / Tablero Principal**:

   * Resumen visual y estadísticas clave sobre el rendimiento general de la farmacia, ventas recientes y alertas de stock.

## Arquitectura del Proyecto

El sistema está organizado en un diseño modular con distintas capas, siguiendo prácticas de Arquitectura Limpia y Diseño Guiado por el Dominio (DDD - Domain-Driven Design):

* **`app/domain/`**: Modelos de datos principales (Producto, Usuario, Venta).
* **`app/application/`**: Reglas de negocio y servicios (AuthService, InventoryService, SalesService, DashboardService).
* **`app/infrastructure/`**: Persistencia y acceso a base de datos (SQLiteDatabase, Repositorios).
* **`app/presentation/`**: Interfaces de usuario y controladores (Flask Blueprints, Rutas, Templates de HTML, CSS "Vanilla").

## Requisitos

* **Python** 3.8 o superior.
* Módulos requeridos especificados en `requirements.txt` (por ejemplo, `Flask==3.0.0`).

## Instalación y Configuración

1. **Clonar o descargar el repositorio**.
2. **Crear y activar un entorno virtual**:

```bash
   python -m venv venv
   
   # En Windows:
   venv\\Scripts\\activate
   # En Linux/macOS:
   source venv/bin/activate
   ```

3. **Instalar las dependencias**:

```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación**:

```bash
   # Dentro de la carpeta raíz del proyecto
   python -m app.main
   # O el método alternativo configurando FLASK\_APP
   ```

> El sistema creará automáticamente la base de datos `vannesa\_db.sqlite` e inicializará las tablas requeridas.

5. **Acceder a la aplicación**:
Abre el navegador web y dirígete a `http://localhost:5000`.

## Consideraciones de Diseño UI

El diseño de las vistas (templates) ha sido desarrollado usando **HTML** y estilizado completamente con **CSS Vanilla**, asegurando una experiencia responsiva, estética, rápida e independiente de marcos CSS adicionales garantizando una personalización única.

