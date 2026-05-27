import subprocess
import os

def convertir_stl_a_gcode(ruta_stl, ruta_salida_gcode, ruta_ejecutable_slicer, opciones=None):
    #Convierte un archivo STL a GCODE utilizando el motor de PrusaSlicer, 
    #permitiendo inyectar parámetros de impresión personalizados.
    
    comando = [
        ruta_ejecutable_slicer,
        "--export-gcode",
        ruta_stl,
        "--output", 
        ruta_salida_gcode
    ]

    if opciones:
        for parametro, valor in opciones.items():
            comando.append(f"--{parametro}")
            # SOLO agregamos el valor si no es una cadena vacía
            if valor != "":
                comando.append(str(valor))
                print(f"Iniciando el laminado de: {os.path.basename(ruta_stl)}...")
    print(f"Comando ejecutado: {' '.join(comando)}")

    try:
        resultado = subprocess.run(
            comando, 
            capture_output=True, 
            text=True, 
            check=True
        )
        print("¡Conversión exitosa!")
        print(f"Archivo GCODE guardado en: {ruta_salida_gcode}")
        
    except subprocess.CalledProcessError as e:
        print("Error durante la conversión.")
        print(f"Código de error: {e.returncode}")
        print(f"Salida del error: {e.stderr}")
    except FileNotFoundError:
        print(f"Error: No se encontró el ejecutable del slicer en la ruta: {ruta_ejecutable_slicer}")

# --- Ejemplo de uso ---
if __name__ == "__main__":
    archivo_entrada = "d_thing-body.stl"
    archivo_salida = "d_thing-body.gcode"
    ejecutable_prusa = r"C:\Program Files\Prusa3D\PrusaSlicer\prusa-slicer-console.exe" 
    
    # Aquí defines todas las opciones que quieres sobrescribir
    mis_parametros = {
        # Los anchos de extrusión que preguntaste
        "external-perimeter-extrusion-width": 0.45,
        "perimeter-extrusion-width": 0.45,
        "infill-extrusion-width": 0.45,
        "solid-infill-extrusion-width": 0.45,
        "top-infill-extrusion-width": 0.40,
        "first-layer-extrusion-width": 0.70,
        
        # OTROS PARÁMETROS MUY ÚTILES PARA UNA WEB:
        "layer-height": 0.2,             # Altura de capa general
        "first-layer-height": 0.3,       # Altura de la primera capa
        "fill-density": "15%",           # Densidad de relleno (ojo, lleva %)
        "fill-pattern": "gyroid",        # Patrón de relleno (rectilinear, grid, honeycomb, gyroid...)
        "perimeters": 3,                 # Número de paredes/perímetros
        "top-solid-layers": 4,           # Capas sólidas superiores
        "bottom-solid-layers": 3,        # Capas sólidas inferiores
        "brim-width": 5,                 # Ancho del borde de adherencia (en mm)
        
        # Soportes
        "support-material": "",          # Al dejarlo vacío actúa como un "flag" para activarlo
        "support-material-threshold": 45 # Ángulo para generar soportes
    }
    
    convertir_stl_a_gcode(archivo_entrada, archivo_salida, ejecutable_prusa, opciones=mis_parametros)