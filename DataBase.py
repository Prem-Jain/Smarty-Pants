import sqlite3
class DataBaseOperations:
    _DB = "SmartyPants.db"
    def getUserDetails(email):
        con = sqlite3.connect(DataBaseOperations._DB)
        c = con.cursor()
        try:
            sql_select_query = "SELECT ID, DOB, PASSWORD FROM Users WHERE EMAIL = ?;"
            c.execute(sql_select_query, (email,))
            record = c.fetchall()   
        finally:
            con.commit()
            c.close()
            con.close()
        return record[0]
        
    def checkEmailExists(email):
        con = sqlite3.connect(DataBaseOperations._DB)
        c = con.cursor()
        try:
            sql_select_query = "SELECT * FROM Users WHERE EMAIL = ?;"
            c.execute(sql_select_query, (email,))
            record = c.fetchall()   
        finally:
            con.commit()
            c.close()
            con.close()
        if len(record) == 0:
            return False
        else:
            return True
    
    def addUser(name, email, dob, pwd):
        con = sqlite3.connect(DataBaseOperations._DB)
        c = con.cursor()
        try:
            x = (name, email, dob, pwd)
            insert = """INSERT INTO Users (NAME, EMAIL, DOB, PASSWORD) VALUES (?,?,?,?);"""
            c.execute(insert, x)
            ID = c.lastrowid
        finally:
            con.commit()
            c.close()
            con.close()
        return ID
    
    def getUser(userId):
        con = sqlite3.connect(DataBaseOperations._DB)
        c = con.cursor()
        try:
            sql_select_query = "SELECT NAME, EMAIL, DOB FROM Users where ID = ?;"
            c.execute(sql_select_query, (userId,))
            record = c.fetchall()
        finally:
            con.commit()
            c.close()
            con.close()
        return record[0]
    
    def getLearn():
        con = sqlite3.connect(DataBaseOperations._DB)
        c = con.cursor()
        try:
            sql_select_query = "SELECT * FROM Learn;"
            c.execute(sql_select_query)
            record = c.fetchall()
        finally:
            con.commit()
            c.close()
            con.close()
        return record
    
    def getLearnContent(contentId):
        con = sqlite3.connect(DataBaseOperations._DB)
        c = con.cursor()
        try:
            sql_select_query = "SELECT * FROM Content" + contentId + ";"
            c.execute(sql_select_query)
            record = c.fetchall()
        finally:
            con.commit()
            c.close()
            con.close()
        return record

    def initScores(userId):
        con = sqlite3.connect(DataBaseOperations._DB)
        c = con.cursor()
        try:
            x = (userId,)
            insert = """INSERT INTO Score (userId) VALUES (?);"""
            c.execute(insert, x)
            ID = c.lastrowid
        finally:
            con.commit()
            c.close()
            con.close()
        return ID
    
    def getScore(contentId, userId):
        con = sqlite3.connect(DataBaseOperations._DB)
        c = con.cursor()
        try:
            sql_select_query = "SELECT content" + str(contentId) + "Score FROM Score WHERE userId = ?;"
            c.execute(sql_select_query, (userId,))
            record = c.fetchall()
        finally:
            con.commit()
            c.close()
            con.close()
        return record[0][0]
        
    def updateScore(score, contentId, userId):
        con = sqlite3.connect(DataBaseOperations._DB)
        c = con.cursor()
        try:
            x = (score, userId)
            update = "UPDATE Score SET content" + contentId + "Score = ? WHERE userId = ?;"
            c.execute(update, x)
        finally:
            con.commit()
            c.close()
            con.close()