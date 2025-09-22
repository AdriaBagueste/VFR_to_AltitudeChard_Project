#!/usr/bin/env python3
"""
Superposador de Polígons en Imatges Originals

Aquest script superposa els polígons detectats sobre la imatge original
i organitza tots els resultats en carpetes estructurades.
"""

import cv2
import numpy as np
import json
import os
from pathlib import Path
from datetime import datetime
from airspace_vertex_detector import AirspaceVertexDetector

class PolygonSuperimposer:
    def __init__(self, image_path=None, preprocessed_folder=None, output_base_folder="polygon_results"):
        """
        Inicialitza el superposador de polígons.
        
        Args:
            image_path (str): Camí a la imatge original
            preprocessed_folder (str): Carpeta amb resultats de preprocessament
            output_base_folder (str): Carpeta base per als resultats
        """
        self.image_path = image_path
        self.preprocessed_folder = preprocessed_folder
        self.output_base_folder = Path(output_base_folder)
        self.original_image = None
        self.vertex_detector = None
        self.vertex_data = {}
        
        # Crear estructura de carpetes
        self._create_folder_structure()
        
        # Carregar imatge i detectar polígons
        self._load_and_detect()
    
    def _create_folder_structure(self):
        """Crea l'estructura de carpetes per organitzar els resultats."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_name = Path(self.image_path).stem if self.image_path else "unknown"
        
        # Crear carpeta principal amb timestamp
        self.main_folder = self.output_base_folder / f"polygons_{image_name}_{timestamp}"
        
        # Subcarpetes
        self.folders = {
            "original": self.main_folder / "01_original",
            "individual_polygons": self.main_folder / "02_individual_polygons",
            "by_airspace_type": self.main_folder / "03_by_airspace_type",
            "superimposed": self.main_folder / "04_superimposed",
            "coordinates": self.main_folder / "05_coordinates",
            "visualizations": self.main_folder / "06_visualizations",
            "data": self.main_folder / "07_data"
        }
        
        # Crear totes les carpetes
        for folder in self.folders.values():
            folder.mkdir(parents=True, exist_ok=True)
        
        print(f"✓ Estructura de carpetes creada: {self.main_folder}")
    
    def _load_and_detect(self):
        """Carrega la imatge i detecta els polígons."""
        try:
            # Inicialitzar detector de vèrtexs
            if self.preprocessed_folder:
                self.vertex_detector = AirspaceVertexDetector(preprocessed_folder=self.preprocessed_folder)
            elif self.image_path:
                self.vertex_detector = AirspaceVertexDetector(image_path=self.image_path)
            else:
                raise ValueError("Cal proporcionar image_path o preprocessed_folder")
            
            # Carregar imatge original
            self.original_image = self.vertex_detector.original_image
            if self.original_image is None:
                raise ValueError("No s'ha pogut carregar la imatge original")
            
            # Desa imatge original
            cv2.imwrite(str(self.folders["original"] / "original_image.png"), self.original_image)
            
            # Detecta àrees d'espais aeris
            self.vertex_detector.detect_airspace_areas()
            
            # Extreu vèrtexs
            self.vertex_detector.extract_polygon_vertices()
            
            # Obté dades dels vèrtexs
            self.vertex_data = self.vertex_detector.vertex_data
            
            print(f"✓ Imatge carregada i polígons detectats: {len(self.vertex_data)} tipus d'espai aeri")
            
        except Exception as e:
            print(f"❌ Error carregant imatge o detectant polígons: {e}")
            raise
    
    def create_individual_polygon_images(self):
        """Crea imatges individuals per a cada polígon detectat."""
        print("\n🎨 Creant imatges individuals dels polígons...")
        
        colors = {
            "restricted_airspace": (0, 0, 255),      # Vermell
            "controlled_airspace": (255, 0, 0),      # Blau
            "uncontrolled_airspace": (0, 255, 0),    # Verd
            "danger_areas": (0, 255, 255),           # Groc
            "prohibited_areas": (255, 0, 255)        # Magenta
        }
        
        polygon_count = 0
        
        for airspace_type, polygons in self.vertex_data.items():
            if not polygons:
                continue
            
            # Crear carpeta per tipus d'espai aeri
            airspace_folder = self.folders["individual_polygons"] / airspace_type
            airspace_folder.mkdir(exist_ok=True)
            
            color = colors.get(airspace_type, (128, 128, 128))
            
            for polygon in polygons:
                # Crear imatge amb fons transparent
                polygon_image = np.zeros((*self.original_image.shape[:2], 4), dtype=np.uint8)
                
                # Dibuixar polígon
                vertices = np.array(polygon['vertices'], np.int32)
                cv2.fillPoly(polygon_image, [vertices], (*color, 255))
                
                # Dibuixar vèrtexs
                for vertex in vertices:
                    cv2.circle(polygon_image, tuple(vertex), 6, (*color, 255), -1)
                
                # Dibuixar contorn
                cv2.polylines(polygon_image, [vertices], True, (*color, 255), 3)
                
                # Dibuixar ID i informació
                centroid = polygon['centroid']
                cv2.putText(polygon_image, f"ID: {polygon['id']}", 
                           (int(centroid[0]) + 10, int(centroid[1]) - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (*color, 255), 2)
                
                # Desa imatge individual
                filename = f"{airspace_type}_polygon_{polygon['id']:03d}.png"
                cv2.imwrite(str(airspace_folder / filename), polygon_image)
                
                polygon_count += 1
        
        print(f"✓ Creat {polygon_count} imatges individuals dels polígons")
    
    def create_airspace_type_images(self):
        """Crea imatges separades per cada tipus d'espai aeri."""
        print("\n🎨 Creant imatges per tipus d'espai aeri...")
        
        colors = {
            "restricted_airspace": (0, 0, 255),      # Vermell
            "controlled_airspace": (255, 0, 0),      # Blau
            "uncontrolled_airspace": (0, 255, 0),    # Verd
            "danger_areas": (0, 255, 255),           # Groc
            "prohibited_areas": (255, 0, 255)        # Magenta
        }
        
        for airspace_type, polygons in self.vertex_data.items():
            if not polygons:
                continue
            
            # Crear imatge base
            airspace_image = self.original_image.copy()
            color = colors.get(airspace_type, (128, 128, 128))
            
            # Dibuixar tots els polígons d'aquest tipus
            for polygon in polygons:
                vertices = np.array(polygon['vertices'], np.int32)
                
                # Dibuixar polígon omplert amb transparència
                overlay = airspace_image.copy()
                cv2.fillPoly(overlay, [vertices], color)
                cv2.addWeighted(airspace_image, 0.7, overlay, 0.3, 0, airspace_image)
                
                # Dibuixar contorn
                cv2.polylines(airspace_image, [vertices], True, color, 3)
                
                # Dibuixar vèrtexs
                for vertex in vertices:
                    cv2.circle(airspace_image, tuple(vertex), 4, color, -1)
                
                # Dibuixar ID
                centroid = polygon['centroid']
                cv2.putText(airspace_image, f"{polygon['id']}", 
                           (int(centroid[0]) + 10, int(centroid[1]) - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Desa imatge del tipus d'espai aeri
            filename = f"{airspace_type}_all_polygons.png"
            cv2.imwrite(str(self.folders["by_airspace_type"] / filename), airspace_image)
            
            print(f"✓ Creat imatge per {airspace_type}: {len(polygons)} polígons")
    
    def create_superimposed_images(self):
        """Crea imatges amb tots els polígons superposats."""
        print("\n🎨 Creant imatges superposades...")
        
        colors = {
            "restricted_airspace": (0, 0, 255),      # Vermell
            "controlled_airspace": (255, 0, 0),      # Blau
            "uncontrolled_airspace": (0, 255, 0),    # Verd
            "danger_areas": (0, 255, 255),           # Groc
            "prohibited_areas": (255, 0, 255)        # Magenta
        }
        
        # Imatge amb tots els polígons
        all_polygons_image = self.original_image.copy()
        
        # Imatge amb contorns només
        outlines_image = self.original_image.copy()
        
        # Imatge amb vèrtexs només
        vertices_image = self.original_image.copy()
        
        total_polygons = 0
        
        for airspace_type, polygons in self.vertex_data.items():
            if not polygons:
                continue
            
            color = colors.get(airspace_type, (128, 128, 128))
            
            for polygon in polygons:
                vertices = np.array(polygon['vertices'], np.int32)
                
                # Imatge amb tots els polígons (omplerts)
                overlay = all_polygons_image.copy()
                cv2.fillPoly(overlay, [vertices], color)
                cv2.addWeighted(all_polygons_image, 0.8, overlay, 0.2, 0, all_polygons_image)
                cv2.polylines(all_polygons_image, [vertices], True, color, 2)
                
                # Imatge amb contorns només
                cv2.polylines(outlines_image, [vertices], True, color, 3)
                
                # Imatge amb vèrtexs només
                for vertex in vertices:
                    cv2.circle(vertices_image, tuple(vertex), 5, color, -1)
                
                # Dibuixar etiquetes
                centroid = polygon['centroid']
                label = f"{airspace_type}_{polygon['id']}"
                cv2.putText(all_polygons_image, label, 
                           (int(centroid[0]) + 10, int(centroid[1]) - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                
                total_polygons += 1
        
        # Desa imatges superposades
        cv2.imwrite(str(self.folders["superimposed"] / "all_polygons_filled.png"), all_polygons_image)
        cv2.imwrite(str(self.folders["superimposed"] / "all_polygons_outlines.png"), outlines_image)
        cv2.imwrite(str(self.folders["superimposed"] / "all_polygons_vertices.png"), vertices_image)
        
        print(f"✓ Creat imatges superposades: {total_polygons} polígons totals")
    
    def save_coordinate_files(self):
        """Desa fitxers de coordenades en diferents formats."""
        print("\n💾 Desant fitxers de coordenades...")
        
        # JSON complet
        self.vertex_detector.save_vertex_data(str(self.folders["data"] / "vertex_data.json"))
        
        # Coordenades llegibles
        self.vertex_detector.save_vertex_coordinates(str(self.folders["coordinates"] / "vertex_coordinates.txt"))
        
        # CSV
        self.vertex_detector.export_vertices_csv(str(self.folders["coordinates"] / "vertex_coordinates.csv"))
        
        # Coordenades simples per a cada tipus d'espai aeri
        for airspace_type, polygons in self.vertex_data.items():
            if not polygons:
                continue
            
            filename = f"{airspace_type}_coordinates.txt"
            with open(self.folders["coordinates"] / filename, 'w') as f:
                f.write(f"COORDENADES PER A {airspace_type.upper()}\n")
                f.write("=" * 50 + "\n\n")
                
                for polygon in polygons:
                    f.write(f"Polígon {polygon['id']}:\n")
                    for i, (x, y) in enumerate(polygon['vertices']):
                        f.write(f"  Vèrtex {i+1}: ({x}, {y})\n")
                    f.write("\n")
        
        print("✓ Fitxers de coordenades desats")
    
    def create_visualization_summary(self):
        """Crea un resum visual de tots els resultats."""
        print("\n📊 Creant resum visual...")
        
        # Crear imatge de resum
        summary_image = self.original_image.copy()
        
        # Dibuixar llegenda
        legend_y = 30
        colors = {
            "restricted_airspace": (0, 0, 255),      # Vermell
            "controlled_airspace": (255, 0, 0),      # Blau
            "uncontrolled_airspace": (0, 255, 0),    # Verd
            "danger_areas": (0, 255, 255),           # Groc
            "prohibited_areas": (255, 0, 255)        # Magenta
        }
        
        for airspace_type, polygons in self.vertex_data.items():
            if not polygons:
                continue
            
            color = colors.get(airspace_type, (128, 128, 128))
            
            # Dibuixar quadrat de llegenda
            cv2.rectangle(summary_image, (10, legend_y), (30, legend_y + 20), color, -1)
            
            # Dibuixar text de llegenda
            cv2.putText(summary_image, f"{airspace_type}: {len(polygons)} polígons", 
                       (40, legend_y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            legend_y += 30
        
        # Dibuixar polígons
        for airspace_type, polygons in self.vertex_data.items():
            if not polygons:
                continue
            
            color = colors.get(airspace_type, (128, 128, 128))
            
            for polygon in polygons:
                vertices = np.array(polygon['vertices'], np.int32)
                cv2.polylines(summary_image, [vertices], True, color, 2)
                
                # Dibuixar vèrtexs
                for vertex in vertices:
                    cv2.circle(summary_image, tuple(vertex), 3, color, -1)
        
        # Desa resum
        cv2.imwrite(str(self.folders["visualizations"] / "summary_with_legend.png"), summary_image)
        
        # Crear fitxer de resum de text
        with open(self.folders["visualizations"] / "summary.txt", 'w', encoding='utf-8') as f:
            f.write("RESUM DE DETECCIÓ DE POLÍGONS\n")
            f.write("=" * 40 + "\n\n")
            
            total_polygons = 0
            for airspace_type, polygons in self.vertex_data.items():
                f.write(f"{airspace_type.upper()}: {len(polygons)} polígons\n")
                total_polygons += len(polygons)
            
            f.write(f"\nTOTAL: {total_polygons} polígons detectats\n")
            f.write(f"Imatge original: {self.original_image.shape[1]}x{self.original_image.shape[0]} píxels\n")
        
        print("✓ Resum visual creat")
    
    def create_readme(self):
        """Crea un fitxer README amb informació sobre els resultats."""
        readme_path = self.main_folder / "README.md"
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write("# Resultats de Detecció de Polígons d'Espais Aeris\n\n")
            f.write(f"**Data de processament:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Imatge original:** {self.image_path or 'Preprocessada'}\n\n")
            
            f.write("## Estructura de Carpetes\n\n")
            f.write("- `01_original/` - Imatge original\n")
            f.write("- `02_individual_polygons/` - Imatges individuals de cada polígon\n")
            f.write("- `03_by_airspace_type/` - Imatges agrupades per tipus d'espai aeri\n")
            f.write("- `04_superimposed/` - Imatges amb tots els polígons superposats\n")
            f.write("- `05_coordinates/` - Fitxers de coordenades dels vèrtexs\n")
            f.write("- `06_visualizations/` - Resums visuals i llegendes\n")
            f.write("- `07_data/` - Dades completes en format JSON\n\n")
            
            f.write("## Fitxers Principals\n\n")
            f.write("- `all_polygons_filled.png` - Tots els polígons omplerts\n")
            f.write("- `all_polygons_outlines.png` - Només contorns dels polígons\n")
            f.write("- `all_polygons_vertices.png` - Només vèrtexs dels polígons\n")
            f.write("- `vertex_coordinates.txt` - Coordenades en format llegible\n")
            f.write("- `vertex_coordinates.csv` - Coordenades en format CSV\n")
            f.write("- `vertex_data.json` - Dades completes en JSON\n\n")
            
            f.write("## Estadístiques\n\n")
            total_polygons = sum(len(polygons) for polygons in self.vertex_data.values())
            f.write(f"- **Total polígons detectats:** {total_polygons}\n")
            
            for airspace_type, polygons in self.vertex_data.items():
                if polygons:
                    f.write(f"- **{airspace_type}:** {len(polygons)} polígons\n")
        
        print("✓ Fitxer README creat")
    
    def run_complete_analysis(self):
        """Executa l'anàlisi complet i crea tots els resultats."""
        print("\n🚀 INICIANT ANÀLISI COMPLET DE POLÍGONS")
        print("=" * 50)
        
        try:
            # Crear imatges individuals
            self.create_individual_polygon_images()
            
            # Crear imatges per tipus d'espai aeri
            self.create_airspace_type_images()
            
            # Crear imatges superposades
            self.create_superimposed_images()
            
            # Desa fitxers de coordenades
            self.save_coordinate_files()
            
            # Crear resum visual
            self.create_visualization_summary()
            
            # Crear README
            self.create_readme()
            
            print(f"\n✅ ANÀLISI COMPLETAT!")
            print(f"📁 Resultats desats a: {self.main_folder}")
            print(f"📊 Total polígons detectats: {sum(len(polygons) for polygons in self.vertex_data.values())}")
            
            return self.main_folder
            
        except Exception as e:
            print(f"❌ Error durant l'anàlisi: {e}")
            raise


def main():
    """Funció principal per executar el superposador de polígons."""
    print("🎨 SUPERPOSADOR DE POLÍGONS D'ESPAIS AERIS")
    print("=" * 50)
    
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
    
    try:
        # Opció 1: Utilitzar carpeta de preprocessament si existeix
        if preprocessing_folders:
            print(f"\n🔧 Utilitzant carpeta de preprocessament...")
            latest_folder = sorted(preprocessing_folders)[-1]
            superimposer = PolygonSuperimposer(preprocessed_folder=latest_folder)
        
        # Opció 2: Processar imatge directament
        elif vfr_images:
            print(f"\n🔧 Processant imatge directament...")
            superimposer = PolygonSuperimposer(image_path=vfr_images[0])
        
        else:
            print("\n⚠️  No s'han trobat imatges VFR ni carpetes de preprocessament.")
            print("   Assegura't que tens una imatge VFR o executa primer el preprocessament.")
            return
        
        # Executar anàlisi complet
        result_folder = superimposer.run_complete_analysis()
        
        print(f"\n🎉 PROCESSAMENT COMPLETAT!")
        print(f"📁 Obre la carpeta: {result_folder}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()

