import constants
import time
from binascii import unhexlify
import json
import logging
import serial

#logging.basicConfig(filename='/home/pi/Workspace/returnofthevending/log_mainV2/log_mei.log',level=logging.DEBUG,format='%(asctime)s %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p')
#logging.info('Start Main Program')

def MEI_info(serT):
    counter = 0
    serT.write(unhexlify((constants.MEI_INFO)))
    response = b''
    while counter < 3:
        print("Sending MEI Tube Info...:", (constants.MEI_INFO))
        inw8 = serT.inWaiting()
        print("MEI Status inw8 = ",repr(inw8))
        if inw8 > 0:
            try:
                response = serT.read_until('\r')
                # response = response.decode('utf-8')
                # response = "".join(response.split(' '))
                # response = "".join(response.split('\r'))
                # response = "".join(response.split('\n'))
                # serT.flushInput()
            except Exception as e:
                print("Reader Exception in MEI Info Responding:"+str(e))
                return False,False   ### No Response with Error!

            print("MEI Info Resp = ",repr(response))
            if response != b'':
                # print("Baht1 Tube 1 = ",response[6:8], " Baht1 Tube 2 = ",response[9:11], " Baht5 Tube 1 = ",response[15:17], " Baht5 Tube 2 = ",response[18:20], " Baht10 Tube 1 = ",response[21:23])
                # one_thb = int(response[6:8], 16) + int(response[9:11], 16)
                # five_thb = int(response[15:17], 16) + int(response[18:20], 16)
                # ten_thb = int(response[21:23], 16)

                # result = {'action': 2,'result': 'success','remain': 
                #           {'baht1': one_thb,
                #            'baht5': five_thb,
                #            'baht10': ten_thb
                #            }
                #         }
                return True, response.decode('utf-8')
        else:
            counter = counter + 1
        time.sleep(0.05)
    return False,True  ### No Response, No Error

def MEI_status(serT):
    counter = 0
    serT.write(unhexlify((constants.MEI_TUBE_POLL)))
    response = b''
    while counter < 5:
        print("Sending MEI Tube Status...:", (constants.MEI_TUBE_POLL))
        inw8 = serT.inWaiting()
        print("MEI Status inw8 = ",repr(inw8))
        if inw8 > 0:
            try:
                response = serT.read_until('\r')
                # response = response.decode('utf-8')
                # response = "".join(response.split(' '))
                # response = "".join(response.split('\r'))
                # response = "".join(response.split('\n'))
                # serT.flushInput()
            except Exception as e:
                print("Reader Exception in MEI Status Responding:"+str(e))
                return False,False   ### No Response with Error!

            print("MEI Status Resp = ",repr(response))
            if response != b'':
                '''
                01 Escrow Request
                02 Changer Payout Busy
                03 No Credit
                04 Defective Tube Sensor
                05 Double Arrival
                06 Acceptor Unplugged
                07 Tube Jam
                08 ROM Checksum Error
                09 Coin Routing Error
                0A Changer Busy
                0B Changer was Reset
                0C Coin Jam
                21 Coin not recognized/slug. Returned
                Upon startup one of these values below may be sent to the PC - These are the VMC Commands.
                08 Reset
                09 Status
                0A Tube Status
                0B Poll
                0C Coin Type
                0D Dispense
                '''
                # print("Baht1 Tube 1 = ",response[6:8], " Baht1 Tube 2 = ",response[9:11], " Baht5 Tube 1 = ",response[15:17], " Baht5 Tube 2 = ",response[18:20], " Baht10 Tube 1 = ",response[21:23])
                # one_thb = int(response[6:8], 16) + int(response[9:11], 16)
                # five_thb = int(response[15:17], 16) + int(response[18:20], 16)
                # ten_thb = int(response[21:23], 16)

                # result = {'baht1': one_thb,
                #            'baht5': five_thb,
                #            'baht10': ten_thb
                #         }
                return True, response.decode('utf-8')
        else:
            counter = counter + 1
        time.sleep(0.5)
    return False,True  ### No Response, No Error

# def MEI_recv(serT):
#     print("MEI Ready to Receive...")
#     #logging.info("Ready to read data From MEI")
#     try:
#         inw8 = serT.inWaiting()
#         if inw8 > 0:
#             reader = serT.read_until('\r')
#             # reader = "".join(reader.split('\n'))
#             serT.flushInput()
#             serT.flushOutput()
#         else:
#             reader = False
#         coin = 0
# #        dest = 'cashbox'
#         dest = 'invalidcoin'
#         list1B = ['40','41']
#         if reader:
# #            print("Coin Received, Data from MEI:", reader
#             #logging.info("Received:", reader)
#             if reader[:2] == "08":
#                 if reader[3:5] in list1B:
#                     coin = 1
#                     dest = 'cashbox'
#                     print("1 Baht, Coin Box")
#                     #logging.info("1 Baht, Coin Box")
#                 elif reader[3:5] == "50" or reader[3:5] == "51":
#                     coin = 1
#                     dest = 'tube'
#                     print("1 Baht, Tube")
#                     #logging.info("1 Baht, Tube")
#                 elif reader[3:5] == "42":
#                     coin = 2
#                     dest = 'cashbox'
#                     print("2 Baht, Coin Box")
#                     #logging.info("2 Baht, Coin Box")
#                 elif reader[3:5] == "43" or reader[3:5] == "44":
#                     coin = 5
#                     dest = 'cashbox'
#                     print("5 Baht, Coin Box")
#                     #logging.info("5 Baht, Coin Box")
#                 elif reader[3:5] == "53" or reader[3:5] == "54":
#                     coin = 5
#                     dest = 'tube'
#                     print("5 Baht, Tube")
#                     #logging.info("5 Baht, Tube")
#                 elif reader[3:5] == "45":
#                     coin = 10
#                     dest = 'cashbox'
#                     print("10 Baht, Coin Box")
#                     #logging.info("10 Baht, Coin Box")
#                 elif reader[3:5] == "55":
#                     coin = 10
#                     dest = 'tube'
#                     print("10 Baht, Tube")
#                     #logging.info("10 Baht, Tube")
#                 jsonStr = {'action':2, 'msg':str(coin), 'dest':dest}
#                 return json.dumps(jsonStr)
#             elif reader[:2] == "FF":
#                 jsonStr = {'action': 2,'result': 'fail','description': 'failed please try again'}
#                 return json.dumps(jsonStr)
#         time.sleep(0.1)
#     except Exception as e:
#         print("Exception in mei recv thread")
# #        time.sleep(2)
#         jsonStr = {'action': 2,'result': 'fail','description': 'failed please try again'}
#         return json.dumps(jsonStr)
#         #logging.info("Exception in mei recv thread")

