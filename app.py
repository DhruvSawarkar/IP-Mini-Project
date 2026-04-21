from flask import Flask, request, jsonify
import cv2
import easyocr
import numpy as np
import re
from PIL import Image

app = Flask(__name__)
reader = easyocr.Reader(['en'])

def clean_text(text):
    return re.sub(r'[^A-Z0-9]', '', text.upper())

def is_indian_plate(text):
    pattern = r'^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{3,4}$'
    return re.match(pattern, text)

def fix_plate(text):
    text = text.upper()
    if len(text) > 10:
        text = text[-10:]

    corrected = ""
    for i, ch in enumerate(text):
        if i in [2,3,6,7,8,9]:
            if ch == 'O': ch = '0'
            elif ch == 'I': ch = '1'
            elif ch == 'Q': ch = '0'
            elif ch == 'U': ch = '0'
        corrected += ch
    return corrected

@app.route("/")
def home():
    return "License Plate API Running"

@app.route("/detect", methods=["POST"])
def detect():
    file = request.files['image']

    image = Image.open(file).convert("RGB")
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    results = reader.readtext(
        image,
        detail=0,
        paragraph=True,
        allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    )

    for text in results:
        text = clean_text(text)
        text = fix_plate(text)

        if is_indian_plate(text):
            return jsonify({"plate": text})

    return jsonify({"plate": "Not detected"})

if __name__ == "__main__":
    app.run()