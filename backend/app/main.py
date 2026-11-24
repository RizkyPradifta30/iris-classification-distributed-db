
import joblib
import numpy as np
from app.auth import verify_token
from fastapi import FastAPI, HTTPException, Depends

from pathlib import Path
from fastapi import FastAPI, HTTPException

from app.schemas import IrisInput, IrisPrediction
from app.database import (
    get_primary_connection,
    get_replica_connection
)


# Memuat model Machine Learning
MODEL_PATH = Path(__file__).parent / "iris_model.joblib"
model_data = joblib.load(MODEL_PATH)

model = model_data["model"]
target_names = model_data["target_names"]


app = FastAPI(
    title="Iris Classification API",
    description="Distributed Database and ML Integration",
    version="2.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Iris Classification API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model": "Random Forest"
    }


@app.get("/health/db")
def database_health():

    result = {}

    for name, connection_function in [
        ("primary", get_primary_connection),
        ("replica", get_replica_connection)
    ]:
        try:
            with connection_function() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    cur.fetchone()

            result[name] = "connected"

        except Exception as e:
            result[name] = f"error: {str(e)}"

    return result


@app.get("/model-info")
def model_info():
    return {
        "algorithm": "Random Forest Classifier",
        "classes": target_names
    }


# WRITE ROUTING: Menyimpan prediksi ke Primary
@app.post("/predict", response_model=IrisPrediction)
def predict(
    data: IrisInput,
    user: dict = Depends(verify_token)
):

    features = np.array([[
        data.sepal_length,
        data.sepal_width,
        data.petal_length,
        data.petal_width
    ]])

    prediction = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]

    prediction_name = target_names[prediction]
    confidence = float(max(probabilities))

    try:
        with get_primary_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO predictions (
                        sepal_length,
                        sepal_width,
                        petal_length,
                        petal_width,
                        prediction,
                        confidence
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        data.sepal_length,
                        data.sepal_width,
                        data.petal_length,
                        data.petal_width,
                        prediction_name,
                        confidence
                    )
                )

                prediction_id = cur.fetchone()[0]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save prediction: {str(e)}"
        )

    return {
        "prediction": prediction_name,
        "confidence": round(confidence, 4)
    }


# READ ROUTING: Membaca riwayat dari Replica
@app.get("/predictions")
def get_predictions(
    user: dict = Depends(verify_token)
):

    try:
        with get_replica_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        id,
                        sepal_length,
                        sepal_width,
                        petal_length,
                        petal_width,
                        prediction,
                        confidence,
                        created_at
                    FROM predictions
                    ORDER BY id DESC
                    """
                )

                rows = cur.fetchall()

                columns = [
                    "id",
                    "sepal_length",
                    "sepal_width",
                    "petal_length",
                    "petal_width",
                    "prediction",
                    "confidence",
                    "created_at"
                ]

                return [
                    dict(zip(columns, row))
                    for row in rows
                ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read predictions: {str(e)}"
        )
