import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="test_bd_1",  
    user="postgres",          
    password="postgres",      
    port="5432"
)

cur = conn.cursor()

Scada_table = "slabs"

cur.execute("SELECT * FROM slabs ORDER BY id DESC LIMIT 1")


last_row = cur.fetchone()

    
id, Length_slab, Width_slab, Thikness_slab, Temperature_slab, Material_slab,Diametr_roll, Material_roll = last_row
    
    
print("Последняя запись из таблицы:")
print(f"ID: {id}")
print(f"Колонка 2: {Length_slab.replace(' ', '')}")
print(f"Колонка 3: {Width_slab.replace(' ', '')}")
print(f"Колонка 4: {Thikness_slab.replace(' ', '')}")
print(f"Колонка 5: {Temperature_slab.replace(' ', '')}")
print(f"Колонка 6: {Material_slab.replace(' ', '')}")
print(f"Колонка 7: {Diametr_roll.replace(' ', '')}")
print(f"Колонка 8: {Material_roll}")

