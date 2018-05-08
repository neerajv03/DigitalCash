import socket
import MySQLdb
import re

def gotoNextSteps():
    connection.send("Unblind n - 1 Money Orders and reveal the identity Strings")
    
    return

def checkAuthencity(custId, moneyOrderNum, Amount):

    ordNumber = re.findall('\\d+', moneyOrderNum)
    cusId = re.findall('\\d+', custId)

    blindInd = 0
    query = "select * from MoneyOrder where OrdNum in ('%s')" %(ordNumber[0])
    query += " and Ind = %d;" %(blindInd)


    cursor.execute(query)
    temp = cursor.fetchone()
#    print query 
#    print cursor.execute(query)
    

#    print ordNumber[0]
    #length = len(temp)
    ##print ordNumber[0]
    print temp

    #if(temp):
    print "Customer has followed the Correct Steps, Signing the MoneyOrder"
    query = "UPDATE MoneyOrder SET signBank = 1 where OrdNum in ('%s');" %(ordNumber[0])
    cursor.execute(query)
    sqlDatabase.commit()

    query = "Update CustomerDetails "
    query += "set AccountBalance = AccountBalance - '%s'" %(Amount)
    query += " where Cust_Id in ('%s');" %(cusId[0])
    cursor.execute(query)
    sqlDatabase.commit()
    
    connection.send("Customer has followed the Correct Steps, Signing the MoneyOrder")
    print "Deducting an Amount of '%s' from '%s' Account"  %(Amount, cusId[0])

#    else:
#        print "There is a mistake in the MoneyOrder, Kindly Reprocess them."

if __name__ == '__main__':
    print "Bank Server Website"


    sqlDatabase = MySQLdb.connect(host = "localhost", user = "neeraj", passwd = "password", db = "DigitalCash")
    cursor = sqlDatabase.cursor()

    listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listenSocket.bind(('localhost', 9000))
    listenSocket.listen(10)  ## Number of connections 

    while True:
        connection, fromCustomer = listenSocket.accept()
        receive = connection.recv(100)
       # receiveAmount = connection.recv(100);
        custId = receive.split(',')[0]
        Amount = receive.split(',')[1]
        query = 'Select AccountBalance from CustomerDetails where Cust_Id In (%s)' % custId
        cursor.execute(query)
        print receive

        temp = cursor.fetchone()

        if (temp):
            results = list(temp)

            if (int(Amount) > results[0]):
                connection.send("Insufficient Balance in the account, exitting the transaction")
            else:
                query = 'Select Cust_Name from CustomerDetails where Cust_Id In (%s)' % custId
                cursor.execute(query)
                temp = str(cursor.fetchone())
                temp = temp.split(',')[0]
                temp = temp.split('(')[1]
                string = temp + " your balance requirements have been met."
                connection.send(string)

        else:
            connection.send("Incorrect Customer ID, Please check and try again")
        
        waitReply = connection.recv(100)
        #print waitReply

        if(waitReply == "Contacting Bank for Next Steps."):
            print "Processing Next Steps, Please Wait"
            gotoNextSteps()
        
        waitReply = connection.recv(100)
        if(waitReply == "Money Orders Unblinded, Please Check"):
            print "looking for the Authencity of the Money Orders"
            moneyOrderNum = connection.recv(100)
            checkAuthencity(custId, moneyOrderNum, Amount)
            #print custId