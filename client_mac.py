import json, time, subprocess, os,sys
import zmq
context = zmq.Context()


# Server settings
ip = '129.175.80.146'
port = 12100

socket=context.socket(zmq.REQ)
socket.connect("tcp://{0}:{1}".format(ip,port))
#socket.setsockopt(zmq.RCVTIMEO,100)
#socket.setsockopt(zmq.SNDTIMEO,100)

# Start remote kernel
socket.send(b'start_kernel')
ans = socket.recv()
ans = json.loads(ans)
if ans['reply']!='ok':
    print("Error : Could not start kernel or get kernel json file")
    sys.exit()
id = ans['id']
with open('kernel.json','w') as f:
    f.write(ans['kernel_json'])

# Connect to kernel
proc = subprocess.run(["/Users/je/anaconda3/bin/jupyter", "qtconsole", "--existing=kernel.json"])

# Kill remote kernel
socket.send('stop_kernel {0}'.format(id).encode())
ans = socket.recv()
ans = json.loads(ans)
if ans['reply']!='ok':
    print("Error : Could not stop kernel")


