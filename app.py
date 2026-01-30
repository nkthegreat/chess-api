import base64, io, numpy as np, cv2
from flask import Flask, request, jsonify
from PIL import Image

app = Flask(__name__)


   def identify_piece_2d(square):
    # 1. Κανονικοποίηση
    square = cv2.normalize(square, None, 0, 255, cv2.NORM_MINMAX)
    
    # 2. Χρησιμοποιούμε Canny Edge Detection αντί για σκέτο STD
    # Οι ακμές (edges) είναι πιο αξιόπιστες από τη διακύμανση
    edges = cv2.Canny(square, 100, 200)
    edge_density = np.count_nonzero(edges)

    # ΑΥΣΤΗΡΟ ΦΙΛΤΡΟ: Αν οι ακμές είναι λίγες, το τετράγωνο είναι άδειο
    # Δοκίμασε το 100. Αν βλέπεις ακόμα "φαντάσματα", πήγαινέ το στο 150.
    if edge_density < 100: 
        return None

    # 3. Ανίχνευση χρώματος
    mean = np.mean(square)
    return 'P' if mean > 160 else 'p'

def get_fen(img):
    img_gray = np.array(img.convert('L'))
    img_gray = cv2.resize(img_gray, (400, 400))
    
    # ΕΔΩ Η ΑΛΛΑΓΗ: Median Blur για να σβήσουμε τα pixels της οθόνης
    img_gray = cv2.medianBlur(img_gray, 5)
    
    sq = 400 // 8
    fen_rows = []
    
    for y in range(8):
        row = ""
        empty = 0
        for x in range(8):
            # Αυξάνουμε λίγο το margin στο 12 για να "κόψουμε" τις γραμμές της σκακιέρας
            m = 12
            square = img_gray[y*sq+m : (y+1)*sq-m, x*sq+m : (x+1)*sq-m]
            piece = identify_piece_2d(square)
            
            if piece is None:
                empty += 1
            else:
                if empty > 0: row += str(empty); empty = 0
                row += piece
        if empty > 0: row += str(empty)
        fen_rows.append(row)
        
    return "/".join(fen_rows) + " w - - 0 1"

def get_fen(img):
    img_gray = np.array(img.convert('L'))
    img_gray = cv2.resize(img_gray, (400, 400))
    
    sq = 400 // 8
    fen_rows = []
    
    for y in range(8):
        row = ""
        empty = 0
        for x in range(8):
            # Παίρνουμε το τετράγωνο με περιθώριο για να αποφύγουμε τις γραμμές
            m = 8
            square = img_gray[y*sq+m : (y+1)*sq-m, x*sq+m : (x+1)*sq-m]
            piece = identify_piece_2d(square)
            
            if piece is None:
                empty += 1
            else:
                if empty > 0: row += str(empty); empty = 0
                row += piece
        if empty > 0: row += str(empty)
        fen_rows.append(row)
        
    return "/".join(fen_rows) + " w - - 0 1"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        img = Image.open(io.BytesIO(base64.b64decode(data['image'])))
        return jsonify({"fen": get_fen(img)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run()

