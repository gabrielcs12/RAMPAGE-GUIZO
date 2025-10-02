from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

pets = []

@app.route("/pets")
def get_pets():
    return jsonify(pets)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    content = data.get("content", "")
    job_ids = re.findall(r"[0-9a-fA-F\-]{36}", content)
    if job_ids:
        new_pet = {
            "content": content,
            "job_ids": job_ids
        }
        pets.append(new_pet)
        print("✅ Novo pet adicionado:", new_pet)
    return "", 204

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)