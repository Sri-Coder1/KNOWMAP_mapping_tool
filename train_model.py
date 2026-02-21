import pandas as pd
import matplotlib.pyplot as plt
import joblib

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve
)

# ==============================
# 1. Load Processed Dataset
# ==============================

df = pd.read_csv("dataset/cardio_train_processed.csv")

# Separate features and target
X = df.drop("cardio", axis=1)
y = df["cardio"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ==============================
# 2. Logistic Regression Model
# ==============================

print("\n===== Logistic Regression =====")

log_model = LogisticRegression(max_iter=1000)
log_model.fit(X_train, y_train)

y_pred_log = log_model.predict(X_test)
y_prob_log = log_model.predict_proba(X_test)[:, 1]

print("Accuracy:", accuracy_score(y_test, y_pred_log))
print("Classification Report:\n", classification_report(y_test, y_pred_log))

print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred_log))

auc_log = roc_auc_score(y_test, y_prob_log)
print("ROC-AUC Score:", auc_log)

# ROC Curve
fpr_log, tpr_log, _ = roc_curve(y_test, y_prob_log)

plt.figure()
plt.plot(fpr_log, tpr_log)
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve - Logistic Regression")
plt.show()


# ==============================
# 3. Random Forest Model
# ==============================

print("\n===== Random Forest =====")

rf_model = RandomForestClassifier(random_state=42)
rf_model.fit(X_train, y_train)

y_pred_rf = rf_model.predict(X_test)
y_prob_rf = rf_model.predict_proba(X_test)[:, 1]

print("Accuracy:", accuracy_score(y_test, y_pred_rf))
print("Classification Report:\n", classification_report(y_test, y_pred_rf))

print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred_rf))

auc_rf = roc_auc_score(y_test, y_prob_rf)
print("ROC-AUC Score:", auc_rf)

# ROC Curve
fpr_rf, tpr_rf, _ = roc_curve(y_test, y_prob_rf)

plt.figure()
plt.plot(fpr_rf, tpr_rf)
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve - Random Forest")
plt.show()


# ==============================
# 4. Feature Importance (RF)
# ==============================

importance = pd.Series(
    rf_model.feature_importances_,
    index=X.columns
).sort_values(ascending=False)

print("\nFeature Importance:\n")
print(importance)


# ==============================
# 5. Save Best Model
# ==============================

# Choose better model based on ROC-AUC
if auc_rf > auc_log:
    best_model = rf_model
    print("\nRandom Forest selected as best model.")
else:
    best_model = log_model
    print("\nLogistic Regression selected as best model.")

joblib.dump(best_model, "cardio_model.pkl")
print("Best model saved as cardio_model.pkl")
