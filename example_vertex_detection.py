#!/usr/bin/env python3
"""
Exemple d'ús del Detector de Vèrtexs d'Espais Aeris

Aquest script mostra com utilitzar el detector per trobar vèrtexs
de polígons d'espais aeris en cartes VFR.
"""

from airspace_vertex_detector import AirspaceVertexDetector
import os

def detect_vertices_from_preprocessed_folder(folder_path):
    """
    Detecta vèrtexs utilitzant una carpeta de preprocessament existent.
    
    Args:
        folder_path (str): Camí a la carpeta de preprocessament
    """
    print(f"🔍 Utilitzant carpeta de preprocessament: {folder_path}")
    
    try:
        # Inicialitzar detector amb carpeta preprocessada
        detector = AirspaceVertexDetector(preprocessed_folder=folder_path)
        
        # Detectar àrees d'espais aeris
        detector.detect_airspace_areas()
        
        # Extreure vèrtexs
        detector.extract_polygon_vertices()
        
        # Visualitzar i desar resultats
        detector.visualize_polygons("detected_polygons.png")
        detector.save_vertex_data("airspace_vertices.json")
        detector.export_vertices_csv("airspace_vertices.csv")
        
        # Mostrar estadístiques
        detector.print_statistics()
        
        return detector
        
    except Exception as e:
        print(f"❌ Error processant carpeta preprocessada: {e}")
        return None

def detect_vertices_from_image(image_path):
    """
    Detecta vèrtexs directament des d'una imatge.
    
    Args:
        image_path (str): Camí a la imatge VFR
    """
    print(f"🔍 Processant imatge directament: {image_path}")
    
    try:
        # Inicialitzar detector amb imatge
        detector = AirspaceVertexDetector(image_path=image_path)
        
        # Definir rangs de color personalitzats
        custom_color_ranges = {
            "restricted_airspace": ([0, 50, 50], [10, 255, 255]),      # Vermell
            "controlled_airspace": ([100, 50, 50], [130, 255, 255]),   # Blau
            "uncontrolled_airspace": ([40, 50, 50], [80, 255, 255]),   # Verd
            "danger_areas": ([20, 50, 50], [40, 255, 255]),            # Groc/Taronja
            "prohibited_areas": ([160, 50, 50], [180, 255, 255])       # Magenta
        }
        
        # Detectar àrees d'espais aeris
        detector.detect_airspace_areas(custom_color_ranges)
        
        # Extreure vèrtexs amb paràmetres personalitzats
        detector.extract_polygon_vertices(epsilon_factor=0.01, min_vertices=4)
        
        # Visualitzar i desar resultats
        detector.visualize_polygons("detected_polygons_direct.png")
        detector.save_vertex_data("airspace_vertices_direct.json")
        detector.export_vertices_csv("airspace_vertices_direct.csv")
        
        # Mostrar estadístiques
        detector.print_statistics()
        
        return detector
        
    except Exception as e:
        print(f"❌ Error processant imatge: {e}")
        return None

def main():
    """Funció principal per executar l'exemple."""
    print("🛩️  EXEMPLE DE DETECCIÓ DE VÈRTEXS D'ESPAIS AERIS")
    print("=" * 60)
    
    # Buscar carpetes de preprocessament existents
    preprocessing_folders = []
    for item in os.listdir("."):
        if os.path.isdir(item) and item.startswith("preprocessing_steps_"):
            preprocessing_folders.append(item)
    
    # Buscar imatges VFR disponibles
    vfr_images = []
    for img in ["VFR-BORDEAUX.png", "VFR-TOULOUSE.png"]:
        if os.path.exists(img):
            vfr_images.append(img)
    
    print(f"\n📁 Carpetes de preprocessament trobades: {len(preprocessing_folders)}")
    for folder in preprocessing_folders:
        print(f"   - {folder}")
    
    print(f"\n🖼️  Imatges VFR disponibles: {len(vfr_images)}")
    for img in vfr_images:
        print(f"   - {img}")
    
    # Opció 1: Utilitzar carpeta de preprocessament si existeix
    if preprocessing_folders:
        print(f"\n🔧 Opció 1: Utilitzant carpeta de preprocessament més recent...")
        latest_folder = sorted(preprocessing_folders)[-1]
        detector = detect_vertices_from_preprocessed_folder(latest_folder)
        
        if detector:
            print("✅ Detecció completada utilitzant dades preprocessades!")
    
    # Opció 2: Processar imatge directament
    if vfr_images:
        print(f"\n🔧 Opció 2: Processant imatge directament...")
        detector = detect_vertices_from_image(vfr_images[0])
        
        if detector:
            print("✅ Detecció completada processant imatge directament!")
    
    if not preprocessing_folders and not vfr_images:
        print("\n⚠️  No s'han trobat carpetes de preprocessament ni imatges VFR.")
        print("   Assegura't que tens:")
        print("   - Una imatge VFR (VFR-BORDEAUX.png o VFR-TOULOUSE.png)")
        print("   - O una carpeta de preprocessament (preprocessing_steps_*)")
    
    print("\n📋 ARXIUS GENERATS:")
    print("   - detected_polygons.png: Visualització dels polígons detectats")
    print("   - airspace_vertices.json: Dades dels vèrtexs en format JSON")
    print("   - airspace_vertices.csv: Coordenades dels vèrtexs en format CSV")

if __name__ == "__main__":
    main()
