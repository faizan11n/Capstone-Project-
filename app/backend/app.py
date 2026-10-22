import os
import socket
import time
import json
import pymysql
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_HOST = os.environ.get("DB_HOST", "db")
DB_USER = os.environ.get("DB_USER", "demouser")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "demopass123")
DB_NAME = os.environ.get("DB_NAME", "goldenbun")

# Set at image build time by the CI pipeline (see Dockerfile)
APP_VERSION = os.environ.get("APP_VERSION", "dev")
GIT_SHA = os.environ.get("GIT_SHA", "local")
STARTED_AT = time.time()

MENU = [
    {"id": 1, "name": "Classic Cheeseburger", "category": "Burgers", "price": 5.49, "emoji": "🍔"},
    {"id": 2, "name": "Double Bacon Deluxe", "category": "Burgers", "price": 7.99, "emoji": "🥓"},
    {"id": 3, "name": "Crispy Chicken Burger", "category": "Burgers", "price": 6.49, "emoji": "🍗"},
    {"id": 4, "name": "Golden Fries", "category": "Sides", "price": 2.99, "emoji": "🍟"},
    {"id": 5, "name": "Onion Rings", "category": "Sides", "price": 3.49, "emoji": "🧅"},
    {"id": 6, "name": "Cola", "category": "Drinks", "price": 1.99, "emoji": "🥤"},
    {"id": 7, "name": "Vanilla Shake", "category": "Drinks", "price": 3.99, "emoji": "🍦"},
    {"id": 8, "name": "Apple Pie", "category": "Desserts", "price": 2.49, "emoji": "🥧"},
]


def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
    )


def wait_for_db_and_init():
    for attempt in range(20):
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS orders (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        customer_name VARCHAR(100) NOT NULL,
                        items JSON NOT NULL,
                        total DECIMAL(10,2) NOT NULL,
                        status VARCHAR(20) DEFAULT 'Received',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            conn.commit()
            conn.close()
            print("Database ready.")
            return
        except Exception as e:
            print(f"Waiting for database... ({attempt + 1}/20) - {e}")
            time.sleep(3)
    raise Exception("Could not connect to database.")


@app.route("/api/menu", methods=["GET"])
def get_menu():
    return jsonify(MENU)


@app.route("/api/order", methods=["POST"])
def place_order():
    data = request.get_json()
    customer_name = data.get("customer_name", "Guest").strip() or "Guest"
    items = data.get("items", [])
    total = sum(item["price"] * item["quantity"] for item in items)

    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO orders (customer_name, items, total) VALUES (%s, %s, %s)",
            (customer_name, json.dumps(items), total),
        )
        order_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({"order_id": order_id, "total": total, "status": "Received"}), 201


@app.route("/api/orders", methods=["GET"])
def get_orders():
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 20")
        orders = cursor.fetchall()
    conn.close()
    for order in orders:
        order["items"] = json.loads(order["items"])
        order["created_at"] = str(order["created_at"])
        order["total"] = float(order["total"])
    return jsonify(orders)


@app.route("/api/info", methods=["GET"])
def info():
    """Shows which build is live. Used by the /devops.html dashboard."""
    return jsonify({
        "version": APP_VERSION,
        "git_sha": GIT_SHA,
        "pod": socket.gethostname(),
        "uptime_seconds": int(time.time() - STARTED_AT),
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "backend ok"})


if __name__ == "__main__":
    wait_for_db_and_init()
    app.run(host="0.0.0.0", port=5000)
