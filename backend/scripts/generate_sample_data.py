import asyncio
import random
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import MONGODB_URL

TARGET_ROWS = 1200
MONTHS_BACK = 6
USER_ID = "69fc6462acc4b24f3c15fbb6"

MERCHANTS = {
    "Food": [
        ("Swiggy", 80, 600),
        ("Zomato", 80, 700),
        ("Dominos", 150, 500),
        ("McDonalds", 100, 400),
        ("Starbucks", 200, 600),
        ("Cafe Coffee Day", 100, 300),
        ("Burger King", 100, 350),
        ("Subway", 150, 400),
        ("Local Restaurant", 60, 300),
    ],
    "Transport": [
        ("Uber", 40, 400),
        ("Ola", 40, 350),
        ("Rapido", 30, 150),
        ("Metro Recharge", 100, 500),
        ("Petrol Pump", 500, 3000),
        ("Bus Ticket", 20, 100),
    ],
    "Shopping": [
        ("Amazon", 200, 5000),
        ("Flipkart", 200, 4000),
        ("Myntra", 300, 3000),
        ("H&M", 500, 4000),
        ("Zara", 800, 6000),
        ("DMart", 500, 3000),
        ("Reliance Fresh", 200, 1500),
        ("Big Bazaar", 300, 2000),
    ],
    "Subscription": [
        ("Netflix", 199, 199),
        ("Spotify", 119, 119),
        ("Amazon Prime", 299, 299),
        ("Hotstar", 299, 299),
        ("YouTube Premium", 139, 139),
    ],
    "Utilities": [
        ("Airtel Postpaid", 400, 999),
        ("Jio Recharge", 199, 666),
        ("Electricity Bill", 800, 3000),
        ("Water Bill", 200, 600),
        ("Gas Bill", 400, 900),
        ("Broadband", 500, 1500),
    ],
    "Health": [
        ("Apollo Pharmacy", 100, 2000),
        ("Cult Fit", 500, 2500),
        ("Medplus", 100, 1500),
        ("Practo Consultation", 299, 999),
        ("Gym Membership", 800, 2500),
    ],
    "Entertainment": [
        ("PVR Cinemas", 200, 800),
        ("BookMyShow", 200, 1200),
        ("Bowling Alley", 300, 800),
        ("Escape Room", 500, 1500),
    ],
}

ANOMALIES = [
    {"merchant": "Restaurant XYZ", "category": "Food",          "amount": 4800.0},
    {"merchant": "Apple Store",    "category": "Shopping",       "amount": 89000.0},
    {"merchant": "Uber Outstation","category": "Transport",      "amount": 6200.0},
    {"merchant": "Hospital Bill",  "category": "Health",         "amount": 45000.0},
    {"merchant": "Amazon Laptop",  "category": "Shopping",       "amount": 72000.0},
    {"merchant": "Party Supplies", "category": "Entertainment",  "amount": 12000.0},
]

def get_amount(merchant_data, date):
    name, lo, hi = merchant_data

    if lo == hi:
        return float(lo)

    amount = random.uniform(lo, hi)

    if date.weekday() >= 5:
        amount *= random.uniform(1.4, 2.0)

    if date.day >= 28:
        amount *= random.uniform(1.2, 1.5)

    if date.day <= 3:
        amount *= random.uniform(1.1, 1.4)

    return round(amount, 2)


def get_category_weights(date):
    if date.weekday() >= 5:
        return {
            "Food": 30,
            "Entertainment": 15,
            "Shopping": 20,
            "Transport": 10,
            "Subscription": 5,
            "Utilities": 5,
            "Health": 15,
        }
    else:
        return {
            "Food": 25,
            "Transport": 25,
            "Shopping": 15,
            "Subscription": 10,
            "Utilities": 10,
            "Health": 10,
            "Entertainment": 5,
        }


def pick_category(date):
    weights = get_category_weights(date)
    categories = list(weights.keys())
    probabilities = [weights[c] for c in categories]
    return random.choices(categories, weights=probabilities, k=1)[0]


def generate_transactions():
    transactions = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=MONTHS_BACK * 30)

    for _ in range(TARGET_ROWS - len(ANOMALIES)):
        days_range = (end_date - start_date).days
        random_days = random.randint(0, days_range)
        date = start_date + timedelta(days=random_days)
        date = date.replace(
            hour=random.randint(7, 23),
            minute=random.randint(0, 59)
        )

        category = pick_category(date)
        merchant_data = random.choice(MERCHANTS[category])
        amount = get_amount(merchant_data, date)

        transactions.append({
            "user_id": USER_ID,
            "merchant": merchant_data[0],
            "category": category,
            "amount": amount,
            "date": date,
            "description": f"{merchant_data[0]} payment",
            "payment_method": random.choice(["UPI", "Credit Card", "Debit Card", "Net Banking"]),
            "is_anomaly": False,
            "source": "generated",
            "created_at": datetime.now(),
        })

    subscription_day = 1
    for month_offset in range(MONTHS_BACK):
        for sub_name, lo, hi in MERCHANTS["Subscription"]:
            date = end_date.replace(day=subscription_day) - timedelta(days=month_offset * 30)
            transactions.append({
                "user_id": USER_ID,
                "merchant": sub_name,
                "category": "Subscription",
                "amount": float(lo),
                "date": date,
                "description": f"{sub_name} monthly subscription",
                "payment_method": "Credit Card",
                "is_anomaly": False,
                "source": "generated",
                "created_at": datetime.now(),
            })

    for anomaly in ANOMALIES:
        random_days = random.randint(0, (end_date - start_date).days)
        date = start_date + timedelta(days=random_days)
        transactions.append({
            "user_id": USER_ID,
            "merchant": anomaly["merchant"],
            "category": anomaly["category"],
            "amount": anomaly["amount"],
            "date": date,
            "description": f"ANOMALY: {anomaly['merchant']}",
            "payment_method": random.choice(["Credit Card", "UPI"]),
            "is_anomaly": True,
            "source": "generated",
            "created_at": datetime.now(),
        })

    transactions.sort(key=lambda x: x["date"])
    return transactions


async def main():
    print("Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client["expense_db"]
    collection = db["expenses"]

    deleted = await collection.delete_many({"source": "generated"})
    print(f"Cleared {deleted.deleted_count} existing generated records")

    print("Generating transactions...")
    transactions = generate_transactions()
    print(f"Generated {len(transactions)} transactions")

    result = await collection.insert_many(transactions)
    print(f"[OK] Inserted {len(result.inserted_ids)} transactions into MongoDB")

    print("\n-- Summary ----------------------------------")
    pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}, "total": {"$sum": "$amount"}}},
        {"$sort": {"count": -1}}
    ]
    async for doc in collection.aggregate(pipeline):
        print(f"  {doc['_id']:<15} {doc['count']:>4} transactions   Rs.{doc['total']:>10,.2f}")

    anomaly_count = await collection.count_documents({"is_anomaly": True})
    print(f"\n  Anomalies labeled: {anomaly_count}")
    print(f"  Total in DB: {len(result.inserted_ids)}")
    print("-------------------------------------")

    client.close()

if __name__ == "__main__":
    asyncio.run(main())