import socket 
import MySQLdb
import re
import random

flag1 = []

def checkBankSign(moneyOrder, custId):
    #print "Hello"
    order = re.findall('\\d+', moneyOrder)
    iden = re.findall('\\d+', custId)

    query = "Select signBank from MoneyOrder where "
    query += "OrdNum in ('%s')" % (order[0])
    query += " and Id in ('%s');" % (iden[0])

    cursor.execute(query)
    temp = str(cursor.fetchall())
    print temp
    if(temp):
        print "Bank Signature Verified"

        query = "Insert into Merchant (MerchantId, moneyOrderNumber, custId)"
        query += " values ('%d', '%s', '%s');" %(1, order[0], iden[0])

        cursor.execute(query)
        sqlDatabase.commit()
        
        k = random.randrange(0, 1)
        #print k 
        flag1.append(k)
        if(k == 0):
            string = "left"
        else:
            string = "right"
        
        connection.send(string)
        return True
    else:
        print "Bank Verification Failed"
        return False

def depositMoneyOrder(moneyOrder, custId):
    print "Inside Depositing Function"

    merchantBankSocket.send("Hi I am Merchant Talking")

    string = merchantBankSocket.recv(100)
    print string

    order = re.findall('\\d+', moneyOrder)
    iden = re.findall('\\d+', custId)

    print "Depositing Money Order: %s" %(order[0])

    merchantBankSocket.send(str(order[0]) + ',' + str(iden[0]))

def checkAllMoneyOrder():
    print "Here are the Money Orders present in our dataBase"

    query = "select moneyOrderNumber from Merchant"
    cursor.execute(query)
    temp = cursor.fetchall()

    for i in temp:
        print i

    print "Do you want to send any money order to the bank ?"
    num = input()

    if(num > 0):
        print "Enter the Money Order Number !!"
        mon = input()

        merchantBankSocket.send(str(mon))

if __name__ == '__main__':

    print "Welcome to Merchant Website, We accept Money Orders"

    sqlDatabase = MySQLdb.connect(host = "localhost", user = "neeraj", passwd = "password", db = "DigitalCash")
    cursor = sqlDatabase.cursor()

    merchantSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    merchantSocket.bind(('localhost', 9500))
    merchantSocket.listen(10)

    merchantBankSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    merchantBankSocket.connect(('localhost', 8000))

    while True:
        connection, fromCustomer = merchantSocket.accept()
        

        receive = connection.recv(100)
       
        print "hi"

        moneyOrder = receive.split(',')[0]
        custId = receive.split(',')[1]
        
        flag = checkBankSign(moneyOrder, custId)

        if(flag):
            depositMoneyOrder(moneyOrder, custId)

        #print receive

        checkAllMoneyOrder()

        get = connection.recv(100)
        orderNumber = re.findall('\\d+', get)

        #if(flag[0] == 0):
        if(flag1[0]):
            constant = 1
        else:
            constant = 0

        connection.send(str(constant))
        #else:

        fraudIden = connection.recv(100)

        print fraudIden

        merchantBankSocket.send(str(orderNumber))
        