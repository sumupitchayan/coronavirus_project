SELECT id, city, gender, age, aqi FROM virus_data
JOIN pollution
ON location == city
