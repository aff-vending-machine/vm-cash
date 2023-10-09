import constants
import time
from binascii import unhexlify
import logging

log_format = "%(asctime)s - %(levelname)s:%(message)s"
logging.basicConfig(level='INFO', format=log_format)

def CBA_Disable(serT):
    counter = 0
    serT.write(unhexlify((constants.CBA_DISABLE)))
    response = ''
    while counter < 5:
        print("Sending CBA DISABLE:", (constants.CBA_DISABLE))
        inw8 = serT.inWaiting()
        if inw8 > 0:
            try:
                # response = serT.read_until('\r')
                response = serT.readline()
                response = response.decode('utf-8')
                response = "".join(response.split(' '))
                response = "".join(response.split('\r'))
                response = "".join(response.split('\n'))
                # serT.flushInput()
            except Exception as e:
                print("Reader Exception in CBA DISABLE Responding:"+str(e))
                return False,False   ### No Response with Error!

            print("CBA DISABLE Resp = ",repr(response))
            if response != b'':
                if response[:2] == "FF":
                    return True,False   ### Response, but Fail
                elif response[:2] == "00":
                    return True,True    ### Response with Success
        else:
            counter = counter + 1
        time.sleep(0.1)
    return False,True  ### No Response, No Error

def CBA_Enable(serT, bill_config):
    counter = 0
    # serT.write(unhexlify((constants.CBA_ENABLE)))
    serT.write(unhexlify(bill_config))
    response = ''
    while counter < 5:
        print("Sending CBA ENABLE:", (bill_config))
        inw8 = serT.inWaiting()
        if inw8 > 0:
            try:
                # response = serT.read_until('\r')
                response = serT.readline()
                response = response.decode('utf-8')
                response = "".join(response.split(' '))
                response = "".join(response.split('\r'))
                response = "".join(response.split('\n'))
                # serT.flushInput()
            except Exception as e:
                print("Reader Exception in CBA ENABLE Responding:"+str(e))
                return False,False   ### No Response with Error!

            print("CBA ENABLE Resp = ",repr(response))
            if response != '':
                if response[:2] == "FF":
                    return True,False   ### Response, but Fail
                elif response[:2] == "00":
                    return True,True    ### Response with Success
        else:
            counter = counter + 1
        time.sleep(0.1)
    return False,True  ### No Response, No Error
