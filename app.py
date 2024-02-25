from flask import Flask, render_template, request, session
import sqlite3, bcrypt,datetime,simplejson as json, smtplib



#defining functions for encryption

pwd="I wanna yeet my laptop across my desk"
def hash(password):
    pwd_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return pwd_hash



def check_hash(password, hashed_pwd):
    if bcrypt.checkpw(password.encode('utf-8'), hashed_pwd) == True:
        return True
    else:
        return False


def make_int(data):

    try:
        if not data.isdigit():
            data = int(data[1:])
        return int(data)
    except ValueError:
        return 0

def bubblesort(data, order):
    if order == "asc":
        for i in range(len(data)):
            for j in range(len(data) - 1):
                if make_int(data[j][0]) > make_int(data[j + 1][0]):
                    data[j], data[j + 1] = data[j + 1], data[j]
    if order == "desc":
        for i in range(len(data)):
            for j in range(len(data) - 1):
                if make_int(data[j][0]) < make_int(data[j + 1][0]):
                    data[j], data[j + 1] = data[j + 1], data[j]
    return data

# hashed_pwd = hash(pwd)
# print(hashed_pwd)
# print(check_hash(pwd, hashed_pwd))


conn=sqlite3.connect('Medicine_IA.db')
cur=conn.cursor()
cur.execute("PRAGMA foreign_keys=ON")



app = Flask(__name__)
app.secret_key = 'secret'


#inserting a row of data that is encrypted
def insert_row_accounts(username, password):
    conn=sqlite3.connect('Medicine_IA.db')
    cur=conn.cursor()
    hash_username = hash(username)
    hash_password = hash(password)
    cur.execute("INSERT INTO accounts VALUES(NULL, ?, ?)", (hash_username, hash_password))
    conn.commit()
    return cur.lastrowid

def names():
    conn = sqlite3.connect('Medicine_IA.db')
    cur = conn.cursor()
    # get all the names from the students table
    cur.execute("SELECT Name_ FROM Students")
    name = cur.fetchall()
    nameS = [i[0] for i in name]
    # replace the spaces with underscores in the names
    nameS = [i.replace(" ", "_") for i in nameS]

    return nameS

def table_(table):
    conn = sqlite3.connect('Medicine_IA.db')
    cur = conn.cursor()
    if table == "Medical_Log":
        cur.execute("SELECT Log_ID, Medical_Log.Student_ID, Name_ , Time_in, Time_out, Complaint, Action_Taken, Temp, RTC, Informed_parent, Medicine_given, Send_home, Place_of_accident, Date "
                    "FROM Medical_log INNER JOIN Students ON Medical_log.Student_ID = Students.Student_ID")
    else:
        cur.execute("SELECT * FROM " + table)
    data = cur.fetchall()

    column_data = list(map(lambda x: x[0], cur.description))
    column = [i.replace("_", " ") for i in column_data]
    if table == "Medical_Log":
        column_data.pop(2)

    return data,column,column_data

