import os
import json
import numpy as np
import cv2
import base64

ANNOT_DIR = 'annotations'  # folder with JSON files
IMAGE_DIR = 'images'       # folder with original images
OUT_MASK_DIR = 'masks'     # where masks will be saved

os.makedirs(OUT_MASK_DIR, exist_ok=True)


for filename in os.listdir(ANNOT_DIR):
    if not filename.endswith('.json'):
        continue

    json_path = os.path.join(ANNOT_DIR, filename)
    with open(json_path, 'r') as f:
        data = json.load(f)

    img_name = data['imagePath']
    img_path = os.path.join(IMAGE_DIR, img_name)

    if not os.path.exists(img_path):
        continue

    width = data['imageWidth']
    height = data['imageHeight']

    for idx, shape in enumerate(data['shapes']):
        label_id = idx + 1

        if shape.get('shape_type') == 'mask' and 'mask' in shape:
            decoded = base64.b64decode(shape['mask'])
            arr = np.frombuffer(decoded, np.uint8)
            m = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
            p = shape['points']
            t = np.zeros((height, width), dtype=np.uint8)
            t[int(p[0][1]): int(p[1][1]) + 1, int(p[0][0]): int(p[1][0]) + 1] = m

            mask = np.zeros((height, width), dtype=np.uint8)
            mask[t > 0] = 255

            label = shape['label']
            out_name = filename.replace('.json', f'_{label}.png')
            out_path = os.path.join(OUT_MASK_DIR, out_name)
            cv2.imwrite(out_path, mask)
            print(f'Saved mask: {out_path}')

print('All masks generated in:', OUT_MASK_DIR)
