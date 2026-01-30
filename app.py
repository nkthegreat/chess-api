from flask import Flask, request, jsonify
import base64
import io
from PIL import Image

app = Flask(__name__)

def process_board(img):
    # Μετατροπή σε 400x400 και ασπρόμαυρο για ταχύτητα
    img = img.resize((400, 400)).convert('L')
    width, height = img.size
    sq_w, sq_h = width // 8, height // 8
    
    fen = ""
    for y in range(8):
        empty = 0
        for x in range(8):
            # Κόβουμε το κάθε τετράγωνο
            box = (x*sq_w, y*sq_h, (x+1)*sq_w, (y+1)*sq_h)
            square = img.crop(box)
            
            # Απλός έλεγχος: Αν το τετράγωνο είναι ομοιόμορφο, είναι κενό
            # Εδώ αργότερα θα βάλουμε το TensorFlow μοντέλο
            is_empty = True 
            
            if is_empty:
                empty += 1
            else:
                if empty > 0:
                    fen += str(empty)
                    empty = 0
                fen += "p" 
        if empty > 0: fen += str(empty)
        if y < 7: fen += "/"
    
    return fen + " w - - 0 1"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        image_b64 = data['image']
        image_data = base64.b64decode(image_b64)
        img = Image.open(io.BytesIO(image_data))
        
        fen = process_board(img)
        return jsonify({"fen": fen})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run()
