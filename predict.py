import re
import joblib
from bs4 import BeautifulSoup


def extract_text_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator=' ')
    # Remove extra whitespaces and newlines
    clean_text = re.sub('\s+', ' ', text).strip()
    return clean_text


def classify_email(file_path):
    # Load the trained model
    pipeline = joblib.load('email_classification_model.joblib')

    with open(file_path, 'r', encoding='utf-8') as file:
        html = file.read()
        text = extract_text_from_html(html)

        # Classify the email
        predicted_label = pipeline.predict([text])[0]

    return predicted_label


if __name__ == '__main__':
    email_file_path = 'path_to_email_file.html'
    predicted_label = classify_email(email_file_path)

    print("Email Classification:")
    print(f"File: {email_file_path}")
    print(f"Predicted Label: {predicted_label}")
