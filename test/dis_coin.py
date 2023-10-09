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

c = time.time()
mei_sts = mei.MEI_Disable(serC)
d = time.time()
print("ddd: ", d-c)

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
# # serC.write(unhexlify(disable_constant))
# serC.write(b'\x0c\x00\x00\x00\x00')
# print("Sending Disable:", disable_constant)
# c = 0
# while(1):
#     inw8 = serC.inWaiting()
#     if inw8 > 0:
#         response = serC.read_until('\r')
#         response = "".join(response.split('\n'))
#     else:
#         response = serC.readline()
#     print("response1: ", repr(response))
#     print("aaaa: ", response == b'')
#     if response == b'':
#         c += 1
#     if c == 5:
#         break