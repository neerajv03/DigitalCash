import socket 
import MySQLdb
import re
import random

IDENTITY = []
moneyOrder = []

def callCheck(moneyOrder, custId):

    print "Inside callCheck"

    order = re.findall('\\d+', moneyOrder)
    iden = re.findall('\\d+', custId)
    moneyOrder = order

    query = "Select Ind from MoneyOrder where "
    query += "OrdNum in ('%s') "% (order[0])
    query += " and Ind = 0 "
    query += " and Id in ('%s');" %(iden[0])
    cursor.execute(query)

    temp = cursor.fetchall()

    if (len(temp) > 0 ):
        print "The Money Order is Valid, Depositing Money to your Account"

        query = "Update MoneyOrder  "
        query += "set Ind = 1"
        query += " where OrdNum in ('%s') "% (order[0])
        query += " and Ind = 0 "
        query += " and Id in ('%s');" %(iden[0])

        cursor.execute(query)
        sqlDatabase.commit()
    else:
        print "Merchant has already deposited this Money Order."

def callMerchantDirectDepost(mon):
    print "Merchant has Deposited a Money Order"

    query = " Select * from MoneyOrder "
    query += " where OrdNum in ('%s') " %(mon)
    query += " and Ind = 0 "

    cursor.execute(query)
    sqlDatabase.commit()

    temp = cursor.fetchall()

    length = len(temp)
    if(length == 0):
        print " Hi Merchant You have already Deposited this Money Order. We cannot Process this"
    else:
        callCheck(mon, IDENTITY[0])

def calChecking(orderNumber1):
    print orderNumber1
    print "This Money Order has been duplicated."
    print "Revealing the Person who did it"

    Money = re.findall('\\d+', (str(orderNumber1)))
    query = "select distinct UniqueString from MoneyOrder "
    query += "where OrdNum in ('%s') " % (Money[0])
    #print query
    cursor.execute(query)    
    temp = cursor.fetchall()
    print temp

    query = "select Cust_Id, Cust_Name from CustomerDetails where "
    query += " Cust_Id in ( select distinct Id from MoneyOrder where "
    query += " OrdNum in ('%s') ) " % (Money[0])
    #print query

    cursor.execute(query)
    
    temp = cursor.fetchall()
    print temp

if __name__ == '__main__':
    print "Bank Merchant Server Website"

    
    sqlDatabase = MySQLdb.connect(host = "localhost", user = "neeraj", passwd = "password", db = "DigitalCash")
    cursor = sqlDatabase.cursor()

    listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listenSocket.bind(('localhost', 8000))
    listenSocket.listen(10)  ## Number of connections 

    while True:
        connection, fromMerchant = listenSocket.accept()
        receive = connection.recv(100)

        print receive

        connection.send("Hello, Greetings from Bank")
        
        string = connection.recv(100)
        print string
        moneyOrder = string.split(',')[0]
        custId = string.split(',')[1]

        iden = re.findall('\\d+', custId)
        IDENTITY.append(iden[0])

        callCheck(moneyOrder, custId)

        mon = connection.recv(100)
        callMerchantDirectDepost(mon)

        fraudRec = connection.recv(100)
        
        calChecking(fraudRec)
