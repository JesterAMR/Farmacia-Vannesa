import sqlite3

# 1. Conectar a la base de datos (o crearla en memoria para el ejemplo)
conn = sqlite3.connect('vannesa_db.sqlite')
cursor = conn.cursor()

def obtener_estructura():
    print(f"\n--- Estructura de las tablas ---")
    
    # Opción A: Ver el comando SQL original (Equivalente a .schema)
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
    schemas = cursor.fetchall()
    for schema in schemas:
        print(schema[0] if schema else "Tabla no encontrada.")
    print("Función ejecutada")

obtener_estructura()
input("Presiona Enter para continuar...")