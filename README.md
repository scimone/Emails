# Process Emails
A simple script with the following functions:
- extracting clean text out of HTML emails
- extracting name and surname or company name
- classifying if it’s human or automated
 

# Requirements 
pip3 install -U scikit-learn
pip3 install flask
pip3 install bs4
pip3 install flask


# Run

## Optional: Train the classifier
1. Put a data folder inside the root of the project with two subfolders "1. automated" and "2. human"
2. Run the train.py script to train and save the model as "email_classification_model.joblib":
   `python3 train.py`

## Classify an email
1. Run `flask run` in the main root, that will start a service in `http://127.0.0.1:5000/`
2. Use `[POST] /predict` endpoint to predict new email
