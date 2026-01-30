from flask import Flask, request, jsonify
import base64, io
from PIL import Image, ImageStat

app = Flask(__name__)

def get_fen_from_image(img):
    img = img.resize((400, 400)).convert('L') # Ασπρόμαυρο
    sq = 400 // 8
    fen_rows = []
    for y in range(8):
        row = ""
        empty = 0
        for x in range(8):
            square = img.crop((x*sq, y*sq, (x+1)*sq, (y+1)*sq))
            # Αν η διακύμανση είναι πάνω από 15, έχει πιόνι
            if ImageStat.Stat(square).stddev[0] < 15:
                empty += 1
            else:
                if empty > 0: row += str(empty); empty = 0
                row += "p" # Θεωρούμε όλα τα κομμάτια "p" για τώρα
        if empty > 0: row += str(empty)
        fen_rows.append(row)
    return "/".join(fen_rows) + " w - - 0 1"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        img = Image.open(io.BytesIO(base64.b64decode(data['image'])))
        return jsonify({"fen": get_fen_from_image(img)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run()
