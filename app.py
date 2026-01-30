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
            # Μεγαλύτερο περιθώριο (+10 pixels) για να βλέπει μόνο το κέντρο του τετραγώνου
            square = img.crop((x*sq + 10, y*sq + 10, (x+1)*sq - 10, (y+1)*sq - 10))
            
            pixels = np.array(square)
            variance = np.var(pixels)
            avg_brightness = np.mean(pixels)

            # ΠΟΛΥ ΠΙΟ ΑΥΣΤΗΡΟ ΟΡΙΟ (1000): Αγνοεί σκιές και υφές
            if variance < 1000: 
                empty += 1
            else:
                if empty > 0:
                    row += str(empty)
                    empty = 0
                # Αν είναι πολύ φωτεινό -> Λευκό (P), αλλιώς Μαύρο (p)
                row += "P" if avg_brightness > 160 else "p"
                    
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

