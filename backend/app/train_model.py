
import joblib
from pathlib import Path

from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report


# 1. Memuat dataset Iris
iris = load_iris()

X = iris.data
y = iris.target

# 2. Membagi data training dan testing
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# 3. Membuat model Random Forest
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# 4. Melatih model
model.fit(X_train, y_train)

# 5. Menguji model
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("=== IRIS CLASSIFICATION MODEL ===")
print(f"Jumlah data: {len(X)}")
print(f"Data training: {len(X_train)}")
print(f"Data testing: {len(X_test)}")
print(f"Akurasi model: {accuracy:.2%}")

print("\nClassification Report:")
print(classification_report(
    y_test,
    y_pred,
    target_names=iris.target_names
))

# 6. Menyimpan model
output_path = Path(__file__).parent / "iris_model.joblib"

joblib.dump(
    {
        "model": model,
        "target_names": iris.target_names.tolist(),
        "feature_names": iris.feature_names
    },
    output_path
)

print(f"\nModel berhasil disimpan: {output_path}")
