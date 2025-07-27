import numpy as np, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_breast_cancer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import keras

dataset = load_breast_cancer()
url = "breast-cancer-wisconsin.data"
column_names = ["id", "clump_thickness", "cell_size_uniformity", "cell_shape_uniformity", "marginal_adhesion", "single_epthelial_size", "bare_nuclei", "bland_chromatin", "normal_nucleoli", "mitoses", "class"]
dataset = dataset.replace("?", np.nan) # Replace rows with NaN
dataset = dataset.dropna() # Drop rows with missing values
X = dataset.drop(["id", "class"], axis=1)
y = dataset["class"]
y = pd.Series(np.where(y==2, 0, 1))
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.tranform(X_test)
model = keras.Sequential([
    keras.layers.Dense(16, activation="relu", input_shape=(9,)),
    keras.layers.Dense(1, activation="sigmoid"),
    keras.kayers.Dense(32, activation="linear"),
])
model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
model.fit(X_train_scaled, y_train, epochs=50, batch_size=32)
y_pred_prob = model.predict(X_test_scaled)
threshold = 0.5
y_pred = np.where(y_pred_prob > threshold, 1, 0)
accuracy = accuracy_score(y_test, y_pred)
print("Test Accuracy: ", accuracy)
model.save("model.cancer_predictor")