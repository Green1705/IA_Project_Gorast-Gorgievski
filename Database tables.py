from flask import Flask
import sqlite3

#make a database connection

conn = sqlite3.connect('Medicine_IA.db')
cur = conn.cursor()
cur.execute("PRAGMA foreign_keys=ON")

cur.execute("""CREATE TABLE IF NOT EXISTS accounts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT)""")

#create table for students
cur.execute("""CREATE TABLE IF NOT EXISTS students(
    student_id TEXT PRIMARY KEY,
    name TEXT,
    age INTEGER,
    Parents_ID TEXT,
    )""")




app = Flask(__name__)

if __name__ == '__main__':
    app.run()