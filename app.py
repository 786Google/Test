from flask import Flask, request, render_template, jsonify
import google.generativeai as genai
import os
import uuid
import tempfile

app = Flask(__name__, template_folder='templates')
# --- Configure Gemini API Key (securely!) ---
GEMINI_API_KEY = 'AIzaSyBASPK_scXnPq4bTsn5izAxS-MptW6XIx8'
if GEMINI_API_KEY is None:
    raise ValueError("GEMINI_API_KEY environment variable not set.")
genai.configure(api_key=GEMINI_API_KEY)

# --- Gemini Model ---
MODEL = "models/gemini-1.5-pro-latest"

def process_files(files):
    file_uris = []
    for file in files:
        if not file.filename:
            continue

        try:
            # Save the uploaded file to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                file.save(temp_file.name)
                filepath = temp_file.name

            # Upload the file and store the URI
            uploaded_file = genai.upload_file(filepath)
            file_uris.append(uploaded_file)
            os.remove(filepath)  # Remove the temporary file

        except Exception as e:
            print(f"Error uploading file: {e}")
            return None, f"Error uploading file: {e}"

    return file_uris, None

@app.route("/", methods=["GET", "POST"])
def chatbot():
    if request.method == "POST":
        prompt = request.form.get("prompt", "")
        files = request.files.getlist("files")

        file_uris, error_message = process_files(files)
        if error_message:
            return jsonify({"error": error_message})

        prompt_elements = [prompt] if prompt else []
        prompt_elements.extend(file_uris or [])

        if not prompt_elements:
            return jsonify({"response": "Please provide a prompt or upload a file."})

        try:
            # Generate response from the model
            response = genai.GenerativeModel(model_name=MODEL).generate_content(prompt_elements)
            bot_response = response.text
        except Exception as e:
            print(f"Error generating response: {e}")
            bot_response = "An error occurred while processing your request."

        # Cleanup: Delete uploaded files if necessary
        if file_uris:
            for uploaded_file in file_uris:
                try:
                    genai.delete_file(uploaded_file.name)
                except Exception as e:
                    print(f"Error deleting file: {e}")

        return jsonify({"response": bot_response})

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
