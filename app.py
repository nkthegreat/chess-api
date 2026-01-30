import base64, io, numpy as np, cv2
from flask import Flask, request, jsonify
from PIL import Image

app = Flask(__name__)

def get_piece(square):
    # 1. Μετατροπή σε Binary με Canny για να βρούμε μόνο τις γραμμές (edges)
    # Αυτό εξαφανίζει το χρώμα του τετραγώνου και κρατάει μόνο το σχήμα του κομματιού
    edges = cv2.Canny(square, 100, 200)
    
    # Μετράμε πόσα "λευκά" pixels (γραμμές) υπάρχουν
    edge_density = np.count_nonzero(edges)
    
    # 2. Αν οι γραμμές είναι ελάχιστες, το τετράγωνο είναι άδειο
    # Ανέβασα το όριο στο 60 για να είναι πιο "σκληρό"
    if edge_density < 60:
        return None

    # 3. Αν υπάρχει κομμάτι, δες τη φωτεινότητα για να βρεις το χρώμα
    # Χρησιμοποιούμε τη διάμεσο (median) για να μην επηρεαζόμαστε από σκιές
    brightness = np.median(square)
    
    # Αν η φωτεινότητα είναι υψηλή (>145), είναι Λευκό (P), αλλιώς Μαύρο (p)
    return "P" if brightness > 145 else "p"

def get_fen(img):
    img_gray = np.array(img.convert('L'))
    img_gray = cv2.resize(img_gray, (400, 400))
    
    # Εφαρμογή ελαφρού Blur για να σβήσουμε "βρωμιές" της κάμερας
    img_gray = cv2.GaussianBlur(img_gray, (5, 5), 0)
    
    sq = 400 // 8
    fen_rows = []
    
    for y in range(8):
        row = ""
        empty = 0
        for x in range(8):
            # Παίρνουμε το κέντρο του τετραγώνου (μεγάλο margin 14px)
            # Κόβουμε πολύ τις άκρες για να ΜΗΝ βλέπει τις γραμμές της σκακιέρας
            margin = 14
            square = img_gray[y*sq+margin : (y+1)*sq-margin, x*sq+margin : (x+1)*sq-margin]
            
            piece = get_piece(square)
            
            if piece is None:
                empty += 1
            else:
                if empty > 0:
                    row += str(empty)
                    empty = 0
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
