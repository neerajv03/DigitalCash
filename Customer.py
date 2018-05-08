from BitVector import *
import PrimeGenerator as pGen
import socket
import random
import string
import MySQLdb
import hashlib
import os
from collections import namedtuple 
from fractions import gcd
import re
#import BitVector

sqlDatabase = MySQLdb.connect(host = "localhost", user = "neeraj", passwd = "password", db = "DigitalCash")
cursor = sqlDatabase.cursor()

generator = pGen.PrimeGenerator(bits = 16, debug = 0, emod = 5)
pdata1 = generator.findPrime()
pdata2 = generator.findPrime()
e = 5
N = pdata1 * pdata2

KeyPair = namedtuple('KeyPair', 'public private')
Key = namedtuple('Key', 'exponent modulus')

rsaListFiles = []
moneyOrderFiles = []
blindOrders = []
signedFiles = []
unblindedSigned = []
verfiedOutput = []
decryptList = []
spendMoneyOrder = []
customerId = []

### Blinding Function Begins

def is_prime(n, k=30):
    if n <= 3:
        return n == 2 or n == 3
    neg_one = n - 1

    s, d = 0, neg_one
    while not d & 1:
        s, d = s+1, d>>1
    assert 2 ** s * d == neg_one and d & 1

    for i in xrange(k):
        a = random.randrange(2, neg_one)
        x = pow(a, d, n)
        if x in (1, neg_one):
            continue
        for r in xrange(1, s):
            x = x ** 2 % n
            if x == 1:
                return False
            if x == neg_one:
                break
        else:
            return False
    return True

def randprime(N=10**8):
    p = 1
    while not is_prime(p):
        p = random.randrange(N)
    return p

def multinv(modulus, value):
    x, lastx = 0, 1
    a, b = modulus, value
    while b:
        a, q, b = b, a // b, a % b
        x, lastx = lastx - q * x, x
    result = (1 - lastx * modulus) // value
    if result < 0:
        result += modulus
    assert 0 <= result < modulus and value * result % modulus == 1
    return result

def keygen(N, public=None):
    prime1 = randprime(N)
    prime2 = randprime(N)
    composite = prime1 * prime2
    totient = (prime1 - 1) * (prime2 - 1)
    if public is None:
        while True:
            private = random.randrange(totient)
            if gcd(private, totient) == 1:
                break
        public = multinv(totient, private)
    else:
        private = multinv(totient, public)
    assert public * private % totient == gcd(public, totient) == gcd(private, totient) == 1
    assert pow(pow(1234567, public, composite), private, composite) == 1234567
    return KeyPair(Key(public, composite), Key(private, composite))

def calculateD():
    phi = (pdata1 - 1) * (pdata2 - 1)
    mod  = BitVector(intVal = phi)
    bitVec = BitVector(intVal = e)
    d = int(bitVec.multiplicative_inverse(mod))
    return d

def decryptRSA():
    d = calculateD()

    for file in verfiedOutput:
        string = "FinalDecryptedOut" + file
        fileWrite = open(string, 'w')
        fileRead = open(file, 'r')

        eMessage = [int(line) for line in fileRead]
        dec = [chr(pow(char, d, N)) for char in eMessage]
        dec = ''.join(dec)

        fileWrite.write(dec)
        decryptList.append(string)    

def verifyMoneyOrder():
    for file in unblindedSigned:
        string = "Verify" + str(file)
        fileWrite = open(string, 'w')

        fileOpen = open(file, 'r')
        
        for line in fileOpen:
            output = str(pow(int(line),*pubkey)%pubkey[1])
        #output = ''.join(output)
            print >> fileWrite, output
        #fileWrite.write(output)
        verfiedOutput.append(string)

def multInverse(modulus, value):
    x, lastx = 0, 1
    a, b = modulus, value
    while b:
        a, q, b = b, a // b, a % b
        x, lastx = lastx - q * x, x
    result = (1 - lastx * modulus) // value
    if result < 0:
        result += modulus
    assert 0 <= result < modulus and value * result % modulus == 1
    return result

