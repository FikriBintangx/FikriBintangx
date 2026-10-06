import cv2
import numpy as np
import sys
import os
from PIL import Image
from rembg import remove

def prep_photo(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        sys.exit(1)
        
    print(f"Removing background from {input_path}...")
    with open(input_path, "rb") as f:
        input_data = f.read()
    
    subject_data = remove(input_data)
    
    # Save temp and open with cv2
    temp_path = "temp_subject.png"
    with open(temp_path, "wb") as f:
        f.write(subject_data)
        
    img = cv2.imread(temp_path, cv2.IMREAD_UNCHANGED)
    os.remove(temp_path)
    
    # Create pure white background
    h, w = img.shape[:2]
    white_bg = np.ones((h, w, 4), dtype=np.uint8) * 255
    
    # Extract alpha channel
    alpha = img[:, :, 3] / 255.0
    
    # Composite onto white
    for c in range(3):
        white_bg[:, :, c] = (alpha * img[:, :, c] + (1 - alpha) * white_bg[:, :, c])
        
    # Convert to grayscale
    gray = cv2.cvtColor(white_bg, cv2.COLOR_BGRA2GRAY)
    
    # Boost contrast with CLAHE
    print("Applying CLAHE contrast boost...")
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    cv2.imwrite(output_path, enhanced)
    print(f"Saved prepped photo to {output_path}")

if __name__ == "__main__":
    in_file = sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg"
    out_file = sys.argv[2] if len(sys.argv) > 2 else "source-prepped.png"
    prep_photo(in_file, out_file)
