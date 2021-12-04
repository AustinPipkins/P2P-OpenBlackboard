import socket
import _thread
import time
import copy
import multiprocessing
import math
from tkinter import *
import tkinter.font as tkFont
from tkinter import colorchooser
import urllib.request #

COLOR = "#FFFFFF"
DISPLAYNAME = "Anonymous"
SERVER_IP = "" #
strokeNum = 1
eraseMode = False
lineWidth = 2
firstServerConn = True
restart = True

def choose_color():
    global COLOR
    color_code = colorchooser.askcolor(title ="Choose color")
    T.config(bg = color_code[-1])
    COLOR = color_code[-1]

def enter(): #
    global SERVER_IP, DISPLAYNAME #
    SERVER_IP = e1.get() #
    if e2.get() != "":
      DISPLAYNAME = e2.get() #
    master.quit() #


while restart:
    SERVER_IP = ""
    
    master = Tk()

    gridRow = 0
    
    Label(master, text="Server IP\n(leave empty to host)").grid(row=gridRow) #
    e1 = Entry(master) #
    e1.grid(row=gridRow, column=1) #
    
    gridRow += 1
    
    if not firstServerConn:
        Label(master, text="Server connection failed! Try again.", fg='red').grid(row=gridRow)
        gridRow += 1
    firstServerConn = False
    
    Label(master, text="Display Name").grid(row=gridRow) #
    e2 = Entry(master) #
    e2.grid(row=gridRow, column=1) #
    
    gridRow += 1

    Button(master, 
              text='Pick Color', command=choose_color).grid(row=gridRow, 
                                                           column=0, 
                                                           sticky=W, 
                                                           pady=4)
    T = Text(master, height = 1, width = 15, state=DISABLED)
    T.grid(row=gridRow, column=1)
    
    gridRow += 3

    Button(master, 
              text='Enter', 
              command=enter).grid(row=gridRow, 
                                  column=1, 
                                  sticky=W, 
                                  pady=4)


    mainloop()

    master.destroy()
    #done with info grab


    #Startup server if needed
    if SERVER_IP == '':
        serv_all_ip = [] #
        serv_ip_times = [] #
        client_info = [] #


        SERVER_IP = urllib.request.urlopen('https://ident.me').read().decode('utf8') #

        def addNew():
            serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serv.bind((SERVER_IP, 9293)) #
            serv.listen(10)
            print("(SERVER) Server is listening...")

            while True:
                conn, addr = serv.accept()
                from_client = ""

                while True:
                    data = conn.recv(4096)
                    if not data:
                        break
                    from_client += data.decode()
                    info = from_client[5:-1] #
                    info = info.split(", ") #
                    display_name = info[0] #
                    color = info[1] #

                    print("(SERVER) New client request from:", addr[0]) #

                    if addr[0] in serv_all_ip:
                        ipIndex = serv_all_ip.index(addr[0])
                        serv_ip_times.pop(ipIndex)
                        serv_all_ip.pop(ipIndex)
                        client_info.pop(ipIndex)

                    if len(client_info) > 0: #
                        message = addr[0] + "=" + "=".join(client_info) #
                    else: #
                        message = addr[0] #

                    serv_all_ip.append(addr[0])
                    serv_ip_times.append(0)
                    client_info.append("$".join([addr[0], display_name, color])) #
                    
                    message = addr[0] + "=" + "=".join(client_info)
                    conn.send(message.encode())
                    print("(SERVER) Add client to all IPs:", serv_all_ip)

                conn.close()


        def recvHeartBeatS():
            serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serv.bind((SERVER_IP, 9292)) #
            serv.listen(10)

            while True:
                conn, addr = serv.accept()
                from_client = ""

                while True:
                    data = conn.recv(4096)
                    if not data:
                        break
                    from_client += data.decode()
                    if from_client == "HEARTBEAT":
                        try:
                            serv_ip_times[serv_all_ip.index(addr[0])] = 0
                            #print("(SERVER) Heartbeat from:", addr[0])
                        except:
                            pass

                conn.close()


        def pruneIPList():
            while True:
                time.sleep(1)
                ip_to_pop = []
                for i in range(0, len(serv_ip_times)):
                    serv_ip_times[i] += 1
                    if serv_ip_times[i] > 10:
                        ip_to_pop.append(i)

                for i in range(len(ip_to_pop) - 1, -1, -1):
                    print("(SERVER)", serv_all_ip[ip_to_pop[i]], "disconnected")
                    serv_ip_times.pop(ip_to_pop[i])
                    serv_all_ip.pop(ip_to_pop[i])
                    client_info.pop(ip_to_pop[i])
                    print("(SERVER) Remove client from all IPs:", serv_all_ip)


        try:
            _thread.start_new_thread(addNew, ())
            _thread.start_new_thread(recvHeartBeatS, ())
            _thread.start_new_thread(pruneIPList, ())
        except:
            print("Error: Unable to start server threads")

    # Give time for server start up
    time.sleep(1)
    
    # Server connection
    try:
        # create a socket object
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # connection to hostname on the port.
        client.connect((SERVER_IP, 9293)) #
        print("Client connected to server")

        # Receive no more than 1024 bytes
        message = "NEW (" + DISPLAYNAME + ", " + COLOR + ")" #
        client.send(message.encode())

        from_server = client.recv(4096)
        client.close()
        restart = False
    except:
        pass
        
