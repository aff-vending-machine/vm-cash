# import serial.tools.list_ports

# def list_usb_com_ports():
#     com_ports = serial.tools.list_ports.comports()
#     print("A: ", com_ports)
#     usb_com_ports = [port.device for port in com_ports if "USB" in port.description]
#     return usb_com_ports

# if __name__ == "__main__":
#     usb_com_ports = list_usb_com_ports()
#     if usb_com_ports:
#         print("USB COM ports found:")
#         for port in usb_com_ports:
#             print(port)
#     else:
#         print("No USB COM ports found.")
import logging
import subprocess
import re
# from subprocess import call
# from subprocess import check_output

log_format = "%(asctime)s - %(levelname)s:%(message)s"
logging.basicConfig(level='INFO', format=log_format)

print("Checking USB-Serial Port...")
ttyLists = []
result = None

try:
        result = subprocess.check_output(('dmesg | grep tty'),shell=True).decode('utf-8')
        # print("::", result, "| ", type(result))
except subprocess.CalledProcessError as e:
    print(e.output)
split = result.split('\n')
for line in split:
    matchObj = re.match( r'.*: (.*) now attached to (.*)', line, re.M|re.I )
    if matchObj:
        logging.info('{0} is {1}'.format(matchObj.group(1), matchObj.group(2)))
        if matchObj.group(1) == 'FTDI USB Serial Device converter':
            ttyLists.append('/dev/%s' % matchObj.group(2))
        elif matchObj.group(1) == 'pl2303 converter':
            # global GPSUSB
            GPSUSB = '/dev/%s' % matchObj.group(2)
        elif matchObj.group(1) == 'ch341-uart converter':
            # global ArduinoUSB
            ArduinoUSB = '/dev/%s' % matchObj.group(2)
    else:
        pass
print("GPSUSB: ", GPSUSB)
print("ArduinoUSB: ", ArduinoUSB)
for list in ttyLists:
    resultList = subprocess.check_output(('udevadm info --name=%s --attribute-walk | grep ATTRS{bInterfaceNumber}' % list),shell=True)[-4:-2]
  
#     if resultList == '00':
#         global TaikoUSB
#         TaikoUSB = list
#         logging.info('TaikoUSB is ' + list)
#     elif resultList == '01':
#         global MEIUSB
#         MEIUSB = list
#         logging.info('MEIUSB is ' + list)
#     elif resultList == '02':
#         global MOTORUSB
#         MOTORUSB = list
#         logging.info('MOTORUSB is ' + list)
#     elif resultList == '03':
#         global GPSUSB
#         GPSUSB = list
#         logging.info('GPSUSB is ' + list)