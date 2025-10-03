import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="test_bd_1",  
    user="postgres",          
    password="sa123456",      
    port="5432"
)

cur = conn.cursor()

table_name = "slabs"

cur.execute(f"SELECT * FROM {table_name}")
rows = cur.fetchall()

print(f"Данные из таблицы {table_name}:")
for row in rows:
    print(row)
