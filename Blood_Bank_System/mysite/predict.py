import pickle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
import pandas as pd

def load_model(model_path):
  try:
    with open(model_path, 'rb') as f:
      model = pickle.load(f)
    return model
  except FileNotFoundError:
    raise FileNotFoundError(f"Model file not found at: {model_path}")


# Function to predict blood donation based on donor data
def predict_donation(donor_data):
  model = load_model("/home/kali/Public/school_project/ML_model/blood_donation_model.pkl")
  data_df = pd.DataFrame([donor_data])
  prediction_proba = model.predict_proba(data_df)[0][1]
  return prediction_proba


# # Example usage (replace with your actual donor data)
# donor_data = {
#     'Recency (months)': 0,
#     'Frequency (times)': 2,
#     'Time (months)': 12,
#     'money': 12500,
# }

# prediction_proba = predict_donation(donor_data)
# print(f"Predicted probability of donation: {prediction_proba:.2f}")
