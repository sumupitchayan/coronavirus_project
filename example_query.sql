SELECT id, city, gender, age, aqi FROM virus_data
JOIN environment
ON location == city