def unBlindMoneyOrder():
    
    length = len(signedFiles)
    roSign = signedFiles[length - 1]

    for file in signedFiles:
        string = "UnblindedMoneyOrder" + str(file)
        fileWrite = open(string, 'w')

        fileOpen = open(file, 'r')
        for line in fileOpen:
            signedMessage = int(line)
            cipherText = (signedMessage * multinv(pubkey[1], factor))% pubkey[1]            
            print >> fileWrite, cipherText
        unblindedSigned.append(string)
    
    blindedMoneyOrder = re.findall('\\d+', roSign)
    #blindedMoneyOrder = blindedMoneyOrder.split('[')[1]
    #blindedMoneyOrder = blindedMoneyOrder.split(']')[0]
    spendMoneyOrder.append(blindedMoneyOrder)

    query = "Select distinct Id from MoneyOrder where OrdNum in ('%s');" % blindedMoneyOrder[0]
    cursor.execute(query)
    temp = str(cursor.fetchone())
    custId = re.findall('\\d+', temp)
    
    print custId[0]
    print blindedMoneyOrder[0]

    query = "Update MoneyOrder "
    query += "set Ind = 1 "
    query += "where Id in ('%s') and " %(custId[0])
    query += "OrdNum not in ('%s');" %(blindedMoneyOrder[0])
    cursor.execute(query)
    sqlDatabase.commit()


def signMoneyOrders():
    for file in blindOrders:
        string = "signedMoneyOrders" + str(file)
        fileWrite = open(string, 'w')

        fileOpen = open(file, 'r')
        for line in fileOpen:
            cipherText = pow(int(line), *privkey)% privkey[1]
            print >> fileWrite, cipherText

        signedFiles.append(string)

def blindingfactor(N):
    b=random.random()*(N-1)
    r=int(b)
    while (gcd(r,N)!=1):
        r=r+1
    factor = r
    return r

def blindMoneyOrders():
    for file in rsaListFiles:
        string = "blind" + str(file)
        fileWrite = open(string, 'w')
        fileOpen = open(file, 'r')
        
        for line in fileOpen:
            val = int(line)
            cipherText = (pow(factor,*pubkey)* val) % pubkey[1] 
            print >> fileWrite, cipherText
        blindOrders.append(string)        

def rsaEncrypt():
    for file in moneyOrderFiles:
        string = "RSA_Encrypt" + str(file)
        fileWrite = open(string, 'w')
        fileOpen = open(file, 'r')
        plainText = fileOpen.read()
        for char in plainText:
            cipherText = pow(ord(char), e, N)
            print >> fileWrite, cipherText
        
        rsaListFiles.append(string)

### Blinding Logic Ends

def createMoneyOrderFiles(moneyOrderNumber):    
    query = "select * from MoneyOrder where OrdNum in (%s);" % moneyOrderNumber
    cursor.execute(query)
    tempList = list (cursor.fetchall())

    amount = [item[1] for item in tempList]
    msgNum = [item[3] for item in tempList]
    idenstr = [item[4] for item in tempList]
    left = [item[6] for item in tempList]
    right = [item[7] for item in tempList]
    
    fileName = str(moneyOrderNumber)  + ".txt"
    fileWrite = open(fileName, 'w')

    string = "------------------------------------------------\n"
    string += "Money Order Number: %s\n" % moneyOrderNumber
    string += "------------------------------------------------\n"
    string += "Money Order Amount: %d\n" % amount[0]
    string += "------------------------------------------------\n"
    string += "Unique String of Customer: %s\n" % idenstr[0]
    string += "------------------------------------------------\n"

    for count in range(0, len(msgNum)):

        string += "%d Iteration: \n" % msgNum[count]
        string += "Left String Value:  %s\n" % left[count]
        string += "Right String Value: %s\n" % right[count]
        string += "------------------------------------------------\n"
    
    print >> fileWrite, string
    fileWrite.close()

    moneyOrderFiles.append(fileName)
    return

