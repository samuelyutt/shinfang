import os
import cv2
import numpy as np
from tqdm import tqdm
from pathlib import Path

MASK_DIR = Path('./masks')
LABEL_DIR = Path('./labels')
CLASS_MAPPING = {
    1: 0,  # pot
    2: 1,  # bowl
    3: 2,  # spatula
    4: 3   # egg
}

LABEL_DIR.mkdir(parents=True, exist_ok=True)
mask_files = list(MASK_DIR.glob('*.png'))


for mask_path in tqdm(mask_files, desc='Converting masks to YOLO format'):
    mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
    if mask is None:
        continue

    height, width = mask.shape
    yolo_labels = []

    # Find contours for each class ID present in the mask
    for pixel_value, class_id in CLASS_MAPPING.items():
        class_mask = np.uint8(mask == pixel_value)
        contours, _ = cv2.findContours(class_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Process each contour for the current class
        for contour in contours:
            # A contour is a list of points. We need to normalize them.
            # A polygon needs at least 3 points
            if contour.shape[0] < 3:
                continue

            # Normalize coordinates
            normalized_contour = contour.astype(float) / [width, height]
            
            # Flatten the array and format for YOLO
            # Format: class_id x1 y1 x2 y2 ... xn yn
            segment = normalized_contour.flatten().tolist()
            yolo_labels.append(f'{class_id} ' + ' '.join(map(str, segment)))

    # Save the YOLO-formatted labels to a .txt file
    if yolo_labels:
        label_path = LABEL_DIR / (mask_path.stem + '.txt')
        with open(label_path, 'w') as f:
            f.write('\n'.join(yolo_labels))

print(f'Conversion complete. {len(mask_files)} masks converted.')
print(f'YOLO labels saved in: {LABEL_DIR}')
