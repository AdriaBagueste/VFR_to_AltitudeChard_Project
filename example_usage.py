#!/usr/bin/env python3
"""
Example usage of the Chart Preprocessor for VFR charts.

This script demonstrates how to use the ChartPreprocessor class
to process VFR charts with all the preprocessing steps.
"""

from chart_preprocessing import ChartPreprocessor
import os

def process_vfr_chart(image_path):
    """
    Process a VFR chart through all preprocessing steps.
    
    Args:
        image_path (str): Path to the VFR chart image
    """
    
    # Define color ranges for different airspace types (HSV values)
    # These ranges can be adjusted based on your specific chart colors
    airspace_colors = {
        "restricted_airspace": ([0, 50, 50], [10, 255, 255]),      # Red areas
        "controlled_airspace": ([100, 50, 50], [130, 255, 255]),   # Blue areas  
        "uncontrolled_airspace": ([40, 50, 50], [80, 255, 255]),   # Green areas
        "danger_areas": ([20, 50, 50], [40, 255, 255]),            # Yellow/Orange areas
        "prohibited_areas": ([160, 50, 50], [180, 255, 255])       # Magenta areas
    }
    
    # Define chart geographic bounds (adjust these for your specific chart)
    # Example bounds for Bordeaux VFR chart
    chart_bounds = {
        "north": 45.2,    # Northernmost latitude
        "south": 44.5,    # Southernmost latitude  
        "east": -0.3,     # Easternmost longitude
        "west": -1.0      # Westernmost longitude
    }
    
    # Define areas to crop for text analysis (x, y, width, height)
    # These should be adjusted based on your chart's layout
    info_boxes = [
        (50, 50, 200, 100),      # Chart title area
        (300, 400, 150, 80),     # Legend area
        (800, 50, 200, 150),     # Scale information
        (50, 600, 300, 100),     # Airport information
    ]
    
    try:
        print(f"Processant carta VFR: {image_path}")
        print("=" * 60)
        
        # Initialize the preprocessor (will create timestamped folder automatically)
        preprocessor = ChartPreprocessor(image_path)
        
        # Run the complete preprocessing pipeline
        preprocessor.run_full_pipeline(
            chart_bounds=chart_bounds,
            color_ranges=airspace_colors,
            info_boxes=info_boxes
        )
        
        print(f"\n✓ Processament completat amb èxit!")
        print(f"✓ Tots els resultats desats a: {preprocessor.output_folder}")
        print("\nCarpetes generades:")
        print("- 01_original: Imatge original")
        print("- 02_grayscale: Conversió a escala de grisos")
        print("- 03_hsv: Espai de color HSV")
        print("- 04_noise_reduction_gaussian: Desenfocament gaussià")
        print("- 05_noise_reduction_median: Desenfocament mediana")
        print("- 06_thresholding: Umbralització bàsica")
        print("- 07_binarization: Umbralització adaptativa")
        print("- 08_edge_detection: Detecció de vores Canny")
        print("- 09-12_morphological_*: Operacions morfològiques")
        print("- 13_contours: Contorns detectats")
        print("- 14_polygon_approximation: Aproximació de polígons")
        print("- 15_color_segmentation: Segmentació de color d'espai aeri")
        print("- 16_cropped_info_boxes: Àrees d'informació retallades")
        print("- 17_text_enhancement: Millora de text per a OCR")
        print("- 18_coordinate_mapping: Mapatge de píxels a lat/lon")
        
    except FileNotFoundError:
        print(f"Error: Fitxer d'imatge '{image_path}' no trobat.")
        print("Si us plau, assegura't que el fitxer existeix i el camí és correcte.")
    except Exception as e:
        print(f"Error durant el processament: {e}")

def main():
    """Main function to run the example."""
    
    # List of available VFR chart images
    available_images = [
        "VFR-BORDEAUX.png",
        "VFR-TOULOUSE.png"
    ]
    
    print("Exemple de Preprocessament de Cartes VFR")
    print("=" * 40)
    print("\nImatges disponibles:")
    for i, img in enumerate(available_images, 1):
        if os.path.exists(img):
            print(f"{i}. {img} ✓")
        else:
            print(f"{i}. {img} ✗ (no trobat)")
    
    # Process the first available image
    for img in available_images:
        if os.path.exists(img):
            print(f"\nProcessant: {img}")
            process_vfr_chart(img)
            break
    else:
        print("\nNo s'han trobat imatges de cartes VFR al directori actual.")
        print("Si us plau, col·loca una imatge PNG/TIFF al directori actual i executa de nou.")

if __name__ == "__main__":
    main()
