import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib

def train_symptiq_model():
    print("Step 1: Loading the dataset...")
    try:
        # Read the CSV file. 
        df = pd.read_csv('MLDataset_SymptiQ.csv')
    except FileNotFoundError:
        print("ERROR: Could not find 'MLDataset_SymptiQ.csv'. Make sure it is in the same folder as this script!")
        return

    # Clean the data: We only want the first two columns. 
    # Excel sometimes adds invisible empty columns/rows, so we drop any missing data to prevent crashes.
    df = df[['User Input Text (Features)', 'Target_Disease (Label)']].dropna()

    # Separate our inputs (Symptoms) and our expected outputs (Disease)
    X_text = df['User Input Text (Features)']
    y_labels = df['Target_Disease (Label)']

    print(f"Successfully loaded {len(df)} symptom examples.")

    print("Step 2: Converting text to numbers (Vectorization)...")
    # Computers can't read English, so TfidfVectorizer turns the text into a mathematical grid.
    # stop_words='english' tells it to ignore useless words like "the", "and", "I", "have".
    vectorizer = TfidfVectorizer(stop_words='english')
    X_numbers = vectorizer.fit_transform(X_text)

    print("Step 3: Training the AI Model...")
    # Multinomial Naive Bayes is an incredibly fast, lightweight algorithm perfect for text classification.
    model = MultinomialNB()
    model.fit(X_numbers, y_labels)

    print("Step 4: Saving the brain to files...")
    # We save both the model AND the vectorizer. The main app needs the exact same 
    # vectorizer to translate the user's input the exact same way later.
    joblib.dump(model, 'model.pkl')
    joblib.dump(vectorizer, 'vectorizer.pkl')

    print("==================================================")
    print("SUCCESS! Training Complete.")
    print("==================================================")

if __name__ == "__main__":
    train_symptiq_model()