import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler


#read dataset
df = pd.read_csv("dataset\cardio_train.csv", sep=';')

#removing id col
if "id" in df.columns:
    df.drop("id", axis=1,inplace=True)

#removing duplicates
df = df.drop_duplicates()
df = df.fillna(df.mean())

df = df[(df["ap_hi"] < 250) & (df["ap_lo"] < 200)]

#converting age to years
df["age"] = df["age"] / 365

df = df.rename(columns={
    "ap_hi": "systolic_bp",
    "ap_lo": "diastolic_bp"
})

scaler = StandardScaler()
numeric_cols = df.drop("cardio", axis=1).columns
df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

plt.figure()
df["cardio"].value_counts().plot(kind="pie", autopct="%1.1f%%", startangle=90)
plt.title("Heart Disease Count")
plt.xlabel("0 = No Disease, 1 = Disease")
plt.ylabel("Count")
plt.show()


df.to_csv("dataset/cardio_train_processed.csv", index=False)

print("Preprocessing completed successfully!")
