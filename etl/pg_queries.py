from psycopg import sql

# Запрос для получения фильмов и связанных данных по переданным идентификаторам
get_film_works_query = sql.SQL("""
SELECT 
    fw.id,
    fw.title,
    fw.description,
    fw.rating AS imdb_rating,
    array_agg(DISTINCT g.name) AS genres,
    jsonb_agg(DISTINCT jsonb_build_object(
        'id', p.id,
        'full_name', p.full_name,
        'role', pfw.role
    )) AS person_details
FROM 
    content.film_work AS fw
LEFT JOIN 
    content.person_film_work pfw ON pfw.film_work_id = fw.id
LEFT JOIN 
    content.person p ON pfw.person_id = p.id
LEFT JOIN 
    content.genre_film_work gfw ON gfw.film_work_id = fw.id
LEFT JOIN 
    content.genre g ON gfw.genre_id = g.id
WHERE 
    fw.id = ANY(%s)
GROUP BY 
    fw.id
ORDER BY 
    fw.modified;
""")

# Запрос для получения всех ID фильмов, измененных с момента последней проверки
get_all_modify_ids_query = sql.SQL("""
SELECT fw.id 
FROM content.film_work fw
LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
LEFT JOIN content.person p ON pfw.person_id = p.id
LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
LEFT JOIN content.genre g ON gfw.genre_id = g.id
WHERE fw.modified > %s
   OR p.modified > %s
   OR g.modified > %s
GROUP BY fw.id;
""")
