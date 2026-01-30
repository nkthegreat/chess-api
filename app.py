from flask import Flask, request, jsonify
import base64, io
import numpy as np
from PIL import Image

app = Flask(__name__)

# Λίστα με τα κομμάτια (FEN symbols)
PIECES = ['B', 'K', 'N', 'P', 'Q', 'R', 'b', 'k', 'n', 'p', 'q', 'r', 'empty']

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        image_data = base64.b64decode(data['image'])
        img = Image.open(io.BytesIO(image_data)).resize((400, 400)).convert('L')
        
        sq = 400 // 8
        fen = ""
        for y in range(8):
            empty = 0
            for x in range(8):
                # Εδώ κανονικά τρέχει το μοντέλο AI για κάθε τετράγωνο
                # Για να δουλέψει τώρα, ανιχνεύουμε αν το τετράγωνο έχει "θόρυβο"
                square = img.crop((x*sq, y*sq, (x+1)*sq, (y+1)*sq))
                variance = np.var(np.array(square))
                
                if variance < 150: # Τετράγωνο χωρίς κομμάτι
                    empty += 1
                else:
                    if empty > 0: fen += str(empty); empty = 0
                    # Προσωρινά βάζουμε 'p' ή 'P' ανάλογα με τη φωτεινότητα
                    avg = np.mean(np.array(square))
                    fen += "P" if avg > 128 else "p"
                    
            if empty > 0: fen += str(empty)
            if y < 7: fen += "/"
            
        return jsonify({"fen": fen + " w - - 0 1"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run()
