import cv2
import numpy as np
import os
from pathlib import Path
import json
from datetime import datetime

class ChartPreprocessor:
    def __init__(self, input_image_path, output_folder=None):
        """
        Initialize the chart preprocessor with input image and output folder.
        
        Args:
            input_image_path (str): Path to the input PNG/TIFF image
            output_folder (str): Folder to save preprocessing steps (if None, creates timestamped folder)
        """
        self.input_path = input_image_path
        
        # Create timestamped output folder if none specified
        if output_folder is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_name = Path(input_image_path).stem
            output_folder = f"preprocessing_steps_{image_name}_{timestamp}"
        
        self.output_folder = Path(output_folder)
        self.original_image = None
        self.current_image = None
        self.image_info = {}
        
        # Create output folder structure
        self._create_output_folders()
        
        # Load the image
        self._load_image()
    
    def _create_output_folders(self):
        """Create folder structure for each preprocessing step."""
        folders = [
            "01_original",
            "02_grayscale",
            "03_hsv",
            "04_noise_reduction_gaussian",
            "05_noise_reduction_median",
            "06_thresholding",
            "07_binarization",
            "08_edge_detection",
            "09_morphological_dilate",
            "10_morphological_erode",
            "11_morphological_open",
            "12_morphological_close",
            "13_contours",
            "14_polygon_approximation",
            "15_color_segmentation",
            "16_cropped_info_boxes",
            "17_text_enhancement",
            "18_coordinate_mapping"
        ]
        
        for folder in folders:
            (self.output_folder / folder).mkdir(parents=True, exist_ok=True)
    
    def _load_image(self):
        """Load the input image and store basic information."""
        self.original_image = cv2.imread(self.input_path)
        if self.original_image is None:
            raise ValueError(f"Could not load image from {self.input_path}")
        
        self.current_image = self.original_image.copy()
        
        # Store image information
        self.image_info = {
            "original_shape": self.original_image.shape,
            "height": self.original_image.shape[0],
            "width": self.original_image.shape[1],
            "channels": self.original_image.shape[2] if len(self.original_image.shape) == 3 else 1
        }
        
        # Save original image
        cv2.imwrite(str(self.output_folder / "01_original" / "original.png"), self.original_image)
        print(f"✓ Imatge carregada: {self.image_info['width']}x{self.image_info['height']} píxels")
    
    def save_step(self, image, step_name, filename="result.png", additional_info=None):
        """Save the current processing step."""
        folder_path = self.output_folder / step_name
        file_path = folder_path / filename
        cv2.imwrite(str(file_path), image)
        
        if additional_info:
            info_path = folder_path / "info.json"
            with open(info_path, 'w') as f:
                json.dump(additional_info, f, indent=2)
        
        print(f"✓ Desat {step_name}: {file_path}")
    
    def convert_to_grayscale(self):
        """Convert image to grayscale."""
        gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        self.save_step(gray, "02_grayscale", "grayscale.png")
        self.current_image = gray
        return gray
    
    def convert_to_hsv(self):
        """Convert image to HSV color space."""
        hsv = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2HSV)
        self.save_step(hsv, "03_hsv", "hsv.png")
        return hsv
    
    def apply_gaussian_blur(self, kernel_size=(5, 5), sigma=0):
        """Apply Gaussian blur for noise reduction."""
        blurred = cv2.GaussianBlur(self.current_image, kernel_size, sigma)
        self.save_step(blurred, "04_noise_reduction_gaussian", "gaussian_blur.png", 
                      {"kernel_size": kernel_size, "sigma": sigma})
        self.current_image = blurred
        return blurred
    
    def apply_median_blur(self, kernel_size=5):
        """Apply median blur for noise reduction."""
        blurred = cv2.medianBlur(self.current_image, kernel_size)
        self.save_step(blurred, "05_noise_reduction_median", "median_blur.png",
                      {"kernel_size": kernel_size})
        return blurred
    
    def apply_thresholding(self, threshold_value=127, max_value=255, threshold_type=cv2.THRESH_BINARY):
        """Apply thresholding to the image."""
        if len(self.current_image.shape) == 3:
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = self.current_image
        
        _, thresh = cv2.threshold(gray, threshold_value, max_value, threshold_type)
        self.save_step(thresh, "06_thresholding", "threshold.png",
                      {"threshold_value": threshold_value, "max_value": max_value, 
                       "threshold_type": threshold_type})
        return thresh
    
    def apply_adaptive_thresholding(self, max_value=255, adaptive_method=cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                  threshold_type=cv2.THRESH_BINARY, block_size=11, C=2):
        """Apply adaptive thresholding for better binarization."""
        if len(self.current_image.shape) == 3:
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = self.current_image
        
        adaptive_thresh = cv2.adaptiveThreshold(gray, max_value, adaptive_method, 
                                              threshold_type, block_size, C)
        self.save_step(adaptive_thresh, "07_binarization", "adaptive_threshold.png",
                      {"max_value": max_value, "adaptive_method": adaptive_method,
                       "threshold_type": threshold_type, "block_size": block_size, "C": C})
        return adaptive_thresh
    
    def detect_edges_canny(self, low_threshold=50, high_threshold=150):
        """Apply Canny edge detection."""
        if len(self.current_image.shape) == 3:
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = self.current_image
        
        edges = cv2.Canny(gray, low_threshold, high_threshold)
        self.save_step(edges, "08_edge_detection", "canny_edges.png",
                      {"low_threshold": low_threshold, "high_threshold": high_threshold})
        return edges
    
    def apply_morphological_operations(self, kernel_size=(5, 5), iterations=1):
        """Apply various morphological operations."""
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
        
        # Dilation
        dilated = cv2.dilate(self.current_image, kernel, iterations=iterations)
        self.save_step(dilated, "09_morphological_dilate", "dilated.png",
                      {"kernel_size": kernel_size, "iterations": iterations})
        
        # Erosion
        eroded = cv2.erode(self.current_image, kernel, iterations=iterations)
        self.save_step(eroded, "10_morphological_erode", "eroded.png",
                      {"kernel_size": kernel_size, "iterations": iterations})
        
        # Opening (erosion followed by dilation)
        opened = cv2.morphologyEx(self.current_image, cv2.MORPH_OPEN, kernel, iterations=iterations)
        self.save_step(opened, "11_morphological_open", "opened.png",
                      {"kernel_size": kernel_size, "iterations": iterations})
        
        # Closing (dilation followed by erosion)
        closed = cv2.morphologyEx(self.current_image, cv2.MORPH_CLOSE, kernel, iterations=iterations)
        self.save_step(closed, "12_morphological_close", "closed.png",
                      {"kernel_size": kernel_size, "iterations": iterations})
        
        return dilated, eroded, opened, closed
    
    def detect_contours(self, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE):
        """Detect contours in the image."""
        if len(self.current_image.shape) == 3:
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = self.current_image
        
        contours, hierarchy = cv2.findContours(gray, mode, method)
        
        # Draw contours on a copy of the original image
        contour_image = self.original_image.copy()
        cv2.drawContours(contour_image, contours, -1, (0, 255, 0), 2)
        
        self.save_step(contour_image, "13_contours", "contours.png",
                      {"num_contours": len(contours), "mode": mode, "method": method})
        
        return contours, hierarchy
    
    def approximate_polygons(self, contours, epsilon_factor=0.02):
        """Approximate contours as polygons."""
        approximated_contours = []
        
        for contour in contours:
            epsilon = epsilon_factor * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            approximated_contours.append(approx)
        
        # Draw approximated polygons
        poly_image = self.original_image.copy()
        cv2.drawContours(poly_image, approximated_contours, -1, (255, 0, 0), 2)
        
        self.save_step(poly_image, "14_polygon_approximation", "polygons.png",
                      {"num_polygons": len(approximated_contours), "epsilon_factor": epsilon_factor})
        
        return approximated_contours
    
    def segment_colors(self, hsv_image, color_ranges):
        """Segment image based on color ranges for airspace classes."""
        segmented_images = {}
        
        for color_name, (lower, upper) in color_ranges.items():
            # Create mask for the color range
            mask = cv2.inRange(hsv_image, np.array(lower), np.array(upper))
            
            # Apply mask to original image
            segmented = cv2.bitwise_and(self.original_image, self.original_image, mask=mask)
            
            # Save segmented image
            folder_name = f"15_color_segmentation/{color_name}"
            (self.output_folder / folder_name).mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(self.output_folder / folder_name / f"{color_name}_segmented.png"), segmented)
            cv2.imwrite(str(self.output_folder / folder_name / f"{color_name}_mask.png"), mask)
            
            segmented_images[color_name] = segmented
            print(f"✓ Segmentació de color per a {color_name}")
        
        return segmented_images
    
    def crop_info_boxes(self, boxes):
        """Crop information boxes from the image."""
        cropped_boxes = []
        
        for i, (x, y, w, h) in enumerate(boxes):
            cropped = self.original_image[y:y+h, x:x+w]
            
            # Save cropped box
            folder_name = f"16_cropped_info_boxes/box_{i+1}"
            (self.output_folder / folder_name).mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(self.output_folder / folder_name / f"box_{i+1}.png"), cropped)
            
            cropped_boxes.append(cropped)
            print(f"✓ Caixa d'informació retallada {i+1}: {w}x{h} píxels")
        
        return cropped_boxes
    
    def enhance_text_for_ocr(self, image):
        """Enhance text in the image for better OCR."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Apply morphological operations to clean up text
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        enhanced = cv2.morphologyEx(enhanced, cv2.MORPH_CLOSE, kernel)
        
        self.save_step(enhanced, "17_text_enhancement", "enhanced_text.png")
        return enhanced
    
    def map_pixel_to_latlon(self, pixel_coords, chart_bounds):
        """
        Map pixel coordinates to latitude/longitude.
        
        Args:
            pixel_coords: List of (x, y) pixel coordinates
            chart_bounds: Dictionary with 'north', 'south', 'east', 'west' bounds
        """
        height, width = self.original_image.shape[:2]
        
        # Calculate scale factors
        lat_range = chart_bounds['north'] - chart_bounds['south']
        lon_range = chart_bounds['east'] - chart_bounds['west']
        
        lat_scale = lat_range / height
        lon_scale = lon_range / width
        
        # Convert pixel coordinates to lat/lon
        latlon_coords = []
        for x, y in pixel_coords:
            lat = chart_bounds['north'] - (y * lat_scale)
            lon = chart_bounds['west'] + (x * lon_scale)
            latlon_coords.append((lat, lon))
        
        # Save coordinate mapping info
        mapping_info = {
            "pixel_coords": pixel_coords,
            "latlon_coords": latlon_coords,
            "chart_bounds": chart_bounds,
            "image_dimensions": {"width": width, "height": height},
            "scale_factors": {"lat_scale": lat_scale, "lon_scale": lon_scale}
        }
        
        info_path = self.output_folder / "18_coordinate_mapping" / "coordinate_mapping.json"
        with open(info_path, 'w') as f:
            json.dump(mapping_info, f, indent=2)
        
        print(f"✓ Mapejades {len(pixel_coords)} coordenades a lat/lon")
        return latlon_coords
    
    def run_full_pipeline(self, chart_bounds=None, color_ranges=None, info_boxes=None):
        """Run the complete preprocessing pipeline."""
        print("Iniciant pipeline de preprocessament de cartes...")
        print("=" * 50)
        
        # Step 1: Already loaded original image
        
        # Step 2: Grayscale conversion
        print("\n2. Convertint a escala de grisos...")
        self.convert_to_grayscale()
        
        # Step 3: HSV conversion
        print("\n3. Convertint a HSV...")
        hsv_image = self.convert_to_hsv()
        
        # Step 4: Noise reduction
        print("\n4. Aplicant reducció de soroll...")
        self.apply_gaussian_blur()
        self.apply_median_blur()
        
        # Step 5: Thresholding
        print("\n5. Aplicant umbralització...")
        self.apply_thresholding()
        self.apply_adaptive_thresholding()
        
        # Step 6: Edge detection
        print("\n6. Detectant vores...")
        self.detect_edges_canny()
        
        # Step 7: Morphological operations
        print("\n7. Aplicant operacions morfològiques...")
        self.apply_morphological_operations()
        
        # Step 8: Contour detection
        print("\n8. Detectant contorns...")
        contours, hierarchy = self.detect_contours()
        
        # Step 9: Polygon approximation
        print("\n9. Aproximant polígons...")
        approximated_contours = self.approximate_polygons(contours)
        
        # Step 10: Color segmentation (if color ranges provided)
        if color_ranges:
            print("\n10. Realitzant segmentació de color...")
            self.segment_colors(hsv_image, color_ranges)
        
        # Step 11: Crop info boxes (if boxes provided)
        if info_boxes:
            print("\n11. Retallant caixes d'informació...")
            self.crop_info_boxes(info_boxes)
        
        # Step 12: Text enhancement
        print("\n12. Millorant text per a OCR...")
        self.enhance_text_for_ocr(self.current_image)
        
        # Step 13: Coordinate mapping (if chart bounds provided)
        if chart_bounds:
            print("\n13. Configurant mapatge de coordenades...")
            # Example pixel coordinates (you can modify these)
            sample_coords = [(100, 100), (500, 300), (800, 600)]
            self.map_pixel_to_latlon(sample_coords, chart_bounds)
        
        print("\n" + "=" * 50)
        print("Pipeline de preprocessament completat!")
        print(f"Resultats desats a: {self.output_folder}")


def main():
    """Main function to run the preprocessing pipeline."""
    # Example usage
    input_image = "VFR-TOULOUSE.png"  # Change this to your image path
    
    # Define color ranges for airspace segmentation (HSV values)
    color_ranges = {
        "restricted_airspace": ([0, 50, 50], [10, 255, 255]),  # Red-ish
        "controlled_airspace": ([100, 50, 50], [130, 255, 255]),  # Blue-ish
        "uncontrolled_airspace": ([40, 50, 50], [80, 255, 255]),  # Green-ish
    }
    
    # Define chart bounds (example for Bordeaux area)
    chart_bounds = {
        "north": 45.2,
        "south": 44.5,
        "east": -0.3,
        "west": -1.0
    }
    
    # Define info boxes to crop (x, y, width, height)
    info_boxes = [
        (50, 50, 200, 100),    # Example box 1
        (300, 400, 150, 80),   # Example box 2
    ]
    
    try:
        # Initialize preprocessor
        preprocessor = ChartPreprocessor(input_image)
        
        # Run full pipeline
        preprocessor.run_full_pipeline(
            chart_bounds=chart_bounds,
            color_ranges=color_ranges,
            info_boxes=info_boxes
        )
        
    except Exception as e:
        print(f"Error: {e}")
        print("Assegura't que la imatge d'entrada existeix i és un fitxer PNG/TIFF vàlid.")


if __name__ == "__main__":
    main()
