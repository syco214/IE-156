import apps.dbconnect as db
from datetime import datetime

def addfewgenres():
    sqlcode = """ INSERT INTO genres ( 
        genre_name,
        genre_modified_date,
        genre_delete_ind
    )
    VALUES (%s, %s, %s) """

    db.modifydatabase(sqlcode, ['Action', datetime.now(), False])
    db.modifydatabase(sqlcode, ['Horror', datetime.now(), False])

    print('done!')

sql_query = """ SELECT * FROM genres"""
values = []
columns = ['id', 'name', 'modified', 'is_deleted']
df = db.queryfromdatabase(sql_query, values, columns)
print(df)
