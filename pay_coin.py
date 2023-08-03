import serial
import time
import mei
from binascii import unhexlify

serC = serial.Serial(
        "/dev/ttyUSB0",
        baudrate=9600,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout = 1
        )

a = time.time()
mei_sts = mei.MEI_paypay(serC, 5)
b = time.time()
print("eee: ", b-a)
time.sleep(2)

while(1):
    time.sleep(5)

# # mei.MEI_Enable(serC)
# enable_constant = "0CFFFFFFFF"
# serC.write(unhexlify(enable_constant))
# print("Sending Enable:", enable_constant)
# c = 0
# while(1):
#     response = serC.readline()
#     print("response2: ", repr(response))
#     print("aaaa: ", response == b'')
#     if response == b'':
#         c += 1
#     if c == 5:
#         break



# mei.MEI_Disable(serC)
# disable_constant = "0C00000000"
# serC.write(unhexlify(disable_constant))
# serC.write(b'\x0c\x00\x00\x00\x00')

# serC.write(unhexlify(constants.MEI_ENABLE_ALL_COIN))
# print("Sending Disable:", constants.MEI_ENABLE_ALL_COIN)
# c = 0
# while(1):
#     inw8 = serC.inWaiting()
#     print("inw8:", inw8)
#     response = b''
#     if inw8 > 0:
#         response = serC.read_until('\r')
#         response = response.decode('utf-8')
#         response = "".join(response.split(' '))
#         response = "".join(response.split('\r'))
#         response = "".join(response.split('\n'))
#         print("response1: ", repr(response))
#     else:
#         time.sleep(0.5)
#     #     response = serC.readline()
#     # print("aaaa: ", response == b'')
#     if response == b'':
#         c += 1
#     if c == 3:
#         break