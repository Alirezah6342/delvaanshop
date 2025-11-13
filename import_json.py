import json
import psycopg2

conn = psycopg2.connect(
    dbname="storedelvan",
    user="django_user",
    password="A@13579hsb",
    host="localhost",   # یا اگر داخل کانتینر اجرا می‌کنی: host="127.0.0.1"
    port="5432"
)
cur = conn.cursor()

with open("/tmp/store_category.json") as f:
    data = json.load(f)
    for row in data:
        cur.execute(
            "INSERT INTO store_category (id, name, slug) VALUES (%s, %s, %s)",
            (row["id"], row["name"], row["slug"])
        )

conn.commit()
cur.close()
conn.close()
print("Data imported successfully!")
