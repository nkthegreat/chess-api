import base64, io, numpy as np, cv2
from flask import Flask, request, jsonify
from PIL import Image

app = Flask(__name__)

def get_fen(img):
    # 1. Μετατροπή σε Γκρι και εξισορρόπηση φωτισμού (Histogram Equalization)
    img_gray = np.array(img.convert('L'))
    img_gray = cv2.resize(img_gray, (400, 400))
    img_gray = cv2.equalizeHist(img_gray) # Διορθώνει τον κακό φωτισμό
    
    sq = 400 // 8
    fen_rows = []
    
    # Υπολογίζουμε τη μέση φωτεινότητα όλης της σκακιέρας για σύγκριση
    global_mean = np.mean(img_gray)
    
    for y in range(8):
        row = ""
        empty = 0
        for x in range(8):
            # Παίρνουμε το κέντρο του τετραγώνου (margin 12 pixels για σιγουριά)
            margin = 12
            square = img_gray[y*sq+margin : (y+1)*sq-margin, x*sq+margin : (x+1)*sq-margin]
            
            # Υπολογισμός "ζωντάνιας" τετραγώνου
            std = np.std(square) # Διακύμανση
            mean = np.mean(square) # Μέση φωτεινότητα
            
            # Αν το τετράγωνο είναι πολύ "ήσυχο" (std < 20), είναι σίγουρα άδειο
            if std < 20:
                empty += 1
            else:
                if empty > 0:
                    row += str(empty)
                    empty = 0
                
                # Αναγνώριση Λευκού/Μαύρου βάσει της μέσης φωτεινότητας της σκακιέρας
                if mean > global_mean + 10:
                    # Λευκό κομμάτι - Επειδή είδες βασιλιά/πύργο, βάζουμε τυχαία ένα από τα δύο
                    row += 'K' if std > 45 else 'R' 
                else:
                    # Μαύρο κομμάτι
                    row += 'k' if std > 45 else 'r'
                    
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
