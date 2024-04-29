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

    def getContentText(contentId):
        con = sqlite3.connect(DataBaseOperations._DB)
        c = con.cursor()
        try:
            sql_select_query = "SELECT contentId, text FROM Content" + contentId + ";"
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
        finally:
            con.commit()
            c.close()
            con.close()
    
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
        
    def updateScore(score, totalScore, contentId, userId):
        con = sqlite3.connect(DataBaseOperations._DB)
        c = con.cursor()
        try:
            x = (score, totalScore, userId)
            update = "UPDATE Score SET content" + contentId + "Score = ?, TContent" + contentId +"Score = ? WHERE userId = ?;"
            c.execute(update, x)
        finally:
            con.commit()
            c.close()
            con.close()
    
    def getHighScore(contentId, userId):
        con = sqlite3.connect(DataBaseOperations._DB)
        c = con.cursor()
        try:
            sql_select_query = "SELECT TContent" + str(contentId) + "Score FROM Score WHERE userId = ?;"
            c.execute(sql_select_query, (userId,))
            record = c.fetchall()
        finally:
            con.commit()
            c.close()
            con.close()
        return record[0][0]
    
    def getTScores(userId):
        con = sqlite3.connect(DataBaseOperations._DB)
        c = con.cursor()
        try:
            sql_select_query = """SELECT TContent1Score, TContent2Score, TContent3Score, TContent4Score, TContent5Score,
            TContent6Score, TContent7Score, TContent8Score, TContent9Score, TContent10Score, TContent11Score,
            TContent12Score, TContent13Score, TContent14Score, TContent15Score FROM Score WHERE userId = ?;"""
            c.execute(sql_select_query, (userId,))
            record = c.fetchall()
        finally:
            con.commit()
            c.close()
            con.close()
        return record[0]
    
    def initTime(userId):
        con = sqlite3.connect(DataBaseOperations._DB)
        c = con.cursor()
        try:
            x = (userId,)
            insert = """INSERT INTO Time (userId) VALUES (?);"""
            c.execute(insert, x)
            ID = c.lastrowid
        finally:
            con.commit()
            c.close()
            con.close()
        return ID
    
    def updateTime(pageName, time, userId):
        con = sqlite3.connect(DataBaseOperations._DB)
        c = con.cursor()
        try:
            sql_select_query = "SELECT " + pageName + " FROM Time WHERE userId = ?;"
            c.execute(sql_select_query, (userId,))
            record = c.fetchall()
            prevTime = record[0][0]
            x = (prevTime + time, userId)
            update = "UPDATE Time SET " + pageName + " = ? WHERE userId = ?;"
            c.execute(update, x)
        finally:
            con.commit()
            c.close()
            con.close()
            
    def getTime(userId):
        con = sqlite3.connect(DataBaseOperations._DB)
        c = con.cursor()
        try:
            sql_select_query = "SELECT learn, play, read FROM Time WHERE userId = ?;"
            c.execute(sql_select_query, (userId,))
            record = c.fetchall()
        finally:
            con.commit()
            c.close()
            con.close()
        return record[0]