def MEI_payout(serT,value):
    print("In MEI_Payout Thread")
    valueDec = int(float(value))
    valueHex = hex(valueDec).split('x')[-1]
    serT.flushInput()
    serT.flushOutput()
    time.sleep(0.3)
    serT.write(unhexlify("0F02"+str(valueHex).zfill(2)))
    print("Sending:","0F02"+str(valueHex).zfill(2))

    start = time.time()
    reader = ''
    while time.time()-start < 0.7:
        inw8 = serT.inWaiting()
        if inw8 > 0:
            start = time.time()
            reader = reader+ serT.read(inw8)

    if reader:
        print("Payout Resp:",reader)
        #logging.info("Payout 0F02:", reader)
    else:
        print("Payout 0F02 Timeout...")
        return False,None

    serT.flushInput()
    time.sleep(0.1)
    serT.write(unhexlify("0F03"))
    print("Sending: 0F03")
    time.sleep(0.4)

    start = time.time()
    while time.time()-start < 1:
        inw8 = serT.inWaiting()
        if inw8 > 0:
            start = time.time()
            reader = serT.readline()

    isPayout = False

    if reader:
        reader = "".join(reader.split('\r\n'))
        payValue = ''
        isAck = True
        print("Coin Payout Resp:", reader)
        #logging.info("Payout 0F03:", reader)   
        print(reader[:2] , reader[3:5],reader[6:8] ,reader[9:11], reader[12:14] , reader[15:17])
        if reader[:2] != "00":
            print("Pay",reader[:2],"1 Baht coin(s) from Tube 1")
            isPayout = True
            payValue = payValue + '1Bx' + str(int(reader[:2],16)) + ' '

        if reader[3:5] != "00":
            print("Pay",reader[3:5],"1 Baht coin(s) from Tube 2")
            isPayout = True
            payValue = payValue + '1Bx' + str(int(reader[3:5],16)) + ' '

        if reader[9:11] != "00":
            print("Pay",reader[9:11],"5 Baht coin(s) from Tube 3")
            isPayout = True
            payValue = payValue + '5Bx' + str(int(reader[9:11],16)) + ' '

        if reader[12:14] != "00":
            print("Pay",reader[12:14],"5 Baht coin(s) from Tube 4")
            isPayout = True
            payValue = payValue + '5Bx' + str(int(reader[12:14],16)) + ' '

        if reader[15:17] != "00":
            print("Pay",reader[15:17],"10 Baht coin(s) from Tube 5")
            isPayout = True
            payValue = payValue + '10Bx' + str(int(reader[15:17],16))

        serT.flushInput()

        if isPayout:
            return True,payValue
        else:
            return False,None
    else:
        print("Payout 0F03 Timeout...")
        return False,None

def MEI_Disable(serT):
    counter = 0
    serT.write(unhexlify((constants.MEI_DISABLE_ALL_COIN)))
    response = b''
    while counter < 3:
        print("Sending DISABLE:", (constants.MEI_DISABLE_ALL_COIN))
        inw8 = serT.inWaiting()
        if inw8 > 0:
            try:
                response = serT.read_until('\r')
                response = response.decode('utf-8')
                response = "".join(response.split(' '))
                response = "".join(response.split('\r'))
                response = "".join(response.split('\n'))
                serT.flushInput()
            except Exception as e:
                print("Reader Exception in MEI DISABLE Responding:"+str(e))
                return False,False   ### No Response with Error!

            print("MEI DISABLE Resp = ",repr(response))
            if response != b'':
                if response[:2] == "FF":
                    return True,False   ### Response, but Fail
                elif response[:2] == "00":
                    return True,True    ### Response with Success
        else:
            counter = counter + 1
        time.sleep(0.05)
    return False,True  ### No Response, No Error

def MEI_Enable(serT):
    counter = 0
    serT.write(unhexlify((constants.MEI_ENABLE_ALL_COIN)))
    response = b''
    while counter < 3:
        print("Sending ENABLE:", (constants.MEI_ENABLE_ALL_COIN))
        inw8 = serT.inWaiting()
        if inw8 > 0:
            try:
                response = serT.read_until('\r')
                response = response.decode('utf-8')
                response = "".join(response.split(' '))
                response = "".join(response.split('\r'))
                response = "".join(response.split('\n'))
                serT.flushInput()
            except Exception as e:
                print("Reader Exception in MEI ENABLE Responding:"+str(e))
                return False,False   ### No Response with Error!

            print("MEI ENABLE Resp = ",repr(response))
            if response != b'':
                if response[:2] == "FF":
                    return True,False   ### Response, but Fail
                elif response[:2] == "00":
                    return True,True    ### Response with Success
        else:
            counter = counter + 1
        time.sleep(0.05)
    return False,True  ### No Response, No Error
