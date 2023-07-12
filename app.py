import re
import joblib
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load the trained model
pipeline = joblib.load('email_classification_model.joblib')

def extract_text_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator=' ')
    # Remove extra whitespaces and newlines
    clean_text = re.sub('\s+', ' ', text).strip()
    return clean_text

@app.route('/predict', methods=['POST'])
def predict_email():
    try:
        # Check if the request has the correct API key
        api_key = request.headers.get('x-api-key')
        if api_key != 'lvlScmd2Oup2cmjYQkw12gASiYwLBZzd':
            return jsonify({'error': 'Invalid API key'}), 401

        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Read the file and extract text from HTML
        html = file.read().decode('utf-8')
        text = extract_text_from_html(html)

        # Classify the email
        predicted_label = pipeline.predict([text])
        predicted_probabilities = pipeline.predict_proba([text])

        # Return the prediction as JSON
        return jsonify({'result': True, 'data': {
            'predicted_label': predicted_label[0],
            'predicted_probabilities': {
                'automated': predicted_probabilities[0][0],
                'human': predicted_probabilities[0][1]
            },
            'text': text
        }})
    except Exception as e:
        return jsonify({'result': False, 'error': str(e)}), 500
    

if __name__ == '__main__':
    app.run()