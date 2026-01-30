import base64
import io
import numpy as np
import cv2
from flask import Flask, request, jsonify
from PIL import Image

app = Flask(__name__)

def identify_piece(square_gray):
    # Μετατροπή σε Binary για να δούμε καθαρά το σχήμα
    _, thresh = cv2.threshold(square_gray, 128, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    
    # Εύρεση περιγραμμάτων
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None
    
    # Βρίσκουμε το μεγαλύτερο αντικείμενο στο τετράγωνο
    c = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(c)
    
    # Αν το αντικείμενο είναι πολύ μικρό, είναι θόρυβος
    if area < 100:
        return None

    # Υπολογισμός μέσης φωτεινότητας για λευκό/μαύρο
    avg_brightness = np.mean(square_gray[thresh > 0])
    
    # Βασική λογική αναγνώρισης βάσει μεγέθους (Area)
    # Πιόνι: μικρό, Αξιωματικός/Άλογο: μεσαίο, Βασιλιάς/Πύργος: μεγάλο
    if area > 1500: piece = 'Q' # Μεγάλο σχήμα
    elif area > 1000: piece = 'R' # Μεσαίο-Μεγάλο
    elif area > 600: piece = 'N'  # Μεσαίο
    else: piece = 'P'             # Μικρό
    
    # Αν η φωτεινότητα είναι χαμηλή, είναι μαύρο κομμάτι (πεζά γράμματα στο FEN)
    return piece.lower() if avg_brightness < 120 else piece

def get_fen(img):
    # Μετατροπή σε OpenCV format
    open_cv_image = np.array(img.convert('L'))
    open_cv_image = cv2.resize(open_cv_image, (400, 400))
    
    sq = 400 // 8
    fen_rows = []
    
    for y in range(8):
        row = ""
        empty = 0
        for x in range(8):
            # Παίρνουμε το τετράγωνο με εσωτερικό margin για να αποφύγουμε τις γραμμές
            square = open_cv_image[y*sq+5 : (y+1)*sq-5, x*sq+5 : (x+1)*sq-5]
            piece = identify_piece(square)
            
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
