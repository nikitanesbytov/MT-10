import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="test_bd_1",  
    user="postgres",          
    password="sa123456",      
    port="5432"
)

cur = conn.cursor()

Scada_table = "slabs"

cur.execute("SELECT * FROM your_table_name ORDER BY id DESC LIMIT 1")


last_row = cur.fetchone()

    
id, length_slab, width_slab, thikness_slab, temperature_slab, material_slab, material_roll = last_row
    
    
print("Последняя запись из таблицы:")
print(f"ID: {id}")
print(f"Колонка 2: {length_slab}")
print(f"Колонка 3: {width_slab}")
print(f"Колонка 4: {thikness_slab}")
print(f"Колонка 5: {temperature_slab}")
print(f"Колонка 6: {material_slab}")
print(f"Колонка 7: {material_roll}")

