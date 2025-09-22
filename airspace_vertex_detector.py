#!/usr/bin/env python3
"""
Detector de Vèrtexs d'Espais Aeris amb OpenCV AI

Aquest script utilitza OpenCV per detectar i extreure els vèrtexs dels polígons
d'espais aeris en cartes VFR després del preprocessament.
"""

import cv2
import numpy as np
import json
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
from chart_preprocessing import ChartPreprocessor

class AirspaceVertexDetector:
    def __init__(self, preprocessed_folder=None, image_path=None):
        """
        Inicialitza el detector de vèrtexs d'espais aeris.
        
        Args:
            preprocessed_folder (str): Carpeta amb resultats de preprocessament
            image_path (str): Camí a la imatge original (si no es proporciona carpeta)
        """
        self.preprocessed_folder = Path(preprocessed_folder) if preprocessed_folder else None
        self.image_path = image_path
        self.original_image = None
        self.airspace_polygons = {}
        self.vertex_data = {}
        
        if preprocessed_folder:
            self._load_preprocessed_data()
        elif image_path:
            self._load_original_image()
    
    def _load_preprocessed_data(self):
        """Carrega dades preprocessades des de la carpeta especificada."""
        if not self.preprocessed_folder.exists():
            raise FileNotFoundError(f"Carpeta de preprocessament no trobada: {self.preprocessed_folder}")
        
        # Carregar imatge original
        original_path = self.preprocessed_folder / "01_original" / "original.png"
        if original_path.exists():
            self.original_image = cv2.imread(str(original_path))
        else:
            raise FileNotFoundError("Imatge original no trobada en la carpeta de preprocessament")
        
        print(f"✓ Dades preprocessades carregades des de: {self.preprocessed_folder}")
    
    def _load_original_image(self):
        """Carrega imatge original directament."""
        if not Path(self.image_path).exists():
            raise FileNotFoundError(f"Imatge no trobada: {self.image_path}")
        
        self.original_image = cv2.imread(self.image_path)
        if self.original_image is None:
            raise ValueError(f"No es pot carregar la imatge: {self.image_path}")
        
        print(f"✓ Imatge original carregada: {self.image_path}")
    
    def detect_airspace_areas(self, color_ranges=None):
        """
        Detecta àrees d'espais aeris basant-se en colors.
        
        Args:
            color_ranges (dict): Diccionari amb rangs de color HSV per cada tipus d'espai aeri
        """
        if color_ranges is None:
            # Rangs de color per defecte per a espais aeris
            color_ranges = {
                "restricted_airspace": ([0, 50, 50], [10, 255, 255]),      # Vermell
                "controlled_airspace": ([100, 50, 50], [130, 255, 255]),   # Blau
                "uncontrolled_airspace": ([40, 50, 50], [80, 255, 255]),   # Verd
                "danger_areas": ([20, 50, 50], [40, 255, 255]),            # Groc/Taronja
                "prohibited_areas": ([160, 50, 50], [180, 255, 255])       # Magenta
            }
        
        # Convertir a HSV
        hsv_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2HSV)
        
        self.airspace_polygons = {}
        
        for airspace_type, (lower, upper) in color_ranges.items():
            print(f"\n🔍 Detectant {airspace_type}...")
            
            # Crear màscara per al color
            mask = cv2.inRange(hsv_image, np.array(lower), np.array(upper))
            
            # Aplicar operacions morfològiques per netejar la màscara
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            # Trobar contorns
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filtrar contorns per àrea mínima
            min_area = 1000  # Àrea mínima en píxels
            filtered_contours = [c for c in contours if cv2.contourArea(c) > min_area]
            
            if filtered_contours:
                print(f"   ✓ Trobats {len(filtered_contours)} contorns per a {airspace_type}")
                self.airspace_polygons[airspace_type] = filtered_contours
            else:
                print(f"   ⚠ No s'han trobat contorns per a {airspace_type}")
                self.airspace_polygons[airspace_type] = []
    
    def extract_polygon_vertices(self, epsilon_factor=0.02, min_vertices=3):
        """
        Extreu vèrtexs dels polígons d'espais aeris.
        
        Args:
            epsilon_factor (float): Factor per a l'aproximació de Douglas-Peucker
            min_vertices (int): Nombre mínim de vèrtexs per considerar un polígon vàlid
        """
        print("\n📐 Extraient vèrtexs dels polígons...")
        
        self.vertex_data = {}
        
        for airspace_type, contours in self.airspace_polygons.items():
            if not contours:
                continue
            
            print(f"\n🔍 Processant {airspace_type}:")
            polygons = []
            
            for i, contour in enumerate(contours):
                # Aproximar contorn com a polígon
                epsilon = epsilon_factor * cv2.arcLength(contour, True)
                approx_polygon = cv2.approxPolyDP(contour, epsilon, True)
                
                # Verificar que tingui suficients vèrtexs
                if len(approx_polygon) >= min_vertices:
                    # Convertir a llista de coordenades (x, y)
                    vertices = [(int(point[0][0]), int(point[0][1])) for point in approx_polygon]
                    
                    # Calcular propietats del polígon
                    area = cv2.contourArea(contour)
                    perimeter = cv2.arcLength(contour, True)
                    bounding_rect = cv2.boundingRect(contour)
                    
                    polygon_data = {
                        "id": i + 1,
                        "vertices": vertices,
                        "num_vertices": len(vertices),
                        "area": float(area),
                        "perimeter": float(perimeter),
                        "bounding_box": {
                            "x": int(bounding_rect[0]),
                            "y": int(bounding_rect[1]),
                            "width": int(bounding_rect[2]),
                            "height": int(bounding_rect[3])
                        },
                        "centroid": self._calculate_centroid(vertices)
                    }
                    
                    polygons.append(polygon_data)
                    print(f"   ✓ Polígon {i+1}: {len(vertices)} vèrtexs, àrea: {area:.0f} px²")
            
            self.vertex_data[airspace_type] = polygons
            print(f"   📊 Total polígons detectats per a {airspace_type}: {len(polygons)}")
    
    def _calculate_centroid(self, vertices):
        """Calcula el centroide d'un polígon."""
        if not vertices:
            return (0, 0)
        
        x_coords = [v[0] for v in vertices]
        y_coords = [v[1] for v in vertices]
        
        centroid_x = sum(x_coords) / len(x_coords)
        centroid_y = sum(y_coords) / len(y_coords)
        
        return (float(centroid_x), float(centroid_y))
    
    def visualize_polygons(self, output_path="airspace_polygons_visualization.png"):
        """
        Crea una visualització dels polígons detectats.
        
        Args:
            output_path (str): Camí per desar la visualització
        """
        if self.original_image is None:
            print("⚠ No hi ha imatge per visualitzar")
            return
        
        # Crear còpia de la imatge original
        vis_image = self.original_image.copy()
        
        # Colors per a cada tipus d'espai aeri
        colors = {
            "restricted_airspace": (0, 0, 255),      # Vermell
            "controlled_airspace": (255, 0, 0),      # Blau
            "uncontrolled_airspace": (0, 255, 0),    # Verd
            "danger_areas": (0, 255, 255),           # Groc
            "prohibited_areas": (255, 0, 255)        # Magenta
        }
        
        for airspace_type, polygons in self.vertex_data.items():
            color = colors.get(airspace_type, (128, 128, 128))
            
            for polygon in polygons:
                vertices = np.array(polygon["vertices"], np.int32)
                
                # Dibuixar polígon
                cv2.polylines(vis_image, [vertices], True, color, 2)
                
                # Dibuixar vèrtexs
                for vertex in vertices:
                    cv2.circle(vis_image, tuple(vertex), 4, color, -1)
                
                # Dibuixar centroide
                centroid = polygon["centroid"]
                cv2.circle(vis_image, (int(centroid[0]), int(centroid[1])), 6, color, -1)
                
                # Dibuixar ID del polígon
                cv2.putText(vis_image, f"{airspace_type}_{polygon['id']}", 
                           (int(centroid[0]) + 10, int(centroid[1]) - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # Desar visualització
        cv2.imwrite(output_path, vis_image)
        print(f"✓ Visualització desada: {output_path}")
        
        return vis_image
    
    def save_vertex_data(self, output_path="airspace_vertices.json"):
        """
        Desa les dades dels vèrtexs en format JSON.
        
        Args:
            output_path (str): Camí per desar les dades
        """
        # Preparar dades per a JSON
        json_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "image_path": str(self.image_path) if self.image_path else "preprocessed",
                "total_airspace_types": len(self.vertex_data),
                "total_polygons": sum(len(polygons) for polygons in self.vertex_data.values())
            },
            "airspace_polygons": self.vertex_data
        }
        
        # Desa en fitxer JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Dades dels vèrtexs desades: {output_path}")
    
    def save_vertex_coordinates(self, output_path="vertex_coordinates.txt"):
        """
        Desa només les coordenades dels vèrtexs en format llegible.
        
        Args:
            output_path (str): Camí per desar les coordenades
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("COORDENADES DELS VÈRTEXS D'ESPAIS AERIS\n")
            f.write("=" * 50 + "\n\n")
            
            for airspace_type, polygons in self.vertex_data.items():
                if not polygons:
                    continue
                
                f.write(f"TIPUS D'ESPAI AERI: {airspace_type.upper()}\n")
                f.write("-" * 40 + "\n")
                
                for polygon in polygons:
                    f.write(f"\nPolígon ID: {polygon['id']}\n")
                    f.write(f"Nombre de vèrtexs: {polygon['num_vertices']}\n")
                    f.write(f"Àrea: {polygon['area']:.0f} px²\n")
                    f.write(f"Perímetre: {polygon['perimeter']:.0f} px\n")
                    f.write(f"Centroide: ({polygon['centroid'][0]:.1f}, {polygon['centroid'][1]:.1f})\n")
                    f.write("Coordenades dels vèrtexs:\n")
                    
                    for i, (x, y) in enumerate(polygon['vertices']):
                        f.write(f"  Vèrtex {i+1}: ({x}, {y})\n")
                    
                    f.write("\n")
                
                f.write("\n" + "=" * 50 + "\n\n")
        
        print(f"✓ Coordenades dels vèrtexs desades: {output_path}")
    
    def print_vertex_coordinates(self):
        """
        Imprimeix les coordenades dels vèrtexs a la consola.
        """
        print("\n📍 COORDENADES DELS VÈRTEXS D'ESPAIS AERIS")
        print("=" * 60)
        
        for airspace_type, polygons in self.vertex_data.items():
            if not polygons:
                continue
            
            print(f"\n🔹 {airspace_type.upper()}:")
            print("-" * 40)
            
            for polygon in polygons:
                print(f"\n  Polígon ID: {polygon['id']}")
                print(f"  Vèrtexs: {polygon['num_vertices']}")
                print(f"  Àrea: {polygon['area']:.0f} px²")
                print(f"  Centroide: ({polygon['centroid'][0]:.1f}, {polygon['centroid'][1]:.1f})")
                print("  Coordenades:")
                
                for i, (x, y) in enumerate(polygon['vertices']):
                    print(f"    Vèrtex {i+1}: ({x}, {y})")
    
    def get_vertex_coordinates_list(self):
        """
        Retorna una llista simple de totes les coordenades dels vèrtexs.
        
        Returns:
            list: Llista de tuples (airspace_type, polygon_id, vertex_index, x, y)
        """
        coordinates_list = []
        
        for airspace_type, polygons in self.vertex_data.items():
            for polygon in polygons:
                for i, (x, y) in enumerate(polygon['vertices']):
                    coordinates_list.append((airspace_type, polygon['id'], i+1, x, y))
        
        return coordinates_list
    
    def export_vertices_csv(self, output_path="airspace_vertices.csv"):
        """
        Exporta les coordenades dels vèrtexs en format CSV.
        
        Args:
            output_path (str): Camí per desar el fitxer CSV
        """
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Escriure capçalera
            writer.writerow(['Airspace_Type', 'Polygon_ID', 'Vertex_Index', 'X', 'Y', 'Area', 'Perimeter'])
            
            # Escriure dades
            for airspace_type, polygons in self.vertex_data.items():
                for polygon in polygons:
                    for i, (x, y) in enumerate(polygon['vertices']):
                        writer.writerow([
                            airspace_type,
                            polygon['id'],
                            i + 1,
                            x,
                            y,
                            polygon['area'],
                            polygon['perimeter']
                        ])
        
        print(f"✓ Coordenades exportades a CSV: {output_path}")
    
    def get_polygon_statistics(self):
        """Retorna estadístiques dels polígons detectats."""
        stats = {}
        
        for airspace_type, polygons in self.vertex_data.items():
            if not polygons:
                continue
            
            areas = [p['area'] for p in polygons]
            perimeters = [p['perimeter'] for p in polygons]
            vertex_counts = [p['num_vertices'] for p in polygons]
            
            stats[airspace_type] = {
                "num_polygons": len(polygons),
                "avg_area": np.mean(areas),
                "min_area": np.min(areas),
                "max_area": np.max(areas),
                "avg_perimeter": np.mean(perimeters),
                "avg_vertices": np.mean(vertex_counts),
                "min_vertices": np.min(vertex_counts),
                "max_vertices": np.max(vertex_counts)
            }
        
        return stats
    
    def print_statistics(self):
        """Imprimeix estadístiques dels polígons detectats."""
        stats = self.get_polygon_statistics()
        
        print("\n📊 ESTADÍSTIQUES DELS POLÍGONS DETECTATS")
        print("=" * 50)
        
        for airspace_type, stat in stats.items():
            print(f"\n🔹 {airspace_type.upper()}:")
            print(f"   Polígons: {stat['num_polygons']}")
            print(f"   Àrea mitjana: {stat['avg_area']:.0f} px²")
            print(f"   Àrea (min/max): {stat['min_area']:.0f} / {stat['max_area']:.0f} px²")
            print(f"   Perímetre mitjà: {stat['avg_perimeter']:.0f} px")
            print(f"   Vèrtexs mitjans: {stat['avg_vertices']:.1f}")
            print(f"   Vèrtexs (min/max): {stat['min_vertices']} / {stat['max_vertices']}")


def main():
    """Funció principal per executar el detector de vèrtexs."""
    print("🛩️  DETECTOR DE VÈRTEXS D'ESPAIS AERIS")
    print("=" * 50)
    
    # Configuració
    image_path = "VFR-TOULOUSE.png"  # Canvia aquesta ruta per la teva imatge
    
    try:
        # Inicialitzar detector
        detector = AirspaceVertexDetector(image_path=image_path)
        
        # Definir rangs de color per a espais aeris
        color_ranges = {
            "restricted_airspace": ([0, 50, 50], [10, 255, 255]),      # Vermell
            "controlled_airspace": ([100, 50, 50], [130, 255, 255]),   # Blau
            "uncontrolled_airspace": ([40, 50, 50], [80, 255, 255]),   # Verd
            "danger_areas": ([20, 50, 50], [40, 255, 255]),            # Groc/Taronja
            "prohibited_areas": ([160, 50, 50], [180, 255, 255])       # Magenta
        }
        
        # Detectar àrees d'espais aeris
        detector.detect_airspace_areas(color_ranges)
        
        # Extreure vèrtexs dels polígons
        detector.extract_polygon_vertices()
        
        # Visualitzar resultats
        detector.visualize_polygons()
        
        # Desa dades
        detector.save_vertex_data()
        detector.save_vertex_coordinates()  # Desa coordenades en format llegible
        detector.export_vertices_csv()
        
        # Mostrar coordenades a la consola
        detector.print_vertex_coordinates()
        
        # Mostrar estadístiques
        detector.print_statistics()
        
        print("\n✅ PROCESSAMENT COMPLETAT!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
