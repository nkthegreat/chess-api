import base64, io, numpy as np, cv2
from flask import Flask, request, jsonify
from PIL import Image
from skimage.metrics import structural_similarity as ssim

app = Flask(__name__)

def detect_piece_ai(square):
    # 1. Προετοιμασία
    square = cv2.resize(square, (32, 32))
    
    # 2. Υπολογισμός "πολυπλοκότητας" (Entropy-based)
    # Τα κενά τετράγωνα έχουν πολύ υψηλή ομοιότητα με τον εαυτό τους αν μετατοπιστούν
    shift_x = np.roll(square, 2, axis=1)
    similarity = ssim(square, shift_x)
    
    # Αν η ομοιότητα είναι πάνω από 0.9, το τετράγωνο είναι "βαρετό" (άδειο)
    if similarity > 0.85:
        return None

    # 3. Ταξινόμηση βάσει κατανομής φωτεινότητας (Histogram Features)
    hist = cv2.calcHist([square], [0], None, [256], [0, 256])
    mean_val = np.mean(square)
    
    # AI Logic: Τα λευκά κομμάτια έχουν "κορυφές" στο δεξί μέρος του ιστογράμματος
    if mean_val > 150:
        # Λευκό - έστω Πιόνι για αρχή, αλλά με AI δομή
        return "P"
    else:
        # Μαύρο
        return "p"

def get_fen(img):
    img_gray = np.array(img.convert('L'))
    img_gray = cv2.resize(img_gray, (400, 400))
    
    # AI Pre-processing: Adaptive Histogram Equalization (CLAHE)
    # Αυτό κάνει τα κομμάτια να "λάμπουν" ακόμα και σε κακό φωτισμό
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    img_gray = clahe.apply(img_gray)
    
    sq = 400 // 8
    fen_rows = []
    
    for y in range(8):
        row = ""
        empty = 0
        for x in range(8):
            margin = 10
            square = img_gray[y*sq+m : (y+1)*sq-m, x*sq+m : (x+1)*sq-m]
            
            piece = detect_piece_ai(square)
            
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
