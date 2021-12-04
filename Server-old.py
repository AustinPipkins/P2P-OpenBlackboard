 
  
# server 11-17-2021
# server:
import socket
import _thread
import time
import copy


all_ip = ["null"]
ip_times = [0]

my_ip = "131.151.89.233"

def addNew():
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.bind((my_ip, 9299))
    serv.listen(5)
    print("Server listening...")

    while True:
        conn, addr = serv.accept()
        from_client = ""

        while True:
            data = conn.recv(4096)
            if not data:
                break
            from_client += data.decode()
            print(from_client)

            if (addr[0] in all_ip) == False:
                all_ip.append(addr[0])
                ip_times.append(0)
            message = addr[0] + "=" + "=".join(all_ip)
            conn.send(message.encode())
            print("all ip: ", all_ip)

        conn.close()
        print("disconnect")


def recvHeartBeat():
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.bind((my_ip, 9297))
    serv.listen(5)

    while True:
      try:
            conn, addr = serv.accept()
            from_client = ""
            print(all_ip, ip_times, "DEBUG")

            while True:
                data = conn.recv(4096)
                if not data:
                    break
                from_client += data.decode()
                if from_client == "HEARTBEAT":
                    ip_times[all_ip.index(addr[0])] = 0
                    print("heartbeart from", addr[0])

            conn.close()
      except:
          pass


def pruneIPList():
    while 1:
        time.sleep(1)
        print(all_ip, ip_times, "DEBUG")
        ip_to_pop = []
        for i in range(1, len(ip_times)):
            ip_times[i] += 1
            if ip_times[i] > 15:
                ip_to_pop.append(i)

        for i in range(len(ip_to_pop) - 1, -1, -1):
            ip_times.pop(ip_to_pop[i])
            all_ip.pop(ip_to_pop[i])


try:
    _thread.start_new_thread(addNew, ())
    _thread.start_new_thread(recvHeartBeat, ())
    _thread.start_new_thread(pruneIPList, ())
except:
    print("Error: unable to start thread")

while 1:
    pass

  
  
