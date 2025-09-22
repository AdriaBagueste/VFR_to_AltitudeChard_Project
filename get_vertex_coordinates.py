#!/usr/bin/env python3
"""
Script Simple per Obtenir Coordenades dels Vèrtexs

Aquest script detecta i imprimeix només les coordenades dels vèrtexs
dels polígons d'espais aeris en format net i llegible.
"""

from airspace_vertex_detector import AirspaceVertexDetector
import os

def get_coordinates_from_image(image_path):
    """
    Obté les coordenades dels vèrtexs des d'una imatge VFR.
    
    Args:
        image_path (str): Camí a la imatge VFR
    """
    print(f"🔍 Processant imatge: {image_path}")
    
    try:
        # Inicialitzar detector
        detector = AirspaceVertexDetector(image_path=image_path)
        
        # Detectar àrees d'espais aeris
        detector.detect_airspace_areas()
        
        # Extreure vèrtexs
        detector.extract_polygon_vertices()
        
        # Imprimir coordenades
        detector.print_vertex_coordinates()
        
        # Desa coordenades en fitxer
        detector.save_vertex_coordinates("vertex_coordinates.txt")
        
        # Retornar llista de coordenades
        coordinates = detector.get_vertex_coordinates_list()
        
        print(f"\n📊 RESUM:")
        print(f"   Total vèrtexs detectats: {len(coordinates)}")
        print(f"   Coordenades desades a: vertex_coordinates.txt")
        
        return coordinates
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def get_coordinates_from_preprocessed(folder_path):
    """
    Obté les coordenades dels vèrtexs des d'una carpeta de preprocessament.
    
    Args:
        folder_path (str): Camí a la carpeta de preprocessament
    """
    print(f"🔍 Utilitzant carpeta preprocessada: {folder_path}")
    
    try:
        # Inicialitzar detector
        detector = AirspaceVertexDetector(preprocessed_folder=folder_path)
        
        # Detectar àrees d'espais aeris
        detector.detect_airspace_areas()
        
        # Extreure vèrtexs
        detector.extract_polygon_vertices()
        
        # Imprimir coordenades
        detector.print_vertex_coordinates()
        
        # Desa coordenades en fitxer
        detector.save_vertex_coordinates("vertex_coordinates.txt")
        
        # Retornar llista de coordenades
        coordinates = detector.get_vertex_coordinates_list()
        
        print(f"\n📊 RESUM:")
        print(f"   Total vèrtexs detectats: {len(coordinates)}")
        print(f"   Coordenades desades a: vertex_coordinates.txt")
        
        return coordinates
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def print_coordinates_simple(coordinates):
    """
    Imprimeix les coordenades en format simple.
    
    Args:
        coordinates (list): Llista de coordenades
    """
    print("\n📍 COORDENADES SIMPLES (x, y):")
    print("=" * 40)
    
    for airspace_type, polygon_id, vertex_index, x, y in coordinates:
        print(f"({x}, {y})  # {airspace_type} - Polígon {polygon_id} - Vèrtex {vertex_index}")

def main():
    """Funció principal."""
    print("📍 OBTENIR COORDENADES DELS VÈRTEXS")
    print("=" * 40)
    
    # Buscar imatges VFR disponibles
    vfr_images = []
    for img in ["VFR-BORDEAUX.png", "VFR-TOULOUSE.png"]:
        if os.path.exists(img):
            vfr_images.append(img)
    
    # Buscar carpetes de preprocessament
    preprocessing_folders = []
    for item in os.listdir("."):
        if os.path.isdir(item) and item.startswith("preprocessing_steps_"):
            preprocessing_folders.append(item)
    
    coordinates = []
    
    # Opció 1: Utilitzar carpeta de preprocessament si existeix
    if preprocessing_folders:
        print(f"\n🔧 Utilitzant carpeta de preprocessament...")
        latest_folder = sorted(preprocessing_folders)[-1]
        coordinates = get_coordinates_from_preprocessed(latest_folder)
    
    # Opció 2: Processar imatge directament
    elif vfr_images:
        print(f"\n🔧 Processant imatge directament...")
        coordinates = get_coordinates_from_image(vfr_images[0])
    
    else:
        print("\n⚠️  No s'han trobat imatges VFR ni carpetes de preprocessament.")
        print("   Assegura't que tens una imatge VFR o executa primer el preprocessament.")
        return
    
    # Mostrar coordenades en format simple
    if coordinates:
        print_coordinates_simple(coordinates)
        
        print(f"\n✅ COORDENADES OBTINGUDES!")
        print(f"   Total: {len(coordinates)} vèrtexs")
        print(f"   Fitxer: vertex_coordinates.txt")
    else:
        print("\n❌ No s'han detectat vèrtexs.")

if __name__ == "__main__":
    main()

