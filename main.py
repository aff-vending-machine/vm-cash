import falcon
import logging
import json
import serial
import time
import datetime
import mei
import cba
import threading
from queue import Queue

log_format = "%(asctime)s - %(levelname)s:%(message)s"
logging.basicConfig(level='INFO', format=log_format)

serC = serial.Serial(
        "/dev/ttyUSB0",
        baudrate=9600,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout = 1
        )

threads = []
cond = threading.Condition()
timeout_queue = Queue()
msg_queue = Queue()

global coin_recv_value, bill_recv_value, coin_exchange_list
coin_recv_value = 0
bill_recv_value = 0
coin_exchange_list = [0, 0, 0]    #1,5,10

coin_recv_timeout = 65

def coin_collecting(timeout_queue, msg_queue, serT, cond):
    tname = threading.current_thread().name
    logging.info("Thread waiting for event: %s", tname)
    
    previous_status = ''
    thread_status = ''

    coin_timeout = 0
    coin_value = 0
    startt = 0

    global coin_recv_value, bill_recv_value, coin_exchange_list
    
    while True:
        if not timeout_queue.empty():
            coin_timeout = timeout_queue.get()
            logging.info("coin_collecting got event: %s, | %s | %s" % (tname, coin_timeout, datetime.datetime.now().isoformat()))
            timeout_queue.task_done()
        
        if not msg_queue.empty():
            thread_status = msg_queue.get()
            logging.info("Thread_status got event: %s, %s, | %s" % (tname, thread_status, datetime.datetime.now().isoformat()))
            msg_queue.task_done()

        if coin_timeout > 0:
            if thread_status == 'start':
                if previous_status == '' or previous_status == 'stop':
                    startt = time.time()
                    coin_value = 0
                    bill_value = 0
                    previous_status = thread_status
                
                try:
                    inw8 = serT.inWaiting()
                    if inw8 > 0:
                        serT.flushOutput()
                        reader = serT.readline()
                        reader = reader.decode('utf-8')
                        reader = "".join(reader.split(' '))
                        reader = "".join(reader.split('\r'))
                        reader = "".join(reader.split('\n'))
                        serT.flushInput()
                    else:
                        reader = False

                    coin_recv_value = coin_value
                    bill_recv_value = bill_value

                    list1b_box = ['0840','0841']
                    list1b_tube = ['0850','0851']
                    list5b_box = ['0843','0844']
                    list5b_tube = ['0853','0854']
                    list10b_box = ['0845']
                    list10b_tube = ['0855']

                    list20b = ['3080']
                    list50b = ['3081']
                    list100b = ['3082']
                    list500b = ['3083']
                    list1000b = ['3084']

                    if reader:
                        cash_value = reader[:4]
                        if cash_value in list1b_box or cash_value in list1b_tube:
                            logging.info("1 Baht")
                            coin_value += 1
                        elif cash_value in list5b_box or cash_value in list5b_tube:
                            logging.info("5 Baht")
                            coin_value += 5
                        elif cash_value in list10b_box or cash_value in list10b_tube:
                            logging.info("10 Baht")
                            coin_value += 10

                        elif cash_value in list20b:
                            logging.info("20 Baht")
                            bill_value += 20
                        elif cash_value in list50b:
                            logging.info("50 Baht")
                            bill_value += 50
                        elif cash_value in list100b:
                            logging.info("100 Baht")
                            bill_value += 100
                        elif cash_value in list500b:
                            logging.info("500 Baht")
                            bill_value += 500
                        elif cash_value in list1000b:
                            logging.info("1000 Baht")
                            bill_value += 1000

                    coin_recv_value = coin_value
                    bill_recv_value = bill_value

                except Exception as e:
                    logging.error("Exception in CBA recv thread: ",str(e))

            elif thread_status == 'stop'and previous_status == 'start':
                coin_recv_value = coin_value
                coin_timeout = 0
                previous_status = thread_status

            elif thread_status == 'reset':
                coin_recv_value = 0
                coin_exchange_list = [0, 0, 0]
                previous_status = thread_status

            endt = time.time()
            # logging.info("Coin Value: %r | DiffTime: %r" % (coin_recv_value, endt - startt))
            if (endt - startt) > coin_timeout:
                coin_timeout = 0
            time.sleep(0.05)
        time.sleep(0.02)

