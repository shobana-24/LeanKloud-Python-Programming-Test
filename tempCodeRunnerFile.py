import mysql.connector

myDB = mysql.connector.connect(host='localhost', user='root', passwd="sobhi")
myCursor = myDB.cursor()

def create():
    '''creates the database and the tasks and users tables'''
    try: myCursor.execute('drop database todo')