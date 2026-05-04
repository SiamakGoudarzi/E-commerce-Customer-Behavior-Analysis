"""
E-commerce Customer Behavior Analysis
Author: Siamak Goudarzi

This project demonstrates:
- Data cleaning on a raw CSV dataset
- Object-oriented customer modeling
- Callback-based filtering
- Exploratory Data Analysis (EDA)
- Professional visualizations using matplotlib

This script is designed as a clean, simple, and professional
Data Analyst portfolio project without any AI components.
"""

import csv
import logging
from typing import Callable, List
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


# ---------------------------------------------------------
# 1. DATA CLEANING
# ---------------------------------------------------------

def clean_data(csv_path: str) -> str:
    """Load, clean, and save a processed version of the dataset."""
    df = pd.read_csv(csv_path)

    # Remove duplicates
    df = df.drop_duplicates()

    # Remove missing values
    df = df.dropna()

    # Convert data types
    df["Age"] = df["Age"].astype(int)
    df["Customer_Rating"] = df["Customer_Rating"].astype(int)
    df["Total_Amount"] = df["Total_Amount"].astype(float)

   # Robust boolean conversion for sustainability
    df["Is_Returning_Customer"] = df["Is_Returning_Customer"].apply(
        lambda x: str(x).strip().lower() == 'true'
    )

    # Remove invalid values
    df = df[df["Age"] > 0]
    df = df[df["Total_Amount"] >= 0]

    # Remove extreme outliers (top 1%)
    df = df[df["Total_Amount"] < df["Total_Amount"].quantile(0.99)]

    cleaned_path = "cleaned_data.csv"
    df.to_csv(cleaned_path, index=False)

    logging.info(f"Cleaned dataset saved as: {cleaned_path}")
    return cleaned_path


# ---------------------------------------------------------
# 2. CUSTOMER CLASS
# ---------------------------------------------------------

class Customer:
    """Represents a single customer entry from the dataset."""

    def __init__(self, data: dict):
        self.order_id = data['Order_ID']
        self.customer_id = data['Customer_ID']
        self.age = int(data['Age'])
        self.gender = data['Gender']
        self.city = data['City']
        self.total_amount = float(data['Total_Amount'])
        self.is_returning = data['Is_Returning_Customer'] in ["True", True]
        self.rating = int(data['Customer_Rating'])

    def __str__(self) -> str:
        return f"[{self.customer_id}] {self.city} | Age: {self.age} | Spend: €{self.total_amount:.2f}"

    def __repr__(self) -> str:
        return f"<Customer {self.customer_id}>"


# ---------------------------------------------------------
# 3. ANALYZER CLASS
# ---------------------------------------------------------

class ChurnAnalyzer:
    """Loads customers, applies filters, and generates statistics."""

    def __init__(self, csv_file: str):
        self.csv_file = csv_file
        self.customers: List[Customer] = []
        self._load_data()

    def _load_data(self):
        try:
            with open(self.csv_file, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.customers.append(Customer(row))

            logging.info(f"{len(self.customers)} customers loaded.")

        except Exception as e:
            logging.error(f"Error loading data: {e}")

    def filter_data(self, callback: Callable[[Customer], bool]) -> List[Customer]:
        return [c for c in self.customers if callback(c)]

    def get_stats(self) -> dict:
        total = len(self.customers)
        returning = len([c for c in self.customers if c.is_returning])
        avg_amount = np.mean([c.total_amount for c in self.customers])

        return {
            "total_customers": total,
            "returning_customers": returning,
            "new_customers": total - returning,
            "average_spending": round(avg_amount, 2)
        }


# ---------------------------------------------------------
# 4. EDA (Exploratory Data Analysis)
# ---------------------------------------------------------

def run_eda(customers: List[Customer]):
    ages = [c.age for c in customers]
    amounts = [c.total_amount for c in customers]
    ratings = [c.rating for c in customers]

    print("\n--- Exploratory Data Analysis (EDA) ---")
    print(f"Average Age: {np.mean(ages):.2f}")
    print(f"Median Age: {np.median(ages):.2f}")
    print(f"Average Spending: {np.mean(amounts):.2f}")
    print(f"Median Spending: {np.median(amounts):.2f}")
    print(f"Average Rating: {np.mean(ratings):.2f}")
    print(f"Min/Max Spending: {min(amounts)} / {max(amounts)}")


# ---------------------------------------------------------
# 5. VISUALIZATIONS
# ---------------------------------------------------------

def plot_loyalty_pie(customers):
    returning = len([c for c in customers if c.is_returning])
    new_customers = len(customers) - returning

    plt.figure(figsize=(8, 6))
    plt.pie(
        [returning, new_customers],
        labels=["Returning", "New"],
        autopct="%1.1f%%",
        explode=(0.1, 0),
        colors=["#4CAF50", "#FF5722"]
    )
    plt.title("Customer Loyalty Distribution")
    plt.show()


def plot_age_hist(customers):
    ages = [c.age for c in customers]
    plt.figure(figsize=(8, 6))
    plt.hist(ages, bins=10, color="#9C27B0")
    plt.title("Age Distribution")
    plt.xlabel("Age")
    plt.ylabel("Frequency")
    plt.show()


def plot_spending_box(customers):
    amounts = [c.total_amount for c in customers]
    plt.figure(figsize=(6, 6))
    plt.boxplot(amounts)
    plt.title("Spending Outlier Analysis")
    plt.ylabel("Total Amount (€)")
    plt.show()


def plot_city_spending(customers):
    city_totals = {}
    for c in customers:
        city_totals.setdefault(c.city, 0)
        city_totals[c.city] += c.total_amount

    cities = list(city_totals.keys())
    totals = list(city_totals.values())

    plt.figure(figsize=(10, 6))
    plt.bar(cities, totals, color="#2196F3")
    plt.title("Total Spending by City")
    plt.xlabel("City")
    plt.ylabel("Total Spending (€)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


# ---------------------------------------------------------
# 6. CALLBACK FUNCTIONS
# ---------------------------------------------------------

def get_unhappy_customers(c: Customer) -> bool:
    return c.rating <= 2

def get_high_spenders(c: Customer) -> bool:
    return c.total_amount > 3000


# ---------------------------------------------------------
# 7. MAIN PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":
    raw_path = "ecommerce_customer_behavior_dataset_v2.csv"

    # 1. Clean data
    cleaned_file = clean_data(raw_path)

    # 2. Load cleaned data
    analyzer = ChurnAnalyzer(cleaned_file)

    # 3. Basic statistics
    print("\n--- Basic Statistics ---")
    print(analyzer.get_stats())

    # 4. EDA
    run_eda(analyzer.customers)

    # 5. Show sample customers
    print("\n--- Sample Unhappy Customers ---")
    unhappy = analyzer.filter_data(get_unhappy_customers)
    for c in unhappy[:3]:
        print(c)

    # 6. Visualizations
    plot_loyalty_pie(analyzer.customers)
    plot_age_hist(analyzer.customers)
    plot_spending_box(analyzer.customers)
    plot_city_spending(analyzer.customers)
