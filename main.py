from sklearn.utils import resample
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
import os
import re
from bs4 import BeautifulSoup
from collections import Counter


def extract_text_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator=' ')
    # Remove extra whitespaces and newlines
    clean_text = re.sub('\s+', ' ', text).strip()
    return clean_text


def extract_features(text):
    features = {
        'contains_greeting': bool(re.search(r'\b(hi|hello|dear|ciao|salve|gentile)\b', text, re.IGNORECASE)),
        'contains_signature': bool(re.search(r'\b(best regards|sincerely|thank you|cordiali saluti|distinti saluti|grazie)\b', text, re.IGNORECASE)),
        'contains_attachment': bool(re.search(r'\b(attachment|attached|see attached|allegato|allegati|vedi allegato)\b', text, re.IGNORECASE)),
        'contains_specific_keyword': bool(re.search(r'\b(refund|confirmation|invoice|receipt|survey|rimborso|conferma|fattura|ricevuta|sondaggio)\b', text, re.IGNORECASE)),
        'contains_language_specific_phrases': bool(
            re.search(r'\b(automated message|system generated|do not reply|this email was sent automatically|messaggio automatico|generato automaticamente|non rispondere|questa email è stata inviata automaticamente)\b',
                      text, re.IGNORECASE)),
        'contains_urgency_phrases': bool(re.search(r'\b(urgent|as soon as possible|reply by|deadline|time-sensitive|urgente|al più presto|rispondere entro|scadenza|tempo sensibile)\b', text, re.IGNORECASE)),
        'contains_customer_specific_info': bool(re.search(r'\b(customer name|account number|order details|membership|nome del cliente|numero di conto|dettagli dell\'ordine|membri)\b', text, re.IGNORECASE))
    }
    return features


if __name__ == '__main__':
    # Load training data
    automated_emails_dir = 'data/1. automated'
    human_emails_dir = 'data/2. human'

    automated_emails = []
    for filename in os.listdir(automated_emails_dir):
        with open(os.path.join(automated_emails_dir, filename), 'r', encoding='utf-8') as file:
            html = file.read()
            text = extract_text_from_html(html)
            automated_emails.append((text, 'automated'))

    human_emails = []
    for filename in os.listdir(human_emails_dir):
        with open(os.path.join(human_emails_dir, filename), 'r', encoding='utf-8') as file:
            html = file.read()
            text = extract_text_from_html(html)
            human_emails.append((text, 'human'))

    # Check the class distribution
    class_distribution = Counter([label for _, label in automated_emails + human_emails])
    print("Original Class Distribution:", class_distribution)

    # Oversample the minority class
    max_class_count = max(class_distribution.values())
    if class_distribution['human'] > class_distribution['automated']:
        automated_emails_resampled = resample(automated_emails, replace=True, n_samples=max_class_count, random_state=42)
        balanced_emails = automated_emails_resampled + human_emails
    else:
        human_emails_resampled = resample(human_emails, replace=True, n_samples=max_class_count, random_state=42)
        balanced_emails = automated_emails + human_emails_resampled

    # Check the class distribution after oversampling
    class_distribution = Counter([label for _, label in balanced_emails])
    print("Class Distribution after Oversampling:", class_distribution)

    # Prepare training and test data
    balanced_texts = [text for text, _ in balanced_emails]
    balanced_labels = [label for _, label in balanced_emails]
    text_train, text_test, label_train, label_test = train_test_split(balanced_texts, balanced_labels, test_size=0.2, stratify=balanced_labels, random_state=42)

    # Create a pipeline with TF-IDF vectorization and SVM classifier
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('svm', SVC())
    ])

    # Train the pipeline
    pipeline.fit(text_train, label_train)

    # Test the pipeline
    predicted_labels = pipeline.predict(text_test)

    # Compute evaluation metrics
    accuracy = accuracy_score(label_test, predicted_labels)
    precision = precision_score(label_test, predicted_labels, pos_label='automated')
    recall = recall_score(label_test, predicted_labels, pos_label='automated')
    f1 = f1_score(label_test, predicted_labels, pos_label='automated')
    classification_report_output = classification_report(label_test, predicted_labels)

    # Print evaluation metrics
    print(f"Accuracy: {accuracy}")
    print(f"Precision: {precision}")
    print(f"Recall: {recall}")
    print(f"F1-Score: {f1}")
    print(f"\nClassification Report:\n{classification_report_output}")

    # Print examples and classifications
    print("Examples from the Test Set:")
    for text, label, predicted_label in zip(text_test[:5], label_test[:5], predicted_labels[:5]):
        print(f"Text: {text}")
        print(f"True Label: {label}")
        print(f"Predicted Label: {predicted_label}")
        print("-----------------------")
