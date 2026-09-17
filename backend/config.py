import os
from datetime import timedelta

class Config:
    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # SQLite
    SQLALCHEMY_DATABASE_URI = "sqlite:///do_an.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES  = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

    # Apriori / FP-Growth params
    MIN_SUPPORT    = 0.01
    MIN_CONFIDENCE = 0.3
    MIN_LIFT       = 1.0
    TOP_N_RECOMMEND = 5

    # Paths
    BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR       = os.path.join(BASE_DIR, "data")
    PRECOMPUTED_DIR = os.path.join(BASE_DIR, "precomputed")
    RAW_DATA_PATH     = os.path.join(DATA_DIR, "Assignment-1_Data.csv")
    CLEANED_DATA_PATH = os.path.join(DATA_DIR, "Assignment-1_Data_Cleaned.csv")
    APRIORI_RULES_PATH    = os.path.join(PRECOMPUTED_DIR, "apriori_rules.csv")
    FPGROWTH_RULES_PATH   = os.path.join(PRECOMPUTED_DIR, "fpgrowth_rules.csv")
    SEQUENTIAL_RULES_PATH = os.path.join(PRECOMPUTED_DIR, "sequential_patterns.txt")
