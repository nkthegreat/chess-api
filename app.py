from flask import Flask, request, jsonify
import base64
import io
from PIL import Image, ImageStat

app = Flask(__name__)

def is_square_empty(square_img):
    # Μετατρέπουμε σε ασπρόμαυρο και υπολογίζουμε τη διακύμανση (Standard Deviation)
    # Τα κενά τετράγωνα έχουν πολύ χαμηλή διακύμανση χρωμάτων.
    stat = ImageStat.Stat(square_img.convert('L'))
    std_dev = stat.stddev[0]
    # Αν η διακύμανση είναι πάνω από 15, μάλλον έχει πιόνι (δοκίμασε αυτό το νούμερο)
    return std_dev < 15

def get_fen(img):
    img = img.resize((400, 400))
    width, height = img.size
    sq = width // 8
    fen = ""
    
    for y in range(8):
        empty_count = 0
        for x in range(8):
            box = (x * sq, y * sq, (x + 1) * sq, (y + 1) * sq)
            square = img.crop(box)
            
            if is_square_empty(square):
                empty_count += 1
            else:
                if empty_count > 0:
                    fen += str(empty_count)
                    empty_count = 0
                # Εδώ βάζουμε "p" (πιόνι) προσωρινά. 
                # Σε επόμενο βήμα θα ξεχωρίζουμε αν είναι Βασιλιάς, Πύργος κτλ.
                fen += "p"
        
        if empty_count > 0:
            fen += str(empty_count)
        if y < 7:
            fen += "/"
            
    return fen + " w - - 0 1"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        image_data = base64.b64decode(data['image'])
        img = Image.open(io.BytesIO(image_data))
        
        fen_result = get_fen(img)
        return jsonify({"fen": fen_result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run()
