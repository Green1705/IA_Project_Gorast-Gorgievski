from flask import Flask
import sqlite3

conn = sqlite3.connect('Medicine_IA.db')
cur = conn.cursor()
cur.execute("PRAGMA foreign_keys=ON")


# Table for logging in
cur.execute("""CREATE TABLE IF NOT EXISTS accounts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT)""")

# Table for students
cur.execute("""CREATE TABLE IF NOT EXISTS "Students" (
	"Student_ID"	TEXT,
	"Parent_ID"	TEXT,
	"Name_"	TEXT,
	"Gender"	TEXT,
	"Class"	TEXT,
	PRIMARY KEY("Student_ID"),
	FOREIGN KEY("Parent_ID") REFERENCES "Parents"("Parent_ID")
)""")

# Parents table
cur.execute("""CREATE TABLE IF NOT EXISTS "Parents" (
	"Parent_ID"	TEXT,
	"Name"	TEXT,
	"Phone No."	TEXT,
	PRIMARY KEY("Parent_ID")
)""")

# Medical conditions
cur.execute("""CREATE TABLE IF NOT EXISTS "Medical_condition" (
	"Student_ID"	TEXT,
	"Allergy_to"	TEXT,
	"Chronic_Medical_Condition"	TEXT,
	"Medication"	TEXT,
	"Special_Precaution"	TEXT,
	PRIMARY KEY("Student_ID"),
	FOREIGN KEY("Student_ID") REFERENCES "Students"("Student_ID")
)""")

# Medical log
cur.execute("""CREATE TABLE IF NOT EXISTS "Medical_Log" (
	"Log_ID"	TEXT,
	"Student_ID"	TEXT,
	"Time_in"	TEXT,
	"Time_out"	TEXT,
	"Complaint"	TEXT,
	"Action_Taken"	TEXT,
	"Temp"	TEXT,
	"RTC"	TEXT,
	"Informed_parent"	TEXT,
	"Medicine_given"	TEXT,
	"Send_home"	TEXT,
	"Place_of_accident"	TEXT,
	"Date"	TEXT,
	PRIMARY KEY("Log_ID"),
	FOREIGN KEY("Student_ID") REFERENCES "Students"("Student_ID")
)""")

# Inventory table
cur.execute("""CREATE TABLE IF NOT EXISTS "Inventory" (
	"num"	TEXT,
	"Medicine"	TEXT,
	"Quantity"	TEXT,
	"MFD"	TEXT,
	"Expiry_Date"	TEXT,
	"In_hand"	TEXT,
	PRIMARY KEY("num")
)""")

conn.commit()
conn.close()


app = Flask(__name__)

if __name__ == '__main__':
    app.run()