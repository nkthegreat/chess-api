import base64
import io
import numpy as np
import cv2
from flask import Flask, request, jsonify
from PIL import Image

app = Flask(__name__)

def identify_piece_2d(square):
    # 1. Κανονικοποίηση φωτεινότητας
    square = cv2.normalize(square, None, 0, 255, cv2.NORM_MINMAX)
    
    # 2. Ανίχνευση ακμών (Canny) - Πολύ πιο σταθερό για οθόνες
    edges = cv2.Canny(square, 100, 200)
    edge_density = np.count_nonzero(edges)

    # Φίλτρο "φαντασμάτων": Αν οι γραμμές είναι λίγες, το τετράγωνο είναι άδειο
    if edge_density < 100: 
        return None

    # 3. Ανίχνευση χρώματος (Λευκό vs Μαύρο)
    mean = np.mean(square)
    return 'P' if mean > 160 else 'p'

def get_fen(img):
    # Μετατροπή σε Gray και Resize
    img_gray = np.array(img.convert('L'))
    img_gray = cv2.resize(img_gray, (400, 400))
    
    # Median Blur για να καθαρίσει το "δίχτυ" της οθόνης
    img_gray = cv2.medianBlur(img_gray, 5)
    
    sq = 400 // 8
    fen_rows = []
    
    for y in range(8):
        row = ""
        empty = 0
        for x in range(8):
            # Margin 12 pixels για να μην βλέπουμε τις γραμμές της σκακιέρας
            m = 12
            square = img_gray[y*sq+m : (y+1)*sq-m, x*sq+m : (x+1)*sq-m]
            piece = identify_piece_2d(square)
            
            if piece is None:
                empty += 1
            else:
                if empty > 0:
                    row += str(empty)
                    empty = 0
                row += piece
        if empty > 0:
            row += str(empty)
        fen_rows.append(row)
        
    return "/".join(fen_rows) + " w - - 0 1"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        image_data = base64.b64decode(data['image'])
        img = Image.open(io.BytesIO(image_data))
        return jsonify({"fen": get_fen(img)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run()
