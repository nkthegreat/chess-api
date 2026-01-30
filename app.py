from flask import Flask, request, jsonify
import base64
import io
from PIL import Image
# Εδώ θα έρθει το AI μοντέλο σου
# Για τώρα επιστρέφουμε ένα FEN για δοκιμή

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        image_b64 = data['image']
        
        # Αποκωδικοποίηση της εικόνας
        image_data = base64.b64decode(image_b64)
        image = Image.open(io.BytesIO(image_data))
        
        # ΕΔΩ θα μπει ο αλγόριθμος αναγνώρισης
        # π.χ. fen = my_model.predict(image)
        fen = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R" 
        
        return jsonify({"fen": fen})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)