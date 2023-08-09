import falcon
import logging
import json
import serial
import time
import datetime
import mei
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

global recv_value, coin_exchange_list
recv_value = 0
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

    global recv_value, coin_exchange_list
    

    while True:
        # print("IN Starttttttttt ")
        if not timeout_queue.empty():
            coin_timeout = timeout_queue.get()
            logging.info("coin_collecting got event: %s, | %s | %s" % (tname, coin_timeout, datetime.datetime.now().isoformat()))
            timeout_queue.task_done()
        
        if not msg_queue.empty():
            thread_status = msg_queue.get()
            logging.info("Thread_status got event: %s, %s, | %s" % (tname, thread_status, datetime.datetime.now().isoformat()))
            msg_queue.task_done()

        if coin_timeout > 0:
            # print("Threadddddddddddddd: %s, %s | %s" % (thread_status, repr(previous_status), previous_status == ''))
            if thread_status == 'start':
                if previous_status == '' or previous_status == 'stop':
                    startt = time.time()
                    coin_value = 0
                    previous_status = thread_status
                
                try:
                    inw8 = serT.inWaiting()
                    if inw8 > 0:
                        reader = serT.read_until('\r')
                        # reader = "".join(reader.split('\n'))
                        # serT.flushInput()
                        # serT.flushOutput()
                    else:
                        reader = False

                    recv_value = coin_value
                    # logging.info("Reader: %s | Coin_Value: %s | Coin_Timeout: %s" % (repr(reader), coin_value, coin_timeout))
                    list1b_box = [b'40',b'41']
                    list1b_tube = [b'50',b'51']
                    list5b_box = [b'43',b'44']
                    list5b_tube = [b'53',b'54']

                    if reader:
                        # print("Reader[:2]: %s ,Reader[3:5]: %s " % (reader[:2], reader[3:5]))
                        if reader[:2] == b'08':
                            if reader[3:5] in list1b_box:
                                logging.info("1 Baht, Coin Box")
                                coin_value += 1
                            elif reader[3:5] in list1b_tube:
                                logging.info("1 Baht, Tube")
                                coin_value += 1
                                coin_exchange_list[0] += 1
                            elif reader[3:5] == b'42':
                                logging.info("2 Baht, Coin Box")
                                coin_value += 2
                            elif reader[3:5] in list5b_box:
                                logging.info("5 Baht, Coin Box")
                                coin_value += 5
                            elif reader[3:5] in list5b_tube:
                                logging.info("5 Baht, Tube")
                                coin_value += 5
                                coin_exchange_list[1] += 1
                            elif reader[3:5] == b'45':
                                logging.info("10 Baht, Coin Box")
                                coin_value += 10
                            elif reader[3:5] == b'55':
                                logging.info("10 Baht, Tube")
                                coin_value += 10
                                coin_exchange_list[2] += 1
                        recv_value = coin_value
                except Exception as e:
                    logging.error("Exception in mei recv thread: ",str(e))

            elif thread_status == 'stop'and previous_status == 'start':
                # print("Thread Stopppppppppppp")
                recv_value = coin_value
                coin_timeout = 0
                previous_status = thread_status

            elif thread_status == 'reset':
                # print("Thread Stopppppppppppp")
                recv_value = 0
                coin_exchange_list = [0, 0, 0]
                previous_status = thread_status

            endt = time.time()
            # logging.info("Coin Value: %r | DiffTime: %r" % (recv_value, endt - startt))
            if (endt - startt) > coin_timeout:
                coin_timeout = 0
            time.sleep(0.1)
        time.sleep(0.01)

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

        logging.critical('dataReq: %r', dataReq)
        coin_cmd = dataReq.get('command')
        value_data = dataReq.get('value')

        ### define response data ###
        resp_data = {
            'success': False,
            'messages': 'Wrong command'
            }
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
                global recv_value
                recv_value = 0
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
                # time.sleep(0.1)
                # a = time.time()
                # mei_sts = mei.MEI_Disable(serC)
                # b = time.time()

            #### Action 2 ####
            elif coin_cmd == 'received':
                resp_data = {
                        'success': True,
                        'action': 2,
                        'messages': 'coin received value successful',
                        'value': recv_value
                        # 'exchange_list': coin_exchange_list,
                        # 'exchangeable': exchangeable_value
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
                        'value': recv_value,
                        # 'exchange_list': coin_exchange_list,
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
        if coin_cmd == 'payout':
            if mei_sts[0]:
                if mei_sts[1]:
                    if mei_sts[2]:
                        msgs = coin_cmd + ' - successful'
                        recv_value = recv_value - mei_sts[2]
                    else:
                        msgs = coin_cmd + ' - fail, not enough exchange'    
                else:
                    msgs = coin_cmd + ' - fail, try again..'

                resp_data = {
                        'success': True,
                        'action': 2,
                        'messages': msgs,
                        'value': recv_value,
                        # 'exchange_list': coin_exchange_list,
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

#### Falcon V3.0 ####
api = falcon.App(cors_enable=True)
api = falcon.App(middleware=falcon.CORSMiddleware(
    allow_origins='*', allow_credentials='*'))

api.add_route('/api/v1/coin', CoinResource())

'''
fuser -k 80/tcp

Linux:
gunicorn -b :80 main:api

windows:
waitress-serve --port=80 main:api
'''