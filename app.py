import os
import base64
from flask import Flask, request, send_file, render_template_string
import filetype
from google import genai
from google.genai import types

app = Flask(__name__)
port = 3000


API_KEY = "YOUR GEMINI API KEYS"

client = genai.Client(api_key=API_KEY)

@app.route("/", methods=["GET"])
def index():
    return send_file(os.path.join(os.path.dirname(__file__), "index.html"))

@app.route("/result", methods=["POST"])
def result():
    try:
        if 'file' not in request.files:
            return "No files were uploaded.", 400
        
        uploaded_file = request.files['file']
        
        if uploaded_file.filename == '':
            return "No files were uploaded.", 400

        file_bytes = uploaded_file.read()
        
        # Deteksi tipe mime file
        kind = filetype.guess(file_bytes)
        
        if kind is None or not kind.mime.startswith("audio/"):
            return "File yang diunggah harus berupa audio.", 400

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=[
                types.Part.from_bytes(
                    data=file_bytes,
                    mime_type=kind.mime
                ),
                "Transcribe this audio."
            ]
        )

        transcript = response.text if response.text else "Tidak ada hasil transkripsi."

        html_template = """
        <!DOCTYPE html>
        <html lang="id">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>Success</title>
          <script src="https://cdn.tailwindcss.com"></script>
          <style>
            body {
              background-image: linear-gradient(to right top, #d16ba5, #c777b9, #ba83ca, #aa8fd8, #9a9ae1, #8aa7ec, #79b3f4, #69bff8, #52cffe, #41dfff, #46eefa, #5ffbf1);
              background-size: cover;
              background-attachment: fixed;
            }
            .card-glow {
              box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05), 0 0 30px rgba(124, 58, 237, 0.6);
              transition: all 0.3s ease-in-out;
            }
            .card-glow:hover {
              transform: translateY(-5px);
              box-shadow: 0 15px 20px -5px rgba(0, 0, 0, 0.1), 0 6px 8px -3px rgba(0, 0, 0, 0.08), 0 0 40px rgba(167, 139, 250, 0.8);
            }
          </style>
        </head>
        <body class="flex flex-col items-center justify-center min-h-screen p-4">
          <div class="bg-white p-8 rounded-xl shadow-2xl w-full max-w-md card-glow transform hover:scale-105 transition duration-300">
            <div class="bg-gray-100 p-6 rounded-lg text-gray-800 text-sm overflow-auto max-h-60">
              <p id="textresult" class="whitespace-pre-wrap">{{ transcript }}</p>
            </div>
            <div class="text-center mt-6">
              <button onclick="copyText()" class="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-bold py-3 px-8 rounded-full shadow-lg transform hover:scale-105 transition duration-300 ease-in-out focus:outline-none focus:ring-4 focus:ring-purple-300">
                Copy
              </button>
            </div>
          </div>

          <script>
            function copyText() {
              const textToCopy = document.getElementById('textresult').innerText;
              navigator.clipboard.writeText(textToCopy)
                .then(() => alert("Teks berhasil disalin!"))
                .catch(err => alert("Gagal menyalin teks: " + err));
            }
          </script>
        </body>
        </html>
        """
        
        return render_template_string(html_template, transcript=transcript)

    except Exception as e:
        print(f"Error: {e}")
        return "Terjadi kesalahan saat memproses file.", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True)