def logid(num):
    conn = sqlite3.connect('Medicine_IA.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM Medical_Log")
    logs = cur.fetchall()
    log_id = "L"
    if len(logs) == 0:
        log_id += "1"
    else:
        log_id += str(len(logs) + num)
    return log_id

def send_email(subject,message,email):
    # Gmail Sign In

    gmail_sender = 'rakacademyclinic@gmail.com'
    gmail_passwd = 'tqazgbxbqyjoudxy'
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(gmail_sender, gmail_passwd)
    BODY = '\r\n'.join(['To: %s' % email,
                        'From: %s' % gmail_sender,
                        'Subject: %s' % subject,
                        '', message])
    try:
        server.sendmail(gmail_sender, [email], BODY)
        print('email sent')
    except Exception as e:
        print('error sending mail')
        print(e)
    finally:
        server.quit()

def filler(table):
    conn = sqlite3.connect('Medicine_IA.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + table)
    column_data = list(map(lambda x: x[0], cur.description))
    filler= []
    #append empty strings to the filler list for each column
    for i in range(len(column_data)):
        filler.append("")
    return filler

def id(num):
    conn = sqlite3.connect('Medicine_IA.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM Inventory")
    data = cur.fetchall()
    id = ""
    if len(data) == 0:
        id = 0
    else:
        id += str(len(data) + num)
    return id


@app.route('/')
def hello_world():

    nameS=names()

    return render_template('LoginPg.html')
    # return render_template('log.html',display_info="none",names=nameS)


@app.route('/Login', methods=['GET', 'POST'])
def Login():

    nameS=names()

    conn= sqlite3.connect('Medicine_IA.db')
    cur=conn.cursor()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur.execute("SELECT * FROM accounts")
        account = cur.fetchall()

        for i in account:
            if check_hash(password, i[2]) == True and check_hash(username, i[1]) == True:
                session['logged_in'] = True
                session['username'] = username
                return render_template('log.html',display_info="none",names=nameS)
            else:
                continue
        error = "Invalid Credentials. Please try again."
        return render_template('LoginPg.html',error=error)


@app.route('/Redirect_Login')
def Redirect_Login():
    return render_template('LoginPg.html')


#redirect to inventory page
@app.route('/Inventory')
def Inventory():
    table=table_("Inventory")[0]
    column=table_("Inventory")[1]

    table = bubblesort(table,"desc")

    return render_template('index.html',table=table,column=column,table_name="Inventory")


@app.route('/Log_table')
def Log_table():
    table=table_("Medical_Log")[0]
    column=table_("Medical_Log")[1]
    table= bubblesort(table,"desc")
    return render_template('index.html',table=table,column=column,table_name="Medical_Log")


#redirect to home page
@app.route('/Home')
def Home():
    nameS=names()
    return render_template('log.html',display_info="none",names=nameS)


@app.route('/student',methods=['GET','POST'])
def student():
    conn=sqlite3.connect('Medicine_IA.db')
    cur=conn.cursor()
    nameS=names()
    #finding the student
    if request.method == 'POST':

        name = request.form['student_id']

        #replace the underscores with spaces in the name
        name = name.replace("_", " ")


        #checking if the student is in the database
        #inner join with parents table

        cur.execute("SELECT * FROM Students INNER JOIN Parents ON Students.Parent_ID = Parents.Parent_ID WHERE Name_ = ?", (name,))
        student = cur.fetchall()
        if len(student) == 0:
            error = "Student not found. Please try again."
            return render_template('log.html',error=error,display_info="none", student_id=name, names=nameS)
        else:
            for i in student:

                if i[2] == name:


                    student_id= i[0]
                    gender= i[3]
                    class_= i[4]
                    if gender == "M":
                        gender= "Male"
                    elif gender == "F":
                        gender = "Female"
                    pname = i[6]
                    pphone= i[7]
                    med=""
                    allergy=""
                    chronic=""
                    medication=""
                    precaution=""

                    cur2=conn.cursor()
                    cur2.execute("SELECT * FROM Medical_condition WHERE Student_ID= ?", (student_id,))
                    med_cond = cur2.fetchone()
                    if med_cond is None:
                        med = "None"
                    else:
                        allergy = med_cond[1]
                        chronic = med_cond[2]
                        medication= med_cond[3]
                        precaution= med_cond[4]



                    conn.close()
                    return render_template('log.html',
                                           student=name,
                                           gender=gender,
                                           pname=pname,
                                           pphone=pphone,
                                           display_med=med,
                                           allergy=allergy,
                                           chronic=chronic,
                                           medication=medication,
                                           precaution=precaution,
                                           display_gray="none",
                                           student_id=name,
                                           student_hidden=student_id,
                                           class_=class_,
                                           display_options="none",
                                           names=nameS,)






    return render_template('log.html',display_info="none",names=nameS)


@app.route('/med_log',methods=['GET','POST'])
def med_log():
    if request.method == 'POST':
        #make a connection to the database
        conn=sqlite3.connect('Medicine_IA.db')
        cur=conn.cursor()
        cur.execute("SELECT * FROM Medical_log")
        data=cur.fetchall()
        print(data)
        nameS=names()

        #get info from input
        complaint = request.form['complaint']
        actionTaken = request.form['actionTaken']
        temp=request.form['temp']
        medicineGiven= request.form['medicineGiven']
        tin=request.form['tin']
        tout=request.form['tout']
        return_= request.form['return']
        print(return_)
        if return_ == "No":
            return_2="Yes"
        else:
            return_2="No"
        student_id=request.form['student']
        try:
            infop=request.form['infop']
        except:
            infop="No"

        # get today's date
        today = datetime.date.today()
        log_id= logid(1)

        #make sure the log doesn't already exist
        cur.execute("SELECT * FROM Medical_Log WHERE "
                    "Complaint=? AND Action_Taken=? AND Time_in=? AND Time_out=? AND Student_ID=? AND Date=?" ,
                    (complaint,actionTaken,tin,tout,student_id, today))
        log = cur.fetchall()
        print(log)
        print("log log")
        if log == []:
            print("log is empty")
            # insert info into the database

            # This is in case a record has been deleted, primary key is assigned based on the length of the table,
            # so this prevents it from inserting with an existing primary key

            #I noticed that it will not insert a record if the table is empty
            print(data)
            if data == []:
                print("should be inserted")
                cur.execute("INSERT INTO Medical_Log VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, null,?)",
                            (log_id, student_id, tin, tout, complaint, actionTaken, temp, return_, infop, medicineGiven,return_2,
                             today))


            #generating a valid id by looping through the table and finding the first available id
            for i in range(1,len(data)):
                print(i)
                try:

                    log_id=logid(i)
                    print("wuba luba dub dub")
                    cur.execute("INSERT INTO Medical_Log VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, null,?)",
                                (log_id, student_id, tin, tout, complaint, actionTaken, temp, return_, infop,
                                 medicineGiven, return_2,
                                 today))


                    break
                except sqlite3.IntegrityError:
                    continue





        # making sure the title stays with the student name and the other information
        cur2=conn.cursor()
        cur2.execute(
            "SELECT * FROM Students INNER JOIN Parents ON Students.Parent_ID = Parents.Parent_ID WHERE Student_ID = ?",
            (student_id,))
        student = cur2.fetchone()
        print(student)

        student_id = student[0]
        gender = student[3]
        class_ = student[4]
        if gender == "M":
            gender = "Male"
        elif gender == "F":
            gender = "Female"
        pname = student[6]
        pphone = student[7]
        name= student [2]
        med = ""
        allergy = ""
        chronic = ""
        medication = ""
        precaution = ""

        cur3 = conn.cursor()
        cur3.execute("SELECT * FROM Medical_condition WHERE Student_ID= ?", (student_id,))
        med_cond = cur3.fetchone()
        if med_cond is None:
            med = "None"
        else:
            allergy = med_cond[1]
            chronic = med_cond[2]
            medication = med_cond[3]
            precaution = med_cond[4]

    conn.commit()
    conn.close()


    return render_template('log.html',
                           # passing the student name to the title
                           # passing the student id to the hidden input to be used for printing and emails
                           # content is the content of the email
                           display_gray="none",
                           student=name,
                           names=nameS,
                           student_id=name,
                           name=name,
                           content=complaint,
                           student_hidden=log_id,
                           display_submit="none",
                           gender=gender,
                           pname=pname,
                           pphone=pphone,
                           display_med=med,
                           allergy=allergy,
                           chronic=chronic,
                           medication=medication,
                           precaution=precaution,
                           class_=class_,)








@app.route('/apply_table',methods=['GET','POST'])
def apply_table():

    table_name=request.form['table_name']
    print("name")
    print(table_name)

    column_data=table_(table_name)[2]

    conn=sqlite3.connect('Medicine_IA.db')
    cur=conn.cursor()
    cur.execute("SELECT * FROM "+ table_name)
    data=cur.fetchall()

    # The list is decoded to be readable py python using simplejson module
    list=request.form['list']

    list=json.loads(list)

    list.pop(0)
    list = bubblesort(list,"asc")

    # Removing the names in the list since they were just for display purposes
    if table_name == "Medical_Log":
        print("names deleted")
        for i in list:
            del i[2]

    # Converting the string "None" to None value
    for i in range(len(list)):
        for j in range(len(list[i])):
            if list[i][j]=="None":
                list[i][j]=""
            if list[i][j] == "<br>":
                list[i][j]=""


    # The data variable from cur.fetchall() is a list of tuples, so we need to also convert the list accordingly
    # Once we are done changing it
    for i in range(len(list)):
        list[i]=tuple(list[i])


    test = ('', '', '', '', '', '', '', '', '', '','')
    test2 = ('', '', '', '')

    # Instead of updating the whole table, we will just check which cell is different and update only that one
    for i in range(len(list)):
        #if the whole row is empty except the first row then the row will be deleted
        print(list[i][2:])
        if list[i][2:] == test or list[i][2:] == test2:
            cur.execute("DELETE FROM "+table_name+" WHERE "+column_data[0]+" = ?",(data[i][0],))
            continue


        for j in range(len(list[i])):
            if list[i][j] != data [i][j]:

                cur.execute("UPDATE " + table_name + " SET " + column_data[j]+ "=? WHERE "+ column_data[0]+ "=?", (list[i][j],list[i][0]))

    conn.commit()
    conn.close()
    table = table_(table_name)[0]
    table.reverse()
    column=table_(table_name)[1]
    return render_template('index.html',table=table,column=column,table_name=table_name)


@app.route('/email',methods=['GET','POST'])
def email():
    if request.method == 'POST':
        conn=sqlite3.connect('Medicine_IA.db')
        cur=conn.cursor()
        cur2=conn.cursor()
        subject = request.form['subject']
        body = request.form['body']
        email=request.form['email']
        logid= request.form['logid_']

        cur.execute("SELECT Name_,Students.Student_ID,Medical_Log.Complaint FROM Medical_Log INNER JOIN "
                    "Students ON Medical_Log.Student_ID=Students.Student_ID "
                    "WHERE Log_ID=?",(logid,))
        data=cur.fetchone()
        name=data[0]

        send_email(subject,body,email)

        nameS=names()
        student_id = data[1]
        cur2.execute(
            "SELECT * FROM Students INNER JOIN Parents ON Students.Parent_ID = Parents.Parent_ID WHERE Student_ID = ?",
            (student_id,))
        student = cur2.fetchone()
        print(student)

        student_id = student[0]
        gender = student[3]
        class_ = student[4]
        if gender == "M":
            gender = "Male"
        elif gender == "F":
            gender = "Female"
        pname = student[6]
        pphone = student[7]
        name = student[2]
        complaint=data[2]
        med = ""
        allergy = ""
        chronic = ""
        medication = ""
        precaution = ""

        cur3 = conn.cursor()
        cur3.execute("SELECT * FROM Medical_condition WHERE Student_ID= ?", (student_id,))
        med_cond = cur3.fetchone()
        if med_cond is None:
            med = "None"
        else:
            allergy = med_cond[1]
            chronic = med_cond[2]
            medication = med_cond[3]
            precaution = med_cond[4]

        return render_template('log.html',display_gray="none",display_submit="none",
                               student_hidden=logid, student=name,subject=subject,name=name,names=nameS, student_id=name,
                               content=complaint, gender=gender, pname=pname, pphone=pphone,display_med=med,
                               allergy=allergy,chronic=chronic,medication=medication,precaution=precaution,
                               class_=class_, )



@app.route('/done')
def done():
    nameS=names()
    return render_template('log.html', display_info="none", names=nameS)


@app.route('/add_record/<table_name>')
def add_record(table_name):


    conn=sqlite3.connect('Medicine_IA.db')
    cur=conn.cursor()
    cur.execute("SELECT * FROM "+ table_name)
    data=cur.fetchall()

    filler_= filler(table_name)
    print("works")
    if table_name == "Medical_Log":

        for i in range(1, len(data)):
            try:



                log_id = logid(i)
                filler_[0]=log_id
                filler_[1]="0000000"
                cur.execute("INSERT INTO " + table_name + " VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (filler_))

                break
            except sqlite3.IntegrityError:
                continue
    else:
        for i in range(1, len(data)):
            try:

                num=id(i)
                filler_[0] = num
                cur.execute("INSERT INTO " + table_name + " VALUES(?, ?, ?, ?, ?, ?)",(filler_))

                break
            except sqlite3.IntegrityError:
                continue

    conn.commit()
    conn.close()

    table = table_(table_name)[0]
    column = table_(table_name)[1]
    table.reverse()

    return render_template('index.html', table=table, column=column, table_name=table_name)


if __name__ == '__main__':
    app.run()
