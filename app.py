import base64, io, numpy as np, cv2
from flask import Flask, request, jsonify
from PIL import Image

app = Flask(__name__)

def get_piece_type(square):
    # Μετατροπή σε Binary για να δούμε το "σώμα" του κομματιού
    _, thresh = cv2.threshold(square, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Υπολογισμός λευκών pixels (το κομμάτι) προς το σύνολο
    pixels = np.count_nonzero(thresh)
    
    # AI Logic βασισμένο σε γεωμετρικά χαρακτηριστικά
    if pixels < 100: return None # Κενό
    
    brightness = np.median(square[thresh > 0])
    
    # Ταξινόμηση βάσει πυκνότητας (Density Analysis)
    if pixels > 800: piece = 'Q' # Η Βασίλισσα "πιάνει" πολύ χώρο
    elif pixels > 600: piece = 'K' # Ο Βασιλιάς είναι ψηλός
    elif pixels > 400: piece = 'N' # Ο Ίππος έχει περίεργο σχήμα
    else: piece = 'P' # Τα πιόνια είναι μικρά
    
    return piece if brightness > 140 else piece.lower()

def get_fen(img):
    # 1. Pre-processing για οθόνες Lichess
    img_np = np.array(img.convert('L'))
    img_np = cv2.resize(img_np, (400, 400))
    
    # Adaptive Thresholding για να εξαφανίσουμε τις γυαλάδες της οθόνης
    img_np = cv2.adaptiveThreshold(img_np, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    sq = 400 // 8
    fen_rows = []
    
    for y in range(8):
        row = ""
        empty = 0
        for x in range(8):
            # Παίρνουμε το τετράγωνο με "ασφάλεια" 10 pixels
            margin = 10
            square = img_np[y*sq+margin : (y+1)*sq-margin, x*sq+margin : (x+1)*sq-margin]
            
            piece = get_piece_type(square)
            
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
