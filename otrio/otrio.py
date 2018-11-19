from tkinter import *
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from datetime import datetime

icon = 'resizedblob_pBr_icon.ico' #icon image

window = Tk()
window.title("Otrio")
window.resizable(False, False) #prevents resizing the window
window.iconbitmap(icon) #icon

player = 0 #current player
playercount = 2
colors = ["blue", "red", "green", "purple"] #corresponding color

#status bar
class StatusBar(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)
        self.label = Label(self, bd=1, relief=SUNKEN, anchor=W)
        self.label.pack(fill=X)

    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()

def callback():
    print("shoutouts to sean ranklin!")

def pulverize(newtop : Toplevel, number: int):
    global playercount, player
    newtop.destroy()
    start()
    playercount = (int)(number)
    player = 0
    print("PLAYERS:", playercount)
    newtop.grab_release()
    
def command_new():
    #--new-- menu option
    newtop = Toplevel()
    '''newtop.wm_geometry("200x100")'''
    newtop.title("New...")
    newtop.iconbitmap(icon)
    newtop.grab_set()
    
    msg = Message(newtop, text="Choose number of players")
    msg.pack()

    tkvar = StringVar(window)
    choices = {'2','3','4'}
    tkvar.set('2')
    choose_players = OptionMenu(newtop, tkvar, *choices)
    choose_players.pack()

    button = Button(newtop, text="Start", command= lambda: pulverize(newtop, tkvar.get()))
    button.pack()

def command_exit(window: Tk):
    window.destroy()

ruletop = None
def rule_window():
    global ruletop
    if (ruletop is None or not ruletop.winfo_exists()): #check if window exists already
        ruletop = Toplevel()
        ruletop.title("Game Rules")
        ruletop.iconbitmap(icon)
        msg = Message(ruletop, text="Win Conditions:\n1.Get all 3 piece sizes in one cell\n2.Get 3 in a row with pieces of the same size\n3.Get 3 in a row with pieces of ascending size(small, medium, large)")
        msg.pack()

        button = Button(ruletop, text="Close", command= ruletop.destroy)
        button.pack()
        
    
#increment player
def inc_player():
    global player, playercount
    if player == playercount-1:
        player = 0
    else:
        player+=1
    status.set("%d (%s)'s turn", player+1, (colors[player]))

#status bar
status = StatusBar(window)
status.pack(side=BOTTOM, fill=X)
status.set("%s", "big ups liquid richard")

###NETWORK SECTION (most taken from online lol)
client_socket = text = b1 = b2 = b3 = b4 = b5 = None
my_msg = ''
BUFSIZ = 1024
msg_list = []
messages_frame = entry_field = ADDR = None
host_field = port_field = None
PORTvar = HOSTvar = StringVar()
PORT = 0
HOST = ""
c1 = None




#chat/network stuff

def entry_callback(event):
    global entry
    entry.selection_range(0, END)

def get_host(event):
    global HOST, host_field
    HOST = host_field.get()
    host_field.destroy()
    get_port()

def get_port(event=None):
    global ADDR, HOST, PORT, port_field
    PORT = port_field.get()
    if not PORT:
        PORT = 33000
    else:
        PORT = int(PORT)     
    port_field.destroy()
    execute_the_rest()

def chat_window():
    global client_socket, my_msg, msg_list, messages_frame, entry_field, port_field, host_field, text
    if (messages_frame is None or not messages_frame.winfo_exists()):
        messages_frame = Toplevel(window)
        messages_frame.title("Chat")
        messages_frame.iconbitmap(icon)

        text = Text(master=messages_frame)
        text.pack(expand=True, fill="both")
        #Enter the login details (host/port)
        host_field = Entry(messages_frame)
        host_field.bind("<Return>", get_host)
        host_field.pack()
        port_field = Entry(messages_frame)
        port_field.bind("<Return>", get_host)
        port_field.pack()

def buttons(frame):
    for i in "Connect", "Create A Nickname", "Send", "Clear", "Exit":
        b = Button(master=frame, text=i)
        b.pack(side="left")
        yield b

class Client:
    def __init__(self):
        self.s = socket(AF_INET, SOCK_STREAM)
        self.nickname = None

    def connect(self):
        global HOST, PORT, text
        now = str(datetime.now())[:-7]
        if self.nickname is not None:
            try:
                self.s.connect((HOST, PORT))
                text.insert("insert", "({}) : Connected.\n".format(now))
                self.s.sendall(bytes("{}".format(self.nickname).encode("utf-8")))
                self.receive()
            except ConnectionRefusedError:
                text.insert("insert", "({}) : The server is not online.\n".format(now))
        else:
            text.insert("insert", "({}) : You must create a nickname.\n".format(now))

    def receive(self):
        while True:
            data = str(self.s.recv(1024))[2:-1]
            now = str(datetime.now())[:-7]
            if len(data) == 0:
                pass
            else:
                text.insert("insert", "({}) : {}\n".format(now, data))

    def do_nothing(self):
        pass

    def create_nickname(self):
        global messages_frame, b2, text, c1
        b2.configure(command=self.do_nothing)
        _frame = Frame(master=messages_frame)
        _frame.pack()
        new_entry = Entry(master=_frame)
        new_entry.grid(row=0, column=0)
        new_button = Button(master=_frame, text="Accept Your Nickname")
        new_button.grid(row=1, column=0)

        def nickname_command():
            now = str(datetime.now())[:-7]
            if new_entry.get() == "":
                text.insert("insert", "({}) : You must write a nickname.\n".format(now))
            else:
                self.nickname = new_entry.get()
                _frame.destroy()
                text.insert("insert", "({}) : Nickname has changed to: '{}'\n".format(now, self.nickname))
                b2.configure(command=c1.create_nickname)

        new_button.configure(command=nickname_command)

    def send(self):
        global entry
        respond = "{}: {}".format(self.nickname, str(entry.get()))
        now = str(datetime.now())[:-7]
        entry.delete("0", "end")
        try:
            self.s.sendall(bytes(respond.encode("utf-8")))
            '''text.insert("insert", "({}) : {}\n".format(now, respond))'''
        except BrokenPipeError:
            text.insert("insert", "({}) : Server has been disconnected.\n".format(now))
            self.s.close()


def connect():
    global c1
    t1 = Thread(target=c1.connect)
    t1.start()


def send(event=None):
    global c1
    t2 = Thread(target=c1.send)
    t2.start()


def clear():
    text.delete("1.0", "end")


def destroy():
    global messages_frame, text, c1
    respond = "{}".format(c1.nickname + " has disconnected.")
    now = str(datetime.now())[:-7]
    entry.delete("0", "end")
    try:
        c1.s.sendall(bytes(respond.encode("utf-8")))
        text.insert("insert", "({}) : {}\n".format(now, respond))
    except BrokenPipeError:
        text.insert("insert", "({}) : Server has been disconnected.\n".format(now))
        c1.s.close()
    messages_frame.destroy()


def execute_the_rest():
    global client_socket, my_msg, msg_list, messages_frame, entry_field, HOST, PORT, b1, b2, b3, b4, b5, c1, entry
    #host/port input should disappear, and be replaced with this 

    

    entry = Entry(master=messages_frame)
    entry.bind("<FocusIn>", entry_callback)
    entry.bind("<Return>", send)
    entry.pack(expand=True, fill="x")

    b1, b2, b3, b4, b5 = buttons(messages_frame)
    c1 = Client()
    
    b1.configure(command=connect)
    b2.configure(command=c1.create_nickname)
    b3.configure(command=send)
    b4.configure(command=clear)
    b5.configure(command=destroy)
    t0 = Thread()
    t0.run()
        
