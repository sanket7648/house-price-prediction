import os
import joblib
import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

def main():
    print("🚀 Starting Professional ML Training Pipeline...")

    # 1. Ensure output directory exists
    model_dir = '../models'
    os.makedirs(model_dir, exist_ok=True)

    # 2. Load Dataset
    print("📦 Loading California Housing Dataset...")
    data = fetch_california_housing()
    X = pd.DataFrame(data.data, columns=data.feature_names)
    y = data.target

    # 3. Train-Test Split (80% training, 20% testing)
    print("✂️ Splitting data into training and testing sets...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 4. Build the Pipeline
    # This bundles our scaler and model together. 
    # When we use this in the backend, it will automatically scale the user's input before predicting.
    print("🏗️ Building the preprocessing and modeling pipeline...")
    pipeline = Pipeline(steps=[
        ('scaler', StandardScaler()),
        ('model', RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42))
    ])

    # 5. Train the Model
    print("🧠 Training the Random Forest model (this may take a few seconds)...")
    pipeline.fit(X_train, y_train)

    # 6. Evaluate Performance
    print("📊 Evaluating model performance...")
    predictions = pipeline.predict(X_test)
    
    # Calculate metrics
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    
    print("\n--- Model Metrics ---")
    print(f"Mean Absolute Error (MAE): ${mae * 100000:,.2f}")
    print(f"R-squared Score (Accuracy): {r2:.4f}")
    print("---------------------\n")

    # 7. Save the Pipeline
    model_path = os.path.join(model_dir, 'house_price_pipeline.pkl')
    print(f"💾 Saving the full pipeline to {model_path}...")
    joblib.dump(pipeline, model_path)
    
    # Save feature names for backend validation later
    feature_path = os.path.join(model_dir, 'feature_names.pkl')
    joblib.dump(data.feature_names, feature_path)

    print("✅ Pipeline execution complete!")

if __name__ == "__main__":
    main()