# Eina de Preprocessament de Cartes VFR

Una eina Python completa per al preprocessament de cartes VFR (Visual Flight Rules) utilitzant només OpenCV. Aquesta eina realitza tots els passos essencials de preprocessament necessaris per preparar cartes d'aviació per a anàlisi posterior, OCR o mapatge de coordenades.

## Característiques

L'eina realitza els següents passos de preprocessament en seqüència:

1. **Càrrega d'imatge d'alta resolució** - Suporta formats PNG/TIFF
2. **Conversió a escala de grisos** - Converteix a escala de grisos per a anàlisi
3. **Conversió d'espai de color HSV** - Per a segmentació basada en color
4. **Reducció de soroll** - Filtres de desenfocament gaussià i mediana
5. **Umbralització/Binarització** - Umbralització bàsica i adaptativa
6. **Detecció de vores** - Algoritme de detecció de vores Canny
7. **Operacions morfològiques** - Dilatació, erosió, obertura, tancament
8. **Detecció de contorns** - Trobar i extreure contorns
9. **Aproximació de polígons** - Aproximar contorns com a polígons
10. **Segmentació de color** - Segmentar classes d'espai aeri per color
11. **Retallada de caixes d'informació** - Extreure àrees específiques de la carta
12. **Millora de text** - Preparar àrees de text per a OCR
13. **Mapatge de coordenades** - Mapejar coordenades de píxels a lat/lon

## Instal·lació

1. Instal·la les dependències necessàries:
```bash
pip install -r requirements.txt
```

## Ús

### Ús Bàsic

```python
from chart_preprocessing import ChartPreprocessor

# Inicialitza amb la teva imatge de carta VFR
preprocessor = ChartPreprocessor("your_chart.png", "output_folder")

# Executa el pipeline complet de preprocessament
preprocessor.run_full_pipeline()
```

### Ús Avançat amb Paràmetres Personalitzats

```python
from chart_preprocessing import ChartPreprocessor

# Defineix els rangs de color per a la segmentació d'espai aeri (valors HSV)
airspace_colors = {
    "restricted_airspace": ([0, 50, 50], [10, 255, 255]),      # Vermell
    "controlled_airspace": ([100, 50, 50], [130, 255, 255]),   # Blau
    "uncontrolled_airspace": ([40, 50, 50], [80, 255, 255]),   # Verd
}

# Defineix els límits geogràfics de la carta
chart_bounds = {
    "north": 45.2,    # Latitud més septentrional
    "south": 44.5,    # Latitud més meridional
    "east": -0.3,     # Longitud més oriental
    "west": -1.0      # Longitud més occidental
}

# Defineix les àrees a retallar per a anàlisi
info_boxes = [
    (50, 50, 200, 100),      # Títol de la carta
    (300, 400, 150, 80),     # Llegenda
]

# Inicialitza i executa
preprocessor = ChartPreprocessor("VFR-BORDEAUX.png")
preprocessor.run_full_pipeline(
    chart_bounds=chart_bounds,
    color_ranges=airspace_colors,
    info_boxes=info_boxes
)
```

### Executar l'Exemple

```bash
python example_usage.py
```

## Estructura de Sortida

L'eina crea una carpeta de sortida estructurada amb les següents subcarpetes:

```
preprocessing_steps/
├── 01_original/              # Imatge original
├── 02_grayscale/             # Conversió a escala de grisos
├── 03_hsv/                   # Espai de color HSV
├── 04_noise_reduction_gaussian/  # Desenfocament gaussià
├── 05_noise_reduction_median/    # Desenfocament mediana
├── 06_thresholding/          # Umbralització bàsica
├── 07_binarization/          # Umbralització adaptativa
├── 08_edge_detection/        # Detecció de vores Canny
├── 09_morphological_dilate/  # Dilatació
├── 10_morphological_erode/   # Erosió
├── 11_morphological_open/    # Obertura
├── 12_morphological_close/   # Tancament
├── 13_contours/              # Contorns detectats
├── 14_polygon_approximation/ # Aproximació de polígons
├── 15_color_segmentation/    # Segmentació basada en color
│   ├── restricted_airspace/
│   ├── controlled_airspace/
│   └── uncontrolled_airspace/
├── 16_cropped_info_boxes/    # Àrees d'informació retallades
├── 17_text_enhancement/      # Millora de text per a OCR
└── 18_coordinate_mapping/    # Mapatge de píxels a lat/lon
```

## Personalització

### Segmentació de Color

Ajusta els rangs de color HSV al diccionari `airspace_colors` per coincidir amb els colors específics de la teva carta:

```python
airspace_colors = {
    "restricted_airspace": ([0, 50, 50], [10, 255, 255]),    # Àrees vermelles
    "controlled_airspace": ([100, 50, 50], [130, 255, 255]), # Àrees blaves
    # Afegeix més rangs de color segons sigui necessari
}
```

### Límits de la Carta

Estableix els límits geogràfics de la teva carta per al mapatge de coordenades:

```python
chart_bounds = {
    "north": 45.2,    # Ajusta per a la teva carta
    "south": 44.5,
    "east": -0.3,
    "west": -1.0
}
```

### Caixes d'Informació

Defineix les àrees a retallar per a anàlisi de text:

```python
info_boxes = [
    (x, y, width, height),  # Format: (x, y, width, height)
    # Afegeix més caixes segons sigui necessari
]
```

## Processament de Passos Individuals

També pots executar passos individuals de preprocessament:

```python
preprocessor = ChartPreprocessor("chart.png")

# Converteix a escala de grisos
gray = preprocessor.convert_to_grayscale()

# Aplica reducció de soroll
blurred = preprocessor.apply_gaussian_blur()

# Detecta vores
edges = preprocessor.detect_edges_canny()

# I així successivament...
```

## Requisits

- Python 3.7+
- OpenCV 4.8.0+
- NumPy 1.21.0+

## Notes

- L'eina crea automàticament carpetes de sortida per a cada pas de processament
- Cada pas desa tant la imatge processada com les metadades (format JSON)
- La segmentació de color crea carpetes separades per a cada classe d'espai aeri
- El mapatge de coordenades requereix límits precisos de la carta per a una conversió correcta de lat/lon
- Tots els passos de processament utilitzen només OpenCV (sense biblioteques addicionals de processament d'imatges)

## Llicència

Aquesta eina es proporciona tal com està per a finalitats educatives i de recerca.