#menu
menu = Menu(window)
back = Canvas(window, width=640, height=480)

filemenu = Menu(menu, tearoff=False)
menu.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="New", command=command_new)
filemenu.add_command(label="Nut", command=chat_window)
filemenu.add_separator()
filemenu.add_command(label="Exit", command= lambda: command_exit(window))

helpmenu = Menu(menu, tearoff=False)
menu.add_cascade(label="Help", menu=helpmenu)
helpmenu.add_command(label="Rules", command=rule_window)

window.config(menu=menu)

back.pack(fill="none", expand=True, side="bottom")

#the circle creator
def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
Canvas.create_circle = _create_circle

#button frame
class Square(Button):
    def __init__(self, r, c , **k):
        Button.__init__(self, **k)
        self.r = r
        self.c = c
        self.x = self.winfo_rootx()
        self.y = self.winfo_rooty()

    def showGrid(self):
        status.set("%d, %d",r,c)

    def showCoords(self):
        status.set("%d, %d", self.winfo_rootx(), self.winfo_rooty())
        self.x = self.winfo_rootx()
        self.y = self.winfo_rooty()

    def getCoords(self):

        return (self.winfo_rootx(), self.winfo_rooty())

window.update()



#mouse click events
def test(event):
    print("test")

def stop_everything(event):
    back.delete("all")
    command_new()

def onclick(event):
    item = back.find_closest(event.x, event.y) # for some reason item is a tuple lol
    tags = back.gettags(item)
    if tags[0] != "filled" and tags[0] != "rect":
        x,y = tags[1],tags[2]
        which = tags[0]
        back.itemconfig(item, fill=colors[player])
        back.itemconfig(item, tags=("filled", which, x, y))
        if logic() ==1:
            status.set("GAME OVER: player %d (%s) wins", player+1, colors[player])
            back.bind('<Button-1>', stop_everything)
            return
        elif logic() == 2:
            status.set("GAME OVER: no one wins")
            back.bind('<Button-1>', stop_everything)
            return
        inc_player()
 
#logic

def no_moves():
    items = back.find_all()
    for i in items:
        if back.gettags(i)[0] != "filled":
            return 0
    return 1
    
def logic():
    if no_moves() == 1:
        return 2
    filled = back.find_withtag("filled")
    '''print(filled)'''
    #On^3 to search for matches
    for item in filled:
        which = back.gettags(item)[1]
        x,y  = (int)(back.gettags(item)[2]), (int)(back.gettags(item)[3])
        player_color = back.itemcget(item, "fill")
        '''print("ITEM:", item, back.gettags(item), player_color)'''
        for i in filled:
            if i != item and player_color == back.itemcget(i, "fill"):
                tags = back.gettags(i)
                r, c = (int)(tags[2]), (int)(tags[3])
                #all 3 in 1 cell check
                if c == y and r == x:
                    for var in filled:
                        subtags = back.gettags(var)
                        if var != item and var != i:
                            if which != subtags[1] and subtags[1] != tags[1] and (int)(subtags[2]) == x and (int)(subtags[3]) == y and back.itemcget(var, "fill") == player_color:
                                print("all3 MATCH")
                                return 1
                #vertical check
                if y == 1 and c == 0 and x == r: 
                    if which == tags[1]: #same size type
                        for var in filled:
                            subtags = back.gettags(var)
                            if var != item and var != i:
                                if which == subtags[1] and tags[1] == subtags[1] and (int)(subtags[3]) == 2 and (int)(subtags[2]) == x and back.itemcget(var, "fill") == player_color:
                                    print("vert MATCH")
                                    return 1
                    elif which == "mid" and tags[1] != "mid": #checking ascending types, assuming item is the middle one
                        for var in filled:
                            subtags = back.gettags(var)
                            if var != item and var != i:
                                if which != subtags[1] and subtags[1] != tags[1] and (int)(subtags[3]) == 2 and (int)(subtags[2]) == x and back.itemcget(var, "fill") == player_color:
                                    print("vert MATCH")
                                    return 1
                #horizontal check
                if x == 1 and r == 0 and y == c:
                    if which == tags[1]: #same size type
                        for var in filled:
                            subtags = back.gettags(var)
                            if var != item and var != i:
                                if which == subtags[1] and tags[1] == subtags[1] and (int)(subtags[2]) == 2 and (int)(subtags[3]) == y and back.itemcget(var, "fill") == player_color:
                                    print("horiz MATCH")
                                    return 1
                    elif which == "mid" and tags[1] != "mid": #checking ascending types, assuming item is the middle one
                        for var in filled:
                            subtags = back.gettags(var)
                            if var != item and var != i:
                                if which != subtags[1] and subtags[1] != tags[1] and (int)(subtags[2]) == 2 and (int)(subtags[3]) == y and back.itemcget(var, "fill") == player_color:
                                    print("horiz MATCH")
                                    return 1
                #diagonal check, down right
                if x==1 and y==1 and r==0 and c==0: 
                    if which == tags[1]: #same size type
                        for var in filled:
                            subtags = back.gettags(var)
                            if var != item and var != i:
                                if which == subtags[1] and tags[1] == subtags[1] and (int)(subtags[3]) == 2 and (int)(subtags[2]) == 2 and back.itemcget(var, "fill") == player_color:
                                    print("diag MATCH")
                                    return 1
                    elif which == "mid" and tags[1] != "mid": #checking ascending types, assuming item is the middle one
                        for var in filled:
                            subtags = back.gettags(var)
                            if var != item and var != i:
                                if which != subtags[1] and subtags[1] != tags[1] and (int)(subtags[2]) == 2 and (int)(subtags[3]) == 2 and (int)(subtags[2]) == r+2 and back.itemcget(var, "fill") == player_color:
                                    print("diag MATCH")
                                    return 1
                #diagonal check, down left
                if x == 1 and y == 1 and r==0 and c == 2:
                    if which == tags[1]: #same size type
                        for var in filled:
                            subtags = back.gettags(var)
                            if var != item and var != i:
                                if which == subtags[1] and tags[1] == subtags[1] and (int)(subtags[3]) == 0 and (int)(subtags[2]) == 2 and back.itemcget(var, "fill") == player_color:
                                    print("diag MATCH")
                                    return 1
                    elif which == "mid" and tags[1] != "mid": #checking ascending types, assuming item is the middle one
                        for var in filled:
                            subtags = back.gettags(var)
                            if var != item and var != i:
                                if which != subtags[1] and subtags[1] != tags[1] and (int)(subtags[3]) == 0 and (int)(subtags[2]) == 2 and back.itemcget(var, "fill") == player_color:
                                    print("diag MATCH")
                                    return 1
    return 0
                        
#drawing grid

def start():
    global player
    back.delete("all")
    player = 0
    status.set("%d (%s)'s turn", player+1, (colors[player]))
    back.pack()
    shapes = []
    width = back.winfo_width()/3
    height = back.winfo_height()/3
    for r in range(3):
        for c in range(3):
            a = back.create_rectangle(r*width, c*height, (r+1)*width, (c+1)*height, tags=("rect",r,c), fill="white")
            shapes.append(a)        
            b = back.create_oval(r*width+3, c*height+3, (r+1)*width-3, (c+1)*height-3, tags=("outer",r,c), fill="white")
            shapes.append(b)
            d = back.create_oval(r*width+35, c*height+35, (r+1)*width-35, (c+1)*height-35, tags=("mid",r,c), fill="white")
            shapes.append(d)
            e = back.create_oval(r*width+75, c*height+65, (r+1)*width-75, (c+1)*height-65, tags=("inner",r,c), fill="white")
            shapes.append(e)


    back.bind('<Button-1>', onclick)

#window display
window.mainloop()
