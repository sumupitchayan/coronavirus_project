import pandas as pd 

import sqlite3
conn = sqlite3.connect("data/data.db")

df = pd.read_sql_query("SELECT * FROM virus_data JOIN environment ON location == city LIMIT 100;", conn)

df.to_csv(r'/Users/Snigdha/Downloads/coronavirus_project/sample_data.csv', index = False)