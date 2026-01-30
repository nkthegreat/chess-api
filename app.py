import base64, io, numpy as np, cv2
from flask import Flask, request, jsonify
from PIL import Image

app = Flask(__name__)

def identify_piece_2d(square):
    # Μετατροπή σε γκρι και ελαφρύ Blur για να σβήσουν τα pixels της οθόνης
    square = cv2.GaussianBlur(square, (5, 5), 0)
    
    # Παίρνουμε το χρώμα των άκρων (το χρώμα του τετραγώνου) 
    # και το χρώμα του κέντρου (εκεί που θα είναι το κομμάτι)
    h, w = square.shape
    edge_color = np.median(np.concatenate([square[0,:], square[-1,:], square[:,0], square[:,1]]))
    center_area = square[h//4:3*h//4, w//4:3*w//4]
    center_color = np.median(center_area)
    
    # Υπολογίζουμε τη διαφορά
    diff = abs(center_color - edge_color)
    
    # Αν η διαφορά είναι μικρή, το τετράγωνο είναι άδειο
    if diff < 25: 
        return None

    # Αν η διαφορά είναι μεγάλη, έχουμε κομμάτι. 
    # Αν το κέντρο είναι πολύ φωτεινό (>160), είναι Λευκό (P), αλλιώς Μαύρο (p)
    return 'P' if center_color > 160 else 'p'

def get_fen(img):
    img_gray = np.array(img.convert('L'))
    img_gray = cv2.resize(img_gray, (400, 400))
    
    sq = 400 // 8
    fen_rows = []
    
    for y in range(8):
        row = ""
        empty = 0
        for x in range(8):
            # Παίρνουμε το τετράγωνο με περιθώριο για να αποφύγουμε τις γραμμές
            m = 8
            square = img_gray[y*sq+m : (y+1)*sq-m, x*sq+m : (x+1)*sq-m]
            piece = identify_piece_2d(square)
            
            if piece is None:
                empty += 1
            else:
                if empty > 0: row += str(empty); empty = 0
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
