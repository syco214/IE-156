import psycopg2
import pandas as pd
import os 

def getdblocation():
    DATABASE_URL = os.environ['DATABASE_URL']
    db = psycopg2.connect(DATABASE_URL, sslmode='require')

    return db

def modifydatabase(sql, values):
    db = getdblocation()
    cursor = db.cursor()
    cursor.execute(sql, values)
    db.commit()
    db.close()

def querydatafromdatabase(sql, values, dfcolumns):
    db = getdblocation()
    cur = db.cursor()
    cur.execute(sql, values)
    rows = pd.DataFrame(cur.fetchall(), columns=dfcolumns)
    db.close()
    return rows