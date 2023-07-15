# Process Emails

A collection of Python scripts designed to streamline various tasks related to managing emails and PDF attachments. 

Key Features:

- Email Text Extraction: Extract clean and formatted text from HTML email files.
- Email Classification: Classify emails as either automated or human-generated using advanced Natural Language Processing (NLP) techniques. The classification model is trained using Support Vector Machines (SVM) and TF-IDF vectorization.
- PDF Extraction: Extract text and other data from PDF attachments.
- PDF Form Auto-fill: Automatically populate PDF form fields with saved user profile data.
 

# Requirements 
```
pip3 install -U scikit-learn
pip3 install flask
pip3 install bs4
pip3 install joblib
pip3 install gunicorn
```

# Run Classifyer

## Optional: Train the classifier with your own data (alternatively, use pretrained model)
1. Put a `data` folder inside the root of the project with two subfolders "1. automated" and "2. human", containing html email data.
2. Run the train.py script to train and save the model as "email_classification_model.joblib":
   `python3 train.py`

## Classify an email
1. Run `flask run` in the main root, that will start a service in `http://127.0.0.1:5000/`
2. Use `[POST] /predict` endpoint to predict new email


# Run Classifyer in production
`gunicorn --bind 127.0.0.1:8001 --workers 3 --bind unix:/home/ubuntu/email-ai-server/app.sock wsgi:app`