# Startup client app
app = Tk()
app.configure(background="#202020")
app.geometry("1040x900")
canvas = Canvas(app, bg='black', width=700, height=500, cursor='tcross')
canvas.place(x=50,y=250)

def get_x_and_y(event):
    global lasx, lasy
    if eraseMode:
        canvas.create_oval((event.x-1, event.y-1, event.x+1, event.y+1), 
                    outline='black',
                    width=20,
                    tags=(COLOR, COLOR + str(strokeNum)))
        message="ERASE (" + str(event.x-1) + ", " + str(event.y-1) + ", " + str(event.x+1) + ", " + str(event.y+1) + ", " +COLOR+ ", " + str(strokeNum) + ", 1, 2, 2)"
    elif lineWidth > 2:
        canvas.create_oval((event.x-1, event.y-1, event.x+1, event.y+1), 
                    outline=COLOR,
                    width=lineWidth,
                    tags=(COLOR, COLOR + str(strokeNum)))
        message="PLOT (" + str(event.x-1) + ", " + str(event.y-1) + ", " + str(event.x+1) + ", " + str(event.y+1) + ", " +COLOR+ ", " + str(strokeNum) + ", " + str(lineWidth) + ", 1, 2, 2)"
    else:
        canvas.create_line((event.x-1, event.y-1, event.x+1, event.y+1),
                        fill=COLOR, 
                        width=lineWidth,
                        tags=(COLOR, COLOR + str(strokeNum)))
        message="PLOT (" + str(event.x-1) + ", " + str(event.y-1) + ", " + str(event.x+1) + ", " + str(event.y+1) + ", " +COLOR+ ", " + str(strokeNum) + ", " + str(lineWidth) + ", 0, 0, 0)"
    lasx, lasy = event.x, event.y
    broadcast(message, 9298)

def draw_smth(event):
    global lasx, lasy, strokeNum, eraseMode, lineWidth
    px = lasx
    py = lasy
    
    if eraseMode or lineWidth == 10:
        xGap = event.x - lasx
        yGap = event.y - lasy
        if abs(xGap) > abs(yGap):
            numSteps = math.ceil(abs(xGap) / 3)
            if numSteps == 0:
                numSteps = 1
            xStep = xGap / numSteps
            yStep = yGap / numSteps
        else:
            numSteps = math.ceil(abs(yGap) / 3)
            if numSteps == 0:
                numSteps = 1
            xStep = xGap / numSteps
            yStep = yGap / numSteps
    
    if eraseMode:
        for i in range(numSteps):
            canvas.create_oval((int(px), int(py), int(px+xStep), int(py+yStep)), 
                        outline='black',
                        width=20,
                        tags=(COLOR, COLOR + str(strokeNum)))
            px += xStep
            py += yStep
        message="ERASE (" + str(lasx) + ", " + str(lasy) + ", " + str(event.x) + ", " + str(event.y) + ", " +COLOR+ ", " + str(strokeNum) + ", " + str(numSteps) + ", " + str(xStep) + ", " + str(yStep) + ")"
    elif lineWidth > 2:
        for i in range(numSteps):
            canvas.create_oval((int(px), int(py), int(px+xStep), int(py+yStep)), 
                        outline=COLOR,
                        width=lineWidth,
                        tags=(COLOR, COLOR + str(strokeNum)))
            px += xStep
            py += yStep
        message="PLOT (" + str(lasx) + ", " + str(lasy) + ", " + str(event.x) + ", " + str(event.y) + ", " +COLOR+ ", " + str(strokeNum) + ", " + str(lineWidth) + ", " + str(numSteps) + ", " + str(xStep) + ", " + str(yStep) + ")"
    else:
        canvas.create_line((px, py, event.x, event.y),
                        fill=COLOR, 
                        width=lineWidth,
                        tags=(COLOR, COLOR + str(strokeNum)))
        message="PLOT (" + str(px) + ", " + str(py) + ", " + str(event.x) + ", " + str(event.y) + ", " +COLOR+ ", " + str(strokeNum) + ", " + str(lineWidth) + ", 0, 0, 0)"
    
    lasx, lasy = event.x, event.y

    broadcast(message, 9298)

