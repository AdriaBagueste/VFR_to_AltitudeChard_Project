# Discontinued Project

## VFR Chart Preprocessing Tool

A complete Python tool for preprocessing VFR (Visual Flight Rules) charts using only OpenCV. This tool performs all the essential preprocessing steps needed to prepare aviation charts for further analysis, OCR, or coordinate mapping.

## Features

The tool performs the following preprocessing steps in sequence:

1. **High-resolution image loading** - Supports PNG/TIFF formats
2. **Grayscale conversion** - Convert to grayscale for analysis
3. **HSV color space conversion** - For color-based segmentation
4. **Noise reduction** - Gaussian and median blur filters
5. **Thresholding/Binarization** - Basic and adaptive thresholding
6. **Edge detection** - Canny edge detection algorithm
7. **Morphological operations** - Dilation, erosion, opening, closing
8. **Contour detection** - Find and extract contours
9. **Polygon approximation** - Approximate contours as polygons
10. **Color segmentation** - Segment airspace classes by color
11. **Information box cropping** - Extract specific areas of the chart
12. **Text enhancement** - Prepare text areas for OCR
13. **Coordinate mapping** - Map pixel coordinates to lat/lon

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from chart_preprocessing import ChartPreprocessor

# Initialize with your VFR chart image
preprocessor = ChartPreprocessor("your_chart.png", "output_folder")

# Run the full preprocessing pipeline
preprocessor.run_full_pipeline()
```

### Advanced Usage with Custom Parameters

```python
from chart_preprocessing import ChartPreprocessor

# Define color ranges for airspace segmentation (HSV values)
airspace_colors = {
    "restricted_airspace": ([0, 50, 50], [10, 255, 255]),      # Red
    "controlled_airspace": ([100, 50, 50], [130, 255, 255]),   # Blue
    "uncontrolled_airspace": ([40, 50, 50], [80, 255, 255]),   # Green
}

# Define the chart's geographic bounds
chart_bounds = {
    "north": 45.2,    # Northernmost latitude
    "south": 44.5,    # Southernmost latitude
    "east": -0.3,     # Easternmost longitude
    "west": -1.0      # Westernmost longitude
}

# Define areas to crop for analysis
info_boxes = [
    (50, 50, 200, 100),      # Chart title
    (300, 400, 150, 80),     # Legend
]

# Initialize and run
preprocessor = ChartPreprocessor("VFR-BORDEAUX.png")
preprocessor.run_full_pipeline(
    chart_bounds=chart_bounds,
    color_ranges=airspace_colors,
    info_boxes=info_boxes
)
```

### Run the Example

```bash
python example_usage.py
```

## Output Structure

The tool creates a structured output folder with the following subfolders:

```
preprocessing_steps/
├── 01_original/              # Original image
├── 02_grayscale/             # Grayscale conversion
├── 03_hsv/                   # HSV color space
├── 04_noise_reduction_gaussian/  # Gaussian blur
├── 05_noise_reduction_median/    # Median blur
├── 06_thresholding/          # Basic thresholding
├── 07_binarization/          # Adaptive thresholding
├── 08_edge_detection/        # Canny edge detection
├── 09_morphological_dilate/  # Dilation
├── 10_morphological_erode/   # Erosion
├── 11_morphological_open/    # Opening
├── 12_morphological_close/   # Closing
├── 13_contours/              # Detected contours
├── 14_polygon_approximation/ # Polygon approximation
├── 15_color_segmentation/    # Color-based segmentation
│   ├── restricted_airspace/
│   ├── controlled_airspace/
│   └── uncontrolled_airspace/
├── 16_cropped_info_boxes/    # Cropped information areas
├── 17_text_enhancement/      # Text enhancement for OCR
└── 18_coordinate_mapping/    # Mapping pixels to lat/lon
```

## Customization

### Color Segmentation

Adjust the HSV color ranges in the `airspace_colors` dictionary to match your chart's specific colors:

```python
airspace_colors = {
    "restricted_airspace": ([0, 50, 50], [10, 255, 255]),    # Red areas
    "controlled_airspace": ([100, 50, 50], [130, 255, 255]), # Blue areas
    # Add more color ranges as needed
}
```

### Chart Bounds

Set your chart's geographic bounds for coordinate mapping:

```python
chart_bounds = {
    "north": 45.2,    # Adjust for your chart
    "south": 44.5,
    "east": -0.3,
    "west": -1.0
}
```

### Information Boxes

Define areas to crop for text analysis:

```python
info_boxes = [
    (x, y, width, height),  # Format: (x, y, width, height)
    # Add more boxes as needed
]
```

## Processing Individual Steps

You can also run individual preprocessing steps:

```python
preprocessor = ChartPreprocessor("chart.png")

# Convert to grayscale
gray = preprocessor.convert_to_grayscale()

# Apply noise reduction
blurred = preprocessor.apply_gaussian_blur()

# Detect edges
edges = preprocessor.detect_edges_canny()

# And so on...
```

## Requirements

- Python 3.7+
- OpenCV 4.8.0+
- NumPy 1.21.0+

## Notes

- The tool automatically creates output folders for each processing step
- Each step saves both the processed image and metadata (JSON format)
- Color segmentation creates separate folders for each airspace class
- Coordinate mapping requires precise chart bounds for correct lat/lon conversion
- All processing steps use only OpenCV (no additional image processing libraries)

## License

This tool is provided as-is for educational and research purposes.
