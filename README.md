# Process Emails
A simple script with the following functions:
- extracting clean text out of HTML emails
- extracting name and surname or company name
- classifying if it’s human or automated
 

# Requirements 
pip3 install -U scikit-learn
pip3 install bs4


# Run
To use the code, follow these steps:

## Optional: Train the classifier
1. Put a data folder inside the root of the project with two subfolders "1. automated" and "2. human"
1. Run the train.py script to train and save the model as "email_classification_model.joblib".
   `python3 train.py`

## Classify an email
3. Place the email file that you want to classify inside the root and update the email_file_path variable in the second script with the path to that file.
4. Run the predict.py script to classify the email.
   `python3 predict.py`
