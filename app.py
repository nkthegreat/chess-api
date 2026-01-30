import base64, io, numpy as np, cv2
from flask import Flask, request, jsonify
from PIL import Image

app = Flask(__name__)

def identify_piece_2d(square):
    # 1. Παίρνουμε το χρώμα του κέντρου και τη διακύμανση
    # Ένα άδειο 2D τετράγωνο στην οθόνη είναι σχεδόν μονόχρωμο στο κέντρο του
    h, w = square.shape
    center_area = square[h//4:3*h//4, w//4:3*w//4]
    std = np.std(center_area)
    mean = np.mean(center_area)

    # 2. Αν η διακύμανση είναι πολύ χαμηλή (< 8), το τετράγωνο είναι άδειο
    # Οι οθόνες έχουν "θόρυβο", οπότε το 8-10 είναι καλό όριο
    if std < 10:
        return None

    # 3. Ανίχνευση Λευκού/Μαύρου
    # Στο Lichess, τα λευκά κομμάτια είναι πολύ πιο φωτεινά από τα τετράγωνα
    if mean > 180: # Πολύ φωτεινό -> Λευκό
        return 'P'
    elif mean < 80: # Πολύ σκούρο -> Μαύρο
        return 'p'
    else:
        # Αν είναι ενδιάμεσο αλλά έχει "θόρυβο", μάλλον είναι κομμάτι
        return 'N' if mean > 120 else 'n'

def get_fen(img):
    # Μετατροπή σε Γκρι και Resize
    img_gray = np.array(img.convert('L'))
    img_gray = cv2.resize(img_gray, (400, 400))
    
    # Ήπιο Blur για να σβήσουμε τις γραμμές της οθόνης (pixels)
    img_gray = cv2.medianBlur(img_gray, 5)
    
    sq = 400 // 8
    fen_rows = []
    
    for y in range(8):
        row = ""
        empty = 0
        for x in range(8):
            # Παίρνουμε το τετράγωνο
            square = img_gray[y*sq : (y+1)*sq, x*sq : (x+1)*sq]
            piece = identify_piece_2d(square)
            
            if piece is None:
                empty += 1
            else:
                if empty > 0:
                    row += str(empty)
                    empty = 0
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
