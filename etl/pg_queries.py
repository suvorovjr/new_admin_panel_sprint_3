from psycopg import sql

get_film_works_query = sql.SQL("""
SELECT 
    fw.id AS id,
    fw.title AS title,
    fw.description AS description,
    fw.rating AS imdb_rating,
    ARRAY(SELECT g.name FROM content.genre AS g
          JOIN content.genre_film_work AS gfw ON g.id = gfw.genre_id
          WHERE gfw.film_work_id = fw.id) AS genres,
    ARRAY(SELECT p.full_name FROM content.person AS p
          JOIN content.person_film_work AS pfw ON p.id = pfw.person_id
          WHERE pfw.film_work_id = fw.id AND pfw.role = 'DR') AS directors_names,
    ARRAY(SELECT p.full_name FROM content.person AS p
          JOIN content.person_film_work AS pfw ON p.id = pfw.person_id
          WHERE pfw.film_work_id = fw.id AND pfw.role = 'AT') AS actors_names,
    ARRAY(SELECT p.full_name FROM content.person AS p
          JOIN content.person_film_work AS pfw ON p.id = pfw.person_id
          WHERE pfw.film_work_id = fw.id AND pfw.role = 'SW') AS writers_names
FROM 
    content.film_work AS fw
WHERE 
    fw.id = ANY(%s);
""")

get_modify_genres_query = sql.SQL("""
SELECT 
    id, modified
    FROM content.genre
    WHERE modified > %s
    ORDER BY modified;
""")

get_modify_person_query = sql.SQL("""
SELECT 
    id, modified
    FROM content.person
    WHERE modified > %s
    ORDER BY modified;
""")

get_all_modify_ids_query = sql.SQL("""
    SELECT fw.id 
    FROM content.film_work fw
    LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
    LEFT JOIN content.person p ON pfw.person_id = p.id
    LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
    LEFT JOIN content.genre g ON gfw.genre_id = g.id
    WHERE p.id = ANY(%s)
      OR g.id = ANY(%s)
      OR fw.modified > %s
    GROUP BY fw.id;
""")