def bitCommitment(moneyOrderNumber, commitString, msgNum, val):

    # Bit Commitment using One Way Functions
    length = len(str(commitString)) / 8
    randData1 = ''.join([random.choice(string.ascii_letters) for n in xrange(length)])
    randData2 = ''.join([random.choice(string.ascii_letters) for n in xrange(length)])

    bitrandData1 = BitVector(textstring = str(randData1))
    bitrandData2 = BitVector(textstring = str(randData2))

    fullString = str(commitString) + str(bitrandData1) + str(bitrandData2)

    hashVal = hashlib.sha224(fullString).hexdigest()
    query = "Insert into BitCommit (OrdNum, MID, LInd, RandData1, RandData2, CommitString, HashValue)"
    query += " values (%d, %d, %d, \"%s\", \"%s\", \"%s\", \"%s\");" % ( moneyOrderNumber, msgNum, val, str(bitrandData1.getHexStringFromBitVector()), str(bitrandData2.getHexStringFromBitVector()), str(commitString.getHexStringFromBitVector()), hashVal)

    cursor.execute(query)
    sqlDatabase.commit()
    #print hashVal

def secretSpliting(identityString):
    length = len(str(identityString)) / 8
    randData = ''.join([random.choice(string.ascii_letters) for n in xrange(length)])
    rightData = BitVector(textstring = str(randData))
    leftData = identityString ^ rightData   
    #print "check"
    #print identityString
    #print rightData ^ leftData
    return leftData, rightData


def createMoneyOrders(accountNum, amount, moneyCount):
    query = 'select * from CustomerDetails where cust_id in (%d);' % accountNum
    cursor.execute(query)
    temp = cursor.fetchall()
    #query = 'select address from CustomerDetails where cust_id in (%d);' % accountNum
    #cursor.execute(query)
    #temp.append(cursor.fetchall())


    custID = [item[0] for item in temp]
    custName = [item[1] for item in temp] 
    custAddress = [item[3] for item in temp]

    string = str(custID[0]) + str(custName[0]) + str(custAddress[0])
    uniqueString = BitVector(textstring = string)
    amt = BitVector(textstring = str(amount))

    for outCounter in range(0, moneyCount):        
        moneyOrderNumber = random.randint(111111111, 222222222)
       
        #print moneyOrderNumber
        msgNum = 0
        BlindInd = 0
        identityStrings = []
        for count in range(0, moneyCount):
            random.seed()
            msgNum += 1
            randomBit = random.getrandbits(120)
            randomBitVec = BitVector(intVal = randomBit, size = 120)
            identityStrings.append(amt + randomBitVec)
            right, left = secretSpliting(identityStrings[count])
            
          
            query = "Insert into MoneyOrder (Id, Amt, OrdNum,"
            query += " MId, IdentityString, UniqueString, LeftString, RightString, Ind) "
            query += "values (%d, %d, %d, %d, \"%s\", \"%s\", \"%s\", \"%s\", %d);" %(custID[0], amount, moneyOrderNumber, msgNum, uniqueString.getHexStringFromBitVector(), str(identityStrings[count].getHexStringFromBitVector()), str(left.getHexStringFromBitVector()), str(right.getHexStringFromBitVector()), BlindInd)

            bitCommitment(moneyOrderNumber, right, msgNum, 0)
            bitCommitment(moneyOrderNumber, left, msgNum, 1)

            #print query
            cursor.execute(query)
            sqlDatabase.commit()
        
        createMoneyOrderFiles(moneyOrderNumber)
    print "Secret Splitting, Bit Commitment and the MoneyOrder Files have been Performed."
    ## Secret Split Check.. Working
    #for count in range(0, moneyCount):
    #    print identityStrings[count] 
    #    print identityLeft[count] ^ identityRight[count]