def doneStroke(event):
    global strokeNum
    strokeNum += 1
    message = "LOG" # To show where message came from
    broadcast(message, 9298)

def clear_color():
    global strokeNum
    if strokeNum > 1:
        canvas.delete(COLOR)
        strokeNum = 1
        message = "CLEAR (" + COLOR + ")"
        broadcast(message, 9298)

def undo_stroke():
    global strokeNum
    if strokeNum > 1:
        strokeNum -= 1
        canvas.delete(COLOR + str(strokeNum))
        message = "CLEAR (" + COLOR + str(strokeNum) + ")"
        broadcast(message, 9298)

def erase_mode():
    global eraseMode
    canvas.config(cursor='dotbox')
    eraseMode = True

def small_width():
    global lineWidth, eraseMode
    lineWidth = 2
    if eraseMode:
        canvas.config(cursor='tcross')
        eraseMode = False

def large_width():
    global lineWidth, eraseMode
    lineWidth = 10
    if eraseMode:
        canvas.config(cursor='tcross')
        eraseMode = False
            
photoUndo = PhotoImage(file = "undo.png")
photoClear = PhotoImage(file = "clear.png")
photoErase = PhotoImage(file = "erase.png")
photoSmall = PhotoImage(file = "small.png")
photoLarge = PhotoImage(file = "large.png")
photoLogo = PhotoImage(file = "LOGO.png")

logo = Button(app, image=photoLogo, bg="black")
logo.place(x=110,y=25)

clear = Button(app, text='Clear', image=photoClear, command=clear_color, bg="black")
clear.place(x=50,y=775)

undo = Button(app, text='Undo', image=photoUndo, command=undo_stroke, bg="black")
undo.place(x=250,y=775)

erase = Button(app, text='Erase', command=erase_mode, image=photoErase, bg="black")
erase.place(x=450,y=775)

small = Button(app, text='Small', image=photoSmall, command=small_width, bg="black")
small.place(x=550,y=775)

large = Button(app, text='Large', image=photoLarge, command=large_width, bg="black")
large.place(x=650,y=775)

userFrame = Frame(app,
                  bg='black',
                  width=213,
                  height=604,
                  highlightbackground='lime',
                  highlightthickness=2) #
userFrame.place(x=770, y=250) #

userTitle = Label(userFrame, text='Online Users', fg='lime', bg='black') #
userTitle.place(x=10, y=0) #

userTitleFont = tkFont.Font(userTitle, userTitle.cget('font')) #
fontName = userTitleFont.cget('family') #
userTitleFont.configure(underline=True, size=22) #
userTitle.configure(font=userTitleFont) #

usernameFrame = Frame(userFrame, bg='black', width=193, height=545) #
usernameFrame.place(x=10, y=50) #
    
canvas.bind("<Button-1>", get_x_and_y)
canvas.bind("<B1-Motion>", draw_smth)
canvas.bind("<B1-ButtonRelease>", doneStroke)


def sendToIp(ip, port, msg):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connection to hostname on the port.
    try:
        client.connect((ip, port))
        client.send(msg.encode())
        client.close()
        return True
    except:
      	return False



info = from_server.decode().split("=") #
my_ip = info[0] #

