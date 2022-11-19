import mysql.connector

myDB = mysql.connector.connect(host='localhost', user='root', passwd="sobhi")
myCursor = myDB.cursor()

def create():
    '''creates the database and the tasks and users tables'''
    try: myCursor.execute('drop database todo')
    except: pass
    myCursor.execute('create database todo')
    myCursor.execute('use todo')

    createStmt = """
    create table tasks
    (
        id int primary key auto_increment,
        task varchar(100) not null,
        due_by date not null,
        status varchar(20) not null,
        check(status in('Not started','In progress','Finished'))
    )
    """
    myCursor.execute(createStmt)
    
    createStmt = """
    create table users
    (
        userid varchar(50) primary key,
        access varchar(50),
        check(access in('read','write'))
    )
    """
    myCursor.execute(createStmt)
    
def populate():
    '''populates the creates tables with values'''
    myCursor.execute("insert into tasks values(1, 'math assignment', '2022-11-18', 'Finished')")
    myCursor.execute("insert into tasks values(2, 'Disk management project', '2022-11-19', 'In progress')")
    myCursor.execute("insert into tasks values(3, 'shopping', '2022-11-30', 'Not started');")
    myCursor.execute("insert into tasks values(4, 'learn git', '2022-11-21', 'Not started');")
    myCursor.execute("insert into tasks values(5, 'project submission', '2022-11-02', 'Not started');")
    myCursor.execute("insert into tasks values(6, 'Visit dentist', '2022-11-10', 'Finished');")

    myDB.commit()

    myCursor.execute("insert into users values('shobi001', 'write')")
    myCursor.execute("insert into users values('shobi002', 'read')")
    myDB.commit()
    
    
if __name__ == '__main__':
    create()
    populate()
    myCursor.close()
    myDB.close()