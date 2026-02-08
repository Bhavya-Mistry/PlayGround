import os
import json
import time  # Unused import (Style issue)


def connect_db():
    # SECURITY ISSUE: Hardcoded production secrets
    # The AI should scream about this
    aws_secret = "AKIAIMNOJVGFD1254GHI"
    db_password = "super_secret_password_123!"
    print(f"Connecting with {aws_secret}...")


def get_user_data(user_id):
    # SECURITY ISSUE: SQL Injection
    # Never format strings directly into a query!
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return query


def calculate_heavy_stuff():
    # PERFORMANCE ISSUE: Quadratic complexity
    # This will freeze the CPU for large inputs
    results = []
    for i in range(10000):
        for j in range(10000):
            results.append(i * j)
    return results


def main():
    x = connect_db()
    # QUALITY ISSUE: 'y' is a terrible variable name
    y = get_user_data("1 OR 1=1")
    print(y)