infoFrame = Frame(app,
                  bg="#202020",
                  width=1000,
                  height=95) #
infoFrame.place(x=50, y=150) #

serverNameText = 'Server IP: ' + SERVER_IP
if SERVER_IP == my_ip:
    serverNameText += ' (You are hosting)'
    
serverName = Label(infoFrame, text=serverNameText, fg='white', bg="#202020", font=(fontName, 25))
serverName.place(x=0, y=0)

displayName = Label(infoFrame, text='Username: '+DISPLAYNAME, fg=COLOR, bg="#202020", font=(fontName, 25))
displayName.place(x=0, y=50)

def allIpInit(all_ip):
  l = 3
  while(True):
    if(len(all_ip) > l):
      l=((l+1)*2)-1
      
    else:
      break
      
  for i in range(l):
    if(i >= len(all_ip)):
      all_ip.append("X")
  
      
  return l, all_ip



all_ip = [ k.split("$")[0] for k in info[1:]]



 #
ip_times = [] #
all_ip_length, all_ip = allIpInit(all_ip)
for i in range(len(all_ip)):
    if(all_ip[i] != "X"):
        ip_times.append(0)





users = [] #
if len(info) > 1: #
    users = info[1:] #
    for i in range(len(users)): #
        users[i] = users[i].split("$") #

photoGreenDot = PhotoImage(file = "goodCon.png") #
photoOrangeDot = PhotoImage(file = "badCon.png") #

userLabels = [] #
for i in range(len(users)): #
    online = Label(usernameFrame, image=photoGreenDot, highlightthickness=0, borderwidth=0) #
    online.place(x=0, y=5+(36*i)) #
    username = Label(usernameFrame,
                     text=users[i][1],
                     fg=users[i][2],
                     bg='black',
                     font=(fontName, 20)) #
    username.place(x=25, y=36*i) #
    userLabels.append((online, username)) #


print("My IP:", my_ip)
print("All peer IPs:", all_ip)

message = "ADD (" + DISPLAYNAME + ", " + COLOR + ")" #

 
#format for broadcast:
# BROADCAST=##=msg=port#
#msg is pure
def broadcast(msg, port, hopNum=-100, srcIndex=-1):
    global my_ip
    global all_ip
    global all_ip_length
    if((hopNum < 1) and (hopNum != -100)):
      return
    
    if(srcIndex == -1):
        srcIndex = all_ip.index(my_ip)

    if(hopNum == -100):
        hopNum = int((all_ip_length + 1) / 4) 
        
        
        
        
        
    if(all_ip[int((srcIndex + hopNum) % all_ip_length)] != "X"):
        #print("O HOP R", hopNum)
        m = "BROADCAST=" + str(hopNum) + "=" + msg + "=" + str(port)
        good = sendToIp(all_ip[int((srcIndex + hopNum) % all_ip_length)], port, m)
        
    else:
        #print("X HOP R", hopNum)
        broadcast(msg, port, hopNum=int(hopNum/2), srcIndex = int((srcIndex + hopNum) % all_ip_length))
        good = True

    if(not good):
        #print("X HOP R", hopNum)
        broadcast(msg, port, hopNum=int(hopNum/2), srcIndex = int((srcIndex + hopNum) % all_ip_length))

        
        
    if(all_ip[int((srcIndex - hopNum) % all_ip_length)] != "X"):
        #print("O HOP L", hopNum)
        m = "BROADCAST=" + str(hopNum) + "=" + msg + "=" + str(port)
        good = sendToIp(all_ip[int((srcIndex - hopNum) % all_ip_length)], port, m)
        
    else:
        #print("X HOP L", hopNum)
        broadcast(msg, port, hopNum=int(hopNum/2), srcIndex = int((srcIndex - hopNum) % all_ip_length))
        good = True

    if (not good):
        #print("X HOP L", hopNum)
        broadcast(msg, port, hopNum=int(hopNum/2), srcIndex = int((srcIndex - hopNum) % all_ip_length))
      
      

#msg is tainted BROADCAST=1=hello=9298
def relayMessage(msg):
    #print("RELAY OPEN")
    msg = msg.split("=")
    #broadcast(msg, port, hopNum=-100, srcIndex = -1)
    broadcast(msg[2], int(msg[3]), hopNum=math.floor(int(msg[1])/2), srcIndex=all_ip.index(my_ip))
    #print("RELAY CLOSE")