t = threading.Thread(target=coin_collecting, args=(timeout_queue, msg_queue, serC, cond,))
threads.append(t)

timeout_queue.put(0)
msg_queue.put(None)
t.start()

class CoinResource:
    def on_get(self, req, resp):
        resp_data = {
                    'success': True, 
                    'messages': 'Welcome to Coin Service'
                    }
        logging.critical("response_data.. : %r"% (resp_data))
        resp.text = json.dumps(resp_data)
        falcon.HTTPStatus(status=200)
        return
    
    def on_post(self, req, resp):
        try:
            rawReq = req.bounded_stream.read().decode('utf-8')
            dataReq = json.loads(rawReq)
        except:
            dataReq = json.loads("{}")
            resp_data = {
                        'success': False,
                        'messages': 'Coin Service: Wrong param data'
                        }
            resp.text = json.dumps(resp_data)
            falcon.HTTPStatus(status=200)
            return

        logging.info('dataReq: %r', dataReq)
        coin_cmd = dataReq.get('command')
        value_data = dataReq.get('change_value')

        ### define response data ###
        resp_data = {
            'success': False,
            'messages': 'Coin Wrong command'
            }
        global coin_recv_value
        try:
            serC.flushInput()
            #### Action 0 ####
            if coin_cmd == 'info':
                a = time.time()
                mei_sts = mei.MEI_info(serC)
                b = time.time()
            elif coin_cmd == 'status':
                a = time.time()
                mei_sts = mei.MEI_status(serC)
                b = time.time()

            #### Action 1 ####
            elif coin_cmd == 'enable':
                a = time.time()
                mei_sts = mei.MEI_Enable(serC)
                b = time.time()
                timeout_queue.put(coin_recv_timeout)
                msg_queue.put('start')
            elif coin_cmd == 'disable':
                timeout_queue.put(1)
                msg_queue.put('stop')
                a = time.time()
                mei_sts = mei.MEI_Disable(serC)
                b = time.time()
            elif coin_cmd == 'reset':
                timeout_queue.put(1)
                msg_queue.put('reset')
                resp_data = {
                        'success': True,
                        'action': 1,
                        'messages': 'coin acceptor value reset successful'
                        }
            #### Action 2 ####
            elif coin_cmd == 'received':
                resp_data = {
                        'success': True,
                        'action': 2,
                        'messages': 'coin received value successful',
                        'coin_value': coin_recv_value,
                        'bill_value': bill_recv_value
                        }
            elif coin_cmd == 'payout':
                a = time.time()
                mei_sts = mei.MEI_payout(serC, value_data)
                b = time.time()

        except Exception as e:
            logging.info("Coin Service: Error!: %r", e)
            resp_data = {
                        'success': False,
                        'messages': 'Coin Service: Error'
                        }
            
        #### Action 0 ####
        if coin_cmd == 'status' or coin_cmd == 'info':
            if mei_sts[0]:
                resp_data = {
                    'success': True,
                    'action': 0,
                    'messages': mei_sts[1]
                    }
            else:
                resp_data = {
                    'success': False,
                    'action': 0,
                    'messages': mei_sts[1]
                    }

        #### Action 1 ####
        elif coin_cmd == 'enable' or coin_cmd == 'disable':
            if mei_sts[0]:
                if mei_sts[1]:
                    msgs = coin_cmd + ' - changed successful'
                else:
                    msgs = coin_cmd + ' - changed fail, try again..'
                resp_data = {
                        'success': True,
                        'action': 1,
                        'messages': msgs,
                        'coin_value': coin_recv_value,
                        'time': b-a
                        }
            else:
                if mei_sts[1]:
                    msgs = 'No Response'
                else:
                    msgs = 'Serial Error'
                resp_data = {
                        'success': False,
                        'action': 1,
                        'messages': msgs
                        }

        #### Action 2 ####
        if coin_cmd == 'payout':    #### Need disable before payout
            if mei_sts[0]:
                if mei_sts[1]:
                    if mei_sts[2]:
                        msgs = coin_cmd + ' - successful'
                        coin_recv_value = coin_recv_value - mei_sts[2]
                    else:
                        msgs = coin_cmd + ' - fail, not enough exchange'    
                else:
                    msgs = coin_cmd + ' - fail, try again..'

                resp_data = {
                        'success': True,
                        'action': 2,
                        'messages': msgs,
                        'coin_value': coin_recv_value,
                        'time': b-a
                        }
            else:
                if mei_sts[1]:
                    msgs = 'No Response'
                else:
                    msgs = 'Serial Error'
                resp_data = {
                        'success': False,
                        'action': 2,
                        'messages': msgs
                        }

        resp.text = json.dumps(resp_data)
        falcon.HTTPStatus(status=200)
        return