def createBankConnection():
    #print "Hi"

    customerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    customerSocket.connect(('localhost', 9000))

    print "Please Enter the Customer ID:"
    number = input()
    customerId.append(number)
    print "Please Enter the Amount you want to be present in Money Order:"
    Amount = input()
    customerSocket.send(str(number) + ',' + str(Amount))
    #customerSocket.send(str(Amount))
    msg = customerSocket.recv(100)
    print msg

    if ("your balance requirements have been met" in msg):
        print "Enter the number of money orders you want to process"
        moneyCount = input()
        createMoneyOrders(number, Amount, moneyCount)
    else:
        return

    print "Blind the Money Orders\n"
        
        ## Blinding Begins
    rsaEncrypt()
    blindMoneyOrders()
    signMoneyOrders()
    print "All the Money Orders Have Been Blinded, Contacting Bank for Next Steps."

    strng = "Contacting Bank for Next Steps."
   
    customerSocket.send(strng)

    msg = customerSocket.recv(100)
    print msg

    unBlindMoneyOrder()

    print "Unblinded n - 1 Money Orders, Verifying with the bank"
    string = "Money Orders Unblinded, Please Check"
    customerSocket.send(string)
    customerSocket.send(str(spendMoneyOrder[0]))

    msg = customerSocket.recv(100)
    if (msg == "Customer has followed the Correct Steps, Signing the MoneyOrder"):
        print "Signing the Last Money Order, for the customer to use"    

    verifyMoneyOrder()

    print "Signed the Money Order, You can use them"
    decryptRSA()
    #os.system("rm /home/neeraj/Desktop/209_Project/Blind*")
   # os.system("rm /home/neeraj/Desktop/209_Project/Verify*")
    #os.system("rm /home/neeraj/Desktop/209_Project/Unblinded*")
    #os.system("rm /home/neeraj/Desktop/209_Project/RSA*")
    ## Blinding Ends

def createMerchantConnection():
    print "Your Money Order is Ready to use, do let us know whether you want to transfer"   
    userInput = input()
    if(userInput > 0):
        print "Preparing for Merchant Connection"

        #customerMerchantSocket.send("Sending The Money Order..")
        customerMerchantSocket.send(str(spendMoneyOrder[0]) + ',' + (str(customerId[0])))

        order = re.findall('\\d+', str(spendMoneyOrder[0]))
        iden = re.findall('\\d+', str(customerId[0]))

        string = customerMerchantSocket.recv(100)
        if (string == "left"):
            print "Revealing all the Left Identity Strings"
            query = "select LeftString from MoneyOrder where "
            query += " Id in ('%s')" %  (iden[0])
            query += " and OrdNum in ('%s'); " %(order[0])        
            
        else:
            print "Revealing all the Right Identity Strings"
            query = "select RightString from MoneyOrder where "
            query += " Id in ('%s')" %  (iden[0])
            query += " and OrdNum in ('%s'); " %(order[0])
        
        cursor.execute(query)

        temp = cursor.fetchall()

        print "Revealing all my " + string + " Strings"
        for i in temp:
            print i       

def createnewOrder():
    print "Do you want to deposit Money Order Again ?"    

    MoneyOrder = re.findall('\\d+', str(spendMoneyOrder[0]))
    num = input()
    if(num > 0):
        print "Sending Money Order %s" %(str(spendMoneyOrder[0]))
        customerMerchantSocket.send(str(spendMoneyOrder[0]))


        rec = customerMerchantSocket.recv(100)
        if (rec == "0"):
            print "Revealing Right String"
            query = "select RightString from MoneyOrder where "
            query += " Id in ('%s')" %  (str(customerId[0]))
            query += " and OrdNum in ('%s'); " %(str(MoneyOrder[0]))
        
        else:
            print "Revealing Left String"
            query = "select LeftString from MoneyOrder where "
            query += " Id in ('%s')" %  (str(customerId[0]))
            query += " and OrdNum in ('%s'); " %(str(MoneyOrder[0]))
        
        cursor.execute(query)
        temp = cursor.fetchall()
        for i in temp:
            print i
        customerMerchantSocket.send("Revealed")
    
    else:
        print "Exitting the Customer Portal"

        
pubkey, privkey = keygen(2 ** 128)
factor = blindingfactor(pubkey[1])

if __name__ == '__main__':


    print "Welcome to the Customer Portal."    
    #os.system("rm /home/neeraj/Desktop/209_Project/*txt")
    createBankConnection()

    customerMerchantSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    customerMerchantSocket.connect(('localhost', 9500))
    createMerchantConnection()   

    createnewOrder()

    print "Exitting you from the Customer Section"

    # First Bank Program has to run, Because bank program listens to the Inputs