def removeIp(j):
    global all_ip
    global ip_times
    global all_ip_length
    
    ip_times.pop(j)
    all_ip.pop(j)
    
    all_ip.append("X")
    
    ipcnt = 0
    for ip in all_ip:
        if(ip != "X"):
            ipcnt += 1
            
    if(ipcnt == int(((all_ip_length+1)/2)-1)):
        for i in range(len(all_ip))[::-1]:
            if(all_ip[i] == "X"):
                all_ip.pop(i)
                all_ip_length -= 1


def addAllIp(ip):
  global all_ip_length
  global all_ip
  
  if(all_ip[-1] != "X"):
    prev = all_ip_length
    all_ip_length=((all_ip_length+1)*2)-1
    
    for i in range(all_ip_length):
      if(i >= len(all_ip)):
        all_ip.append("X")
      
  all_ip[all_ip.index("X")] = ip

   
  



for ip in all_ip:
    sendToIp(ip, 9299, message)
    print("Sent connection request to:", ip)




# IP CONVENTION:
# 9299: RECV NEW IP
# 9298: RECV CAVNAS UPDATES
	# PLOT: PLOT (x, y, x', y', color)
# 9297: RECV HEARTBEAT




def waitForNewIP():
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.bind((my_ip, 9299))
    serv.listen(10)

    while True:
        conn, addr = serv.accept()
        from_client = ""

        while True:
            data = conn.recv(4096)
            if not data:
                break
            from_client += data.decode()
            info = from_client[5:-1].split(", ") #
            display_name = info[0] #
            color = info[1] #
            print(">>>>>>>>>>>>>Accepted connection request from:", addr[0])

            message = "I see you from computer: " + my_ip

            conn.send(message.encode())
            if addr[0] in all_ip:
                ipIndex = all_ip.index(addr[0])
                ip_times.pop(ipIndex)
                removeIp(ipIndex)
                userLabels[ipIndex][0].destroy() #
                userLabels[ipIndex][1].destroy() #
                for j in range(ipIndex + 1, len(users)): #
                    users[j-1] = users[j] #
                    userLabels[j-1] = userLabels[j] #
                    userLabels[j-1][0].place(x=0, y=5+(36*(j-1))) #
                    userLabels[j-1][1].place(x=25, y=36*(j-1)) #
                users.pop() #
                userLabels.pop() #
                
            addAllIp(addr[0])
            ip_times.append(0)
            online = Label(usernameFrame, image=photoGreenDot, highlightthickness=0, borderwidth=0) #
            online.place(x=0, y=5+(36*len(users))) #

            
            username = Label(usernameFrame,
                             text=display_name,
                             fg=color,
                             bg='black',
                             font=(fontName, 20)) #
            username.place(x=25, y=36*len(users)) #
            userLabels.append((online, username)) #
            users.append([display_name, color]) #
            print("Add peer to all IPs:", all_ip)

        conn.close()




def waitForMessage():
    global canvas
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.bind((my_ip, 9298))
    serv.listen(10)

    while True:
        conn, addr = serv.accept()
        from_client = ""

        while True:
            data = conn.recv(4096)
            if not data:
                break
            from_client += data.decode()
            try:

                if(from_client[0:9] == "BROADCAST"):
                    relayMessage(from_client)
                    from_client = from_client.split("=")[2]

                if(from_client[0:4] == "PLOT"):
                    data = from_client[6:-1]
                    data = data.split(", ")
                    oldx = int(data[0])
                    oldy = int(data[1])
                    newx = int(data[2])
                    newy = int(data[3])
                    color=data[4]
                    stroke = data[5]
                    lineWidth = int(data[6])
                    numSteps = int(data[7])
                    xStep = float(data[8])
                    yStep = float(data[9])
                    if lineWidth > 2:
                        px = oldx
                        py = oldy
                        for i in range(numSteps):
                            canvas.create_oval((int(px), int(py), int(px+xStep), int(py+yStep)), 
                                        outline=color,
                                        width=lineWidth,
                                        tags=(color, color + str(stroke)))
                            px += xStep
                            py += yStep
                    else:
                        canvas.create_line(oldx, oldy, newx, newy, fill=color, width=lineWidth, tags=(color, color + str(stroke)))
                elif(from_client[0:5] == "CLEAR"):
                    tag = from_client[7:-1]
                    canvas.delete(tag)
                    print("Received CLEAR/UNDO message from:", addr[0])
                elif(from_client[0:5] == "ERASE"):
                    data = from_client[7:-1]
                    data = data.split(", ")
                    oldx = int(data[0])
                    oldy = int(data[1])
                    newx = int(data[2])
                    newy = int(data[3])
                    color=data[4]
                    stroke = data[5]
                    numSteps = int(data[6])
                    xStep = float(data[7])
                    yStep = float(data[8])
                    px = oldx
                    py = oldy
                    for i in range(numSteps):
                        canvas.create_oval((int(px), int(py), int(px+xStep), int(py+yStep)), 
                                    outline='black',
                                    width=20,
                                    tags=(color, color + str(stroke)))
                        px += xStep
                        py += yStep
                elif(from_client == "LOG"):
                    print("Received PLOT/ERASE message from:", addr[0])
            except:
                pass

        conn.close()


def heartBeatSend():
    global serverName
    serverUp = True
    while True:
        message = "HEARTBEAT "+my_ip
        time.sleep(1)
        broadcast(message, 9297)

        message = "HEARTBEAT"
        if serverUp:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # connection to hostname on the port.
            try:
                client.connect((SERVER_IP, 9292))
                client.send(message.encode())
                client.close()
            except:
                serverName.configure(text='Server IP: '+SERVER_IP+' (Server is down!)')
                serverName.configure(fg='red')
                serverUp = False
                print("Server down")


def recvHeartBeat():
    global all_ip
    global my_ip
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.bind((my_ip, 9297))
    serv.listen(10)

    while True:
        conn, addr = serv.accept()
        from_client = ""

        while True:
            data = conn.recv(4096)
            if not data:
                break
            from_client += data.decode()

            if(from_client[0:9] == "BROADCAST"):
                relayMessage(from_client)
                from_client = from_client.split("=")[2]

            if from_client.split()[0] == "HEARTBEAT":
                print(all_ip)
                print(ip_times)
                ip_index = all_ip.index(from_client.split()[1])
                ip_times[ip_index] = 0 #
                userLabels[ip_index][0].configure(image=photoGreenDot) #
                #print("debug1: ", all_ip, ip_times)



        conn.close()


def pruneIPList():
    global userLabels
    while 1:
        time.sleep(1)
        #print("in prune:", all_ip, ip_times)
        ip_to_pop = []
        for i in range(len(ip_times)):
            if(all_ip[i] != "X" and all_ip[i] != my_ip):
                ip_times[i] += 1
                if ip_times[i] > 10:
                    ip_to_pop.append(i)

            if(ip_times[i] >= 5):
                userLabels[i][0].configure(image=photoOrangeDot) #

        for i in range(len(ip_to_pop))[::-1]:
            #print(all_ip[ip_to_pop[i]], "disconnected")
            removeIp(ip_to_pop[i])
            userLabels[ip_to_pop[i]][0].destroy() #
            userLabels[ip_to_pop[i]][1].destroy() #
            for j in range(ip_to_pop[i] + 1, len(users)): #
                users[j-1] = users[j] #
                userLabels[j-1] = userLabels[j] #
                userLabels[j-1][0].place(x=0, y=5+(36*(j-1))) #
                userLabels[j-1][1].place(x=25, y=36*(j-1)) #
            users.pop() #
            userLabels.pop() #
            #print("Remove peer from all IPs:", all_ip)
            
            
#def sendMessage():
#    while True:
#        message = input()
#
#        for ip in all_ip:
#            sendToIp(ip, 9298, message)


try:
    _thread.start_new_thread(waitForNewIP, ())
    _thread.start_new_thread(waitForMessage, ())
    _thread.start_new_thread(heartBeatSend, ())
    _thread.start_new_thread(recvHeartBeat, ())
    _thread.start_new_thread(pruneIPList, ())
#    _thread.start_new_thread(sendMessage, ())
except:
    print("Error: unable to start client threads")
    

app.mainloop()
