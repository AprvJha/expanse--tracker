"""Quick diagnostic to test the anomaly pipeline locally."""
import asyncio
import os
import traceback

# Load env
from dotenv import load_dotenv
load_dotenv()

from app.core.database import get_database
from ml.anomaly.detector import detect_anomalies, get_anomaly_metrics
from ml.anomaly.isolation_forest import train_isolation_forest
from ml.insights.patterns import to_dataframe

USER_ID = "69fc6462acc4b24f3c15fbb6"

async def main():
    db = get_database()

    # Step 1: fetch expenses
    print("=" * 60)
    print("  Step 1: Fetching expenses from DB")
    print("=" * 60)
    cursor = db["expenses"].find(
        {"user_id": USER_ID},
        {"_id": 0, "merchant": 1, "amount": 1, "category": 1,
         "date": 1, "is_anomaly": 1}
    )
    expenses = await cursor.to_list(length=10000)
    print(f"Found {len(expenses)} expenses")
    if expenses:
        print(f"Sample: {expenses[0]}")
    else:
        print("NO DATA — check user_id format in DB")
        return

    # Step 2: to_dataframe
    print("\n" + "=" * 60)
    print("  Step 2: Converting to DataFrame")
    print("=" * 60)
    try:
        df = to_dataframe(expenses)
        print(f"DataFrame shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        print(f"dtypes:\n{df.dtypes}")
    except Exception:
        traceback.print_exc()
        return

    # Step 3: detect_anomalies
    print("\n" + "=" * 60)
    print("  Step 3: Running detect_anomalies()")
    print("=" * 60)
    try:
        alerts = detect_anomalies(expenses)
        print(f"Anomalies detected: {len(alerts)}")
        if alerts:
            print(f"First alert: {alerts[0]}")
    except Exception:
        traceback.print_exc()

    # Step 4: get_anomaly_metrics
    print("\n" + "=" * 60)
    print("  Step 4: Running get_anomaly_metrics()")
    print("=" * 60)
    try:
        metrics = get_anomaly_metrics(expenses)
        print(f"Metrics: {metrics}")
    except Exception:
        traceback.print_exc()

    # Step 5: train
    print("\n" + "=" * 60)
    print("  Step 5: Training Isolation Forest")
    print("=" * 60)
    try:
        if len(df) < 50:
            print(f"Only {len(df)} rows — need at least 50 to train")
        else:
            train_isolation_forest(df)
            print("Training succeeded!")
    except Exception:
        traceback.print_exc()


asyncio.run(main())
