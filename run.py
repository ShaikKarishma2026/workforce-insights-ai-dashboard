"""
Top-Level Launcher for Workforce Insights & AI Skills Analytics Platform
Runs verification, builds all assets, and starts the FastAPI server.
"""

import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

def bootstrap():
    print("=" * 70)
    print("   NEXUSHR: WORKFORCE INSIGHTS & AI SKILLS ANALYTICS PLATFORM")
    print("=" * 70)

    raw_csv = PROJECT_ROOT / "dataset" / "dataset_raw.csv"
    if not raw_csv.exists():
        print("[1/5] Generating raw synthetic workforce dataset...")
        from dataset.generate_dataset import generate_raw_dataset
        generate_raw_dataset(raw_csv)
    else:
        print("[1/5] Raw workforce dataset found.")

    cleaned_csv = PROJECT_ROOT / "dataset" / "dataset_cleaned.csv"
    report_json = PROJECT_ROOT / "dataset" / "cleaning_report.json"
    if not cleaned_csv.exists():
        print("[2/5] Running data cleaning & preprocessing pipeline...")
        from dataset.clean_preprocess import clean_and_preprocess_workforce_data
        clean_and_preprocess_workforce_data(raw_csv, cleaned_csv, report_json)
    else:
        print("[2/5] Cleaned workforce dataset verified.")

    db_file = PROJECT_ROOT / "database" / "workforce.db"
    if not db_file.exists():
        print("[3/5] Initializing relational database & executing schema...")
        from database.db_setup import initialize_database
        initialize_database()
    else:
        print("[3/5] Relational database ready.")

    charts_dir = PROJECT_ROOT / "eda" / "charts"
    if not list(charts_dir.glob("*.png")):
        print("[4/5] Pre-generating 10 high-resolution EDA visualizations...")
        from eda.eda_analysis import run_eda
        run_eda()
    else:
        print("[4/5] EDA charts and insights ready.")

    model_file = PROJECT_ROOT / "machine_learning" / "attrition_model.joblib"
    if not model_file.exists():
        print("[5/5] Training Machine Learning models and benchmarks...")
        from machine_learning.train_models import run_all_ml_training
        run_all_ml_training()
    else:
        print("[5/5] Machine Learning models verified.")

    print("\nPre-warming RAG Vector Store & semantic index...")
    from rag.vector_store import get_vector_store
    get_vector_store()

    print("\n" + "=" * 70)
    print(" All systems operational! Starting FastAPI backend server...")
    print(" Dashboard URL: http://127.0.0.1:8000")
    print(" API Documentation: http://127.0.0.1:8000/docs")
    print("=" * 70 + "\n")

    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False, log_level="info")

if __name__ == "__main__":
    bootstrap()
