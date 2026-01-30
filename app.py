import base64
import io
import numpy as np
import cv2
from flask import Flask, request, jsonify
from PIL import Image

app = Flask(__name__)

def identify_piece(square_gray):
    # 1. Καθαρισμός εικόνας
    square_gray = cv2.GaussianBlur(square_gray, (3, 3), 0)
    
    # 2. Υπολογισμός "ενέργειας" άκρων (Canny edge detection)
    # Τα κενά τετράγωνα δεν έχουν σχεδόν καθόλου άκρες στο κέντρο τους
    edges = cv2.Canny(square_gray, 50, 150)
    edge_count = np.sum(edges > 0)
    
    if edge_count < 40: # Πολύ λίγες άκρες = Κενό τετράγωνο
        return None

    # 3. Ανίχνευση αν είναι Λευκό ή Μαύρο βάσει μέσης φωτεινότητας
    avg_brightness = np.mean(square_gray)
    
    # 4. Βασική ταξινόμηση βάσει πυκνότητας άκρων
    # Ο Βασιλιάς και η Βασίλισσα έχουν πολλές λεπτομέρειες (περισσότερες άκρες)
    if edge_count > 300: piece = 'Q'
    elif edge_count > 200: piece = 'R'
    elif edge_count > 120: piece = 'N'
    else: piece = 'P'
    
    return piece.lower() if avg_brightness < 120 else piece

def get_fen(img):
    # Μετατροπή και Resize
    img_gray = np.array(img.convert('L'))
    img_gray = cv2.resize(img_gray, (400, 400))
    
    sq = 400 // 8
    fen_rows = []
    
    for y in range(8):
        row = ""
        empty = 0
        for x in range(8):
            # Παίρνουμε το κέντρο του τετραγώνου (κόβουμε το 20% των άκρων)
            # για να μην βλέπουμε ΠΟΤΕ τις γραμμές της σκακιέρας
            margin = 8
            square = img_gray[y*sq+margin : (y+1)*sq-margin, x*sq+margin : (x+1)*sq-margin]
            
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
