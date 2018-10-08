import json, subprocess, os
import zmq
context = zmq.Context()

# get path
path = os.path.dirname(__file__)
os.getcwd(path)

# Server settings
ip = '129.175.80.146'
port = 12100

socket=context.socket(zmq.REQ)
socket.connect("tcp://{0}:{1}".format(ip,port))
socket.setsockopt(zmq.RCVTIMEO,100)
socket.setsockopt(zmq.SNDTIMEO,100)

# Start remote kernel
socket.send(b'start_kernel')
ans = socket.recv()
ans = json.decode(ans)
if ans['reply']!='ok':
    print("Error : Could not start kernel or get kernel json file")
    return
id = ans['id']
with open('kernel.json','w') as f:
    f.write(ans['kernel_json'])

# Connect to kernel
proc = subprocess.run("jupyter qtconsole --existing=kernel.json")

# Kill remote kernel
socket.send(b'stop_kernel')
ans = socket.recv()
if ans['reply']!='ok':
    print("Error : Could not stop kernel")


