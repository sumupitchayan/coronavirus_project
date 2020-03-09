import requests
import pandas as pd
import sqlite3
from googlemaps import Client as GoogleMaps

TOKEN = '1e50020499453cb7462d5da1ab16c69cb0fb86a7'

GMAPTOKEN = 'AIzaSyCXLcz9z9nFS0WfIstI6pQstTvCha37WkQ'

gmaps = GoogleMaps(GMAPTOKEN)

URL = 'https://api.waqi.info/feed/'

df = pd.read_csv('virus_data.csv')

locations = list(df.location.unique())

conn = sqlite3.connect('data.db')
c = conn.cursor()

c.execute('DROP TABLE IF EXISTS "pollution";')

create_pollution_table_command = '''
CREATE TABLE IF NOT EXISTS pollution (
	location VARCHAR(30) NOT NULL,
	aqi INTEGER NOT NULL,
	PRIMARY KEY (location)
);
'''


c.execute(create_pollution_table_command)

conn.commit()

for loc in range(len(locations)):

    print(locations[loc])

    if type(locations[loc]) == float:
        continue

    geocode_result = gmaps.geocode(locations[loc])

    if len(geocode_result) == 0:
        continue
    lat = geocode_result[0]['geometry']['location']['lat']
    lng = geocode_result[0]['geometry']['location']['lng']
    req = requests.get(URL+'geo:'+str(lat)+';'+str(lng)+'/?token='+TOKEN)
    res = req.json()

    print(res['status'])
    if res['status'] == 'error' or res['status'] == 'nope':
        continue

    c.execute('''INSERT INTO pollution VALUES (?, ?);''', (locations[loc], res['data']['aqi'])) # insert into pollution


conn.commit()