class BillResource:
    def on_get(self, req, resp):
        resp_data = {
                    'success': True, 
                    'messages': 'Welcome to Bill Service'
                    }
        logging.critical("response_data.. : %r"% (resp_data))
        resp.text = json.dumps(resp_data)
        falcon.HTTPStatus(status=200)
        return
    
    def on_post(self, req, resp):
        try:
            rawReq = req.bounded_stream.read().decode('utf-8')
            dataReq = json.loads(rawReq)
        except:
            dataReq = json.loads("{}")
            resp_data = {
                        'success': False,
                        'messages': 'Bill Service: Wrong param data'
                        }
            resp.text = json.dumps(resp_data)
            falcon.HTTPStatus(status=200)
            return

        logging.info('Bill dataReq: %r', dataReq)
        bill_cmd = dataReq.get('command')
        bill_config = dataReq.get('config')

        ### define response data ###
        resp_data = {
            'success': False,
            'messages': 'Bill Wrong command'
            }
        global bill_recv_value
        try:
            serC.flushInput()
            #### Action 1 ####
            if bill_cmd == 'enable':
                a = time.time()
                bill_recv_value = 0
                cba_sts = cba.CBA_Enable(serC, bill_config)
                b = time.time()
            elif bill_cmd == 'disable':
                a = time.time()
                cba_sts = cba.CBA_Disable(serC)
                b = time.time()

        except Exception as e:
            logging.info("Bill Service: Error!: %r", e)
            resp_data = {
                        'success': False,
                        'messages': 'Bill Service: Error'
                        }

        if bill_cmd == 'enable' or bill_cmd == 'disable':
            if cba_sts[0]:
                if cba_sts[1]:
                    msgs = bill_cmd + ' - changed successful'
                else:
                    msgs = bill_cmd + ' - changed fail, try again..'
                resp_data = {
                        'success': True,
                        'action': 1,
                        'messages': msgs,
                        'bill_value': bill_recv_value,
                        'time': b-a
                        }
            else:
                if cba_sts[1]:
                    msgs = 'No Response'
                else:
                    msgs = 'Serial Error'
                resp_data = {
                        'success': False,
                        'action': 1,
                        'messages': msgs
                        }

        resp.text = json.dumps(resp_data)
        falcon.HTTPStatus(status=200)
        return
    
#### Falcon V3.0 ####
api = falcon.App(cors_enable=True)
api = falcon.App(middleware=falcon.CORSMiddleware(
    allow_origins='*', allow_credentials='*'))

api.add_route('/api/v1/coin', CoinResource())
api.add_route('/api/v1/bill', BillResource())

'''
fuser -k 80/tcp

Linux:
gunicorn -b :80 main:api

windows:
waitress-serve --port=80 main:api
'''