import base64, io, numpy as np, cv2
from flask import Flask, request, jsonify
from PIL import Image
import tflite_runtime.interpreter as tflite

app = Flask(__name__)

# Φόρτωση του AI Μοντέλου
interpreter = tflite.Interpreter(model_path="chess_model.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Ταμπέλες (Πρέπει να είναι με τη σειρά που εκπαιδεύτηκε το μοντέλο)
# Συνήθως: B, K, N, P, Q, R (λευκά), b, k, n, p, q, r (μαύρα), empty
LABELS = ['B', 'K', 'N', 'P', 'Q', 'R', 'b', 'k', 'n', 'p', 'q', 'r', 'empty']

def predict_piece(square_img):
    # Προετοιμασία εικόνας για το AI (συνήθως 224x224 ή 64x64)
    # Δοκιμάζουμε 224x224 που είναι το στάνταρ
    img = cv2.resize(square_img, (224, 224))
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    img = img.astype(np.float32) / 255.0
    img = np.expand_dims(img, axis=0)

    interpreter.set_tensor(input_details[0]['index'], img)
    interpreter.invoke()
    
    output_data = interpreter.get_tensor(output_details[0]['index'])
    index = np.argmax(output_data)
    
    label = LABELS[index]
    return None if label == 'empty' else label

def get_fen(img):
    img_gray = np.array(img.convert('L'))
    img_gray = cv2.resize(img_gray, (400, 400))
    sq = 400 // 8
    fen_rows = []
    
    for y in range(8):
        row = ""
        empty = 0
        for x in range(8):
            m = 5
            square = img_gray[y*sq+m : (y+1)*sq-m, x*sq+m : (x+1)*sq-m]
            piece = predict_piece(square)
            
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
