from flask import Flask, request, jsonify
import base64
import io
from PIL import Image, ImageStat

app = Flask(__name__)

def get_piece_at_square(square_img):
    # Μετατροπή σε ασπρόμαυρο για ανάλυση φωτεινότητας
    gray_sq = square_img.convert('L')
    stat = ImageStat.Stat(gray_sq)
    avg_brightness = stat.mean[0] # Μέση φωτεινότητα
    std_dev = stat.stddev[0]     # Διακύμανση (δείχνει αν έχει "σχήμα" μέσα)

    # Αν η διακύμανση είναι χαμηλή, το τετράγωνο είναι άδειο
    if std_dev < 12: 
        return None
    
    # Αν είναι πολύ φωτεινό, θεωρούμε ότι είναι Λευκό κομμάτι (P)
    # Αν είναι πιο σκούρο, θεωρούμε ότι είναι Μαύρο κομμάτι (p)
    if avg_brightness > 160:
        return "P" # Λευκό
    else:
        return "p" # Μαύρο

def generate_real_fen(img):
    img = img.resize((400, 400))
    sq = 400 // 8
    fen_rows = []
    
    for y in range(8):
        row_string = ""
        empty_count = 0
        for x in range(8):
            box = (x * sq, y * sq, (x + 1) * sq, (y + 1) * sq)
            square = img.crop(box)
            piece = get_piece_at_square(square)
            
            if piece is None:
                empty_count += 1
            else:
                if empty_count > 0:
                    row_string += str(empty_count)
                    empty_count = 0
                row_string += piece
        if empty_count > 0:
            row_string += str(empty_count)
        fen_rows.append(row_string)
            
    return "/".join(fen_rows) + " w - - 0 1"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        image_data = base64.b64decode(data['image'])
        img = Image.open(io.BytesIO(image_data))
        
        # Παραγωγή πραγματικού FEN βάσει της εικόνας
        final_fen = generate_real_fen(img)
        return jsonify({"fen": final_fen})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run()
