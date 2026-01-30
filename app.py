from flask import Flask, request, jsonify
import base64, io
import numpy as np
from PIL import Image

app = Flask(__name__)

def get_fen_from_image(img):
    img = img.resize((400, 400)).convert('L')
    sq = 400 // 8
    fen_rows = []
    
    for y in range(8):
        row = ""
        empty = 0
        for x in range(8):
            # Παίρνουμε το τετράγωνο αλλά "κόβουμε" 5 pixels γύρω-γύρω 
            # για να μην βλέπει ο αλγόριθμος τις γραμμές της σκακιέρας
            square = img.crop((x*sq + 5, y*sq + 5, (x+1)*sq - 5, (y+1)*sq - 5))
            
            # Μετατροπή σε array για υπολογισμό
            pixels = np.array(square)
            variance = np.var(pixels)
            avg_brightness = np.mean(pixels)

            # ΑΥΞΗΣΗ ΟΡΙΟΥ: Αν η διακύμανση είναι μικρή, το τετράγωνο είναι άδειο
            # Ανέβασα το όριο στο 300 (από 150) για να είναι πιο αυστηρό
            if variance < 300: 
                empty += 1
            else:
                if empty > 0:
                    row += str(empty)
                    empty = 0
                # Αν είναι φωτεινό -> Λευκό Πιόνι (P), αν είναι σκούρο -> Μαύρο (p)
                row += "P" if avg_brightness > 140 else "p"
                    
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
        
        return jsonify({"fen": get_fen_from_image(img)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run()
