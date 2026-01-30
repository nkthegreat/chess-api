import base64, io, numpy as np, cv2
from flask import Flask, request, jsonify
from PIL import Image

app = Flask(__name__)

def identify_piece(square):
    # 1. Ενίσχυση αντίθεσης (Contrast) για να ξεχωρίσει το κομμάτι
    square = cv2.normalize(square, None, 0, 255, cv2.NORM_MINMAX)
    
    # 2. Canny Edge Detection με αυστηρά όρια
    edges = cv2.Canny(square, 150, 250)
    edge_density = np.count_nonzero(edges)
    
    # 3. ΠΟΛΥ ΑΥΣΤΗΡΟ ΟΡΙΟ (120): Αν έχει λιγότερες από 120 ακμές, είναι κενό
    if edge_density < 120:
        return None

    # 4. Διαχωρισμός Βασιλιά/Ίππου/Πύργου βάσει "πυκνότητας"
    # Ο Βασιλιάς έχει το πιο σύνθετο περίγραμμα
    brightness = np.median(square)
    
    if edge_density > 450: piece = 'K' # Πολύπλοκο σχήμα -> Βασιλιάς
    elif edge_density > 250: piece = 'N' # Μεσαίο σχήμα -> Ίππος
    else: piece = 'P' # Απλό σχήμα -> Πιόνι
    
    return piece if brightness > 140 else piece.lower()

def get_fen(img):
    img_gray = np.array(img.convert('L'))
    img_gray = cv2.resize(img_gray, (400, 400))
    
    sq = 400 // 8
    fen_rows = []
    
    for y in range(8):
        row = ""
        empty = 0
        for x in range(8):
            # Αποφυγή περιμετρικού θορύβου: 
            # Αν είμαστε στην άκρη της φωτογραφίας, αυξάνουμε το margin
            m = 15 
            square = img_gray[y*sq+m : (y+1)*sq-m, x*sq+m : (x+1)*sq-m]
            
            piece = identify_piece(square)
            
            # Φίλτρο "φαντασμάτων": Αν είμαστε στην 1η ή 8η σειρά και βλέπουμε 
            # υπερβολικά πολλά κομμάτια, μάλλον είναι το πλαίσιο της σκακιέρας.
            if piece:
                if empty > 0:
                    row += str(empty)
                    empty = 0
                row += piece
            else:
                empty += 1
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
