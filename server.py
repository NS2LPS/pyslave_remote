import traceback, os, json
from subprocess import Popen, PIPE
from threading import Timer
import zmq

# Server settings
ip = '129.175.80.146'
port = 12100

# Kernel counter
counter = 1

# Kernel dict
proc_dict = {}

# Time out in sec for communication
timeout_sec = 10


class reply:
    @staticmethod
    def start_kernel():
        env = os.environ.copy()
        env['SLAVE_ID'] = counter
        proc = Popen('ipython kernel --profile=pyslave --ip={0}'.format(ip), stdout=PIPE, stderr=PIPE)
        out = ''
        timer = Timer(timeout_sec, proc.kill)
        try:
            print("Starting new kernel...")
            timer.start()
            while not proc.poll() and '.json' not in out:
                out = proc.stdout.readline()
        finally:
            print("Timeout")
            timer.cancel()
        if '.json' not in out:
            print('Error while starting kernel')
            print(p.stderr.read())
            print(out)
            return json.dumps({'reply':'error'})
        print("Kernel OK")
        fname = out.replace('--existing','').strip()
        fname = os.path.join(r'C:\Users\NS2-manip\AppData\Roaming\jupyter\runtime', fname)
        if not os.path.isfile(fname):
            print('Kernel file {0} not found'.format(fname))
            proc.kill()
            return json.dumps({'reply':'error'})
        with open(fname,'r') as f:
            out = f.read()
        proc_dict[counter] = proc
        counter += 1
        print("Kernel info sent back")
        return json.dumps({'reply':'ok','id':counter-1,'kernel_json':out})
    @staticmethod
    def stop_kernel(c):
        print("Stopping kernel {c}...".format(c))
        if c not in proc_dict:
            print('Unknown kernel id : {0}'.format(c))
            return json.dumps({'reply':'error'})
        proc_dict[c].kill()
        proc_dict[c].wait()
        del proc_dict[c]
        print("Kernel stopped")
        return json.dumps({'reply':'ok'})



# Infinite server loop
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:%s" % port)

while True:
    msg = socket.recv().decode()
    try:
        msg = msg.strip().split(' ')
        action = msg[0]
        answer = getattr(reply, action)(*msg[1:])
        socket.send(answer.encode())
    except:
        traceback.print_exc()
