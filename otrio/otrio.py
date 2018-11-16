from tkinter import *
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

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
client_socket = None
my_msg = ''
BUFSIZ = 1024
msg_list = []
messages_frame = entry_field = ADDR = None
host_field = port_field = None
PORTvar = HOSTvar = StringVar()
PORT = 0
HOST = ""

def receive():
    """Handles receiving of messages."""
    global client_socket, msg_list
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            msg_list.insert(END, msg)
        except:  # Possibly client has left the chat.
            break

def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    global my_msg, client_socket, messages_frame
    msg = my_msg.get()
    my_msg.set("")  # Clears input field.
    client_socket.send(bytes(msg, "utf8"))
    if msg == "{quit}":
        print("quitted")
        client_socket.close()
        messages_frame.destroy()

def on_closing(event=None):
    global my_msg, messages_frame
    """This function is to be called when the window is closed."""
    try:
        my_msg.set("{quit}")
        send()
    except:
        print("already closed")

def win_on_closing(event=None):
    global my_msg, messages_frame
    """This function is to be called when the window is closed."""
    try:
        my_msg.set("{quit}")
        send()
    except:
        print("already closed")
    finally:
        window.destroy()


#chat/network stuff

def entry_callback(event):
    entry_field.selection_range(0, END)

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
    global client_socket, my_msg, msg_list, messages_frame, entry_field, port_field, host_field
    if (messages_frame is None or not messages_frame.winfo_exists()):
        messages_frame = Toplevel(window)
        messages_frame.title("Chat")
        messages_frame.iconbitmap(icon)
        #Enter the login details (host/port)
        host_field = Entry(messages_frame)
        host_field.bind("<Return>", get_host)
        host_field.pack()
        port_field = Entry(messages_frame)
        port_field.bind("<Return>", get_host)
        port_field.pack()

def execute_the_rest():
    global client_socket, my_msg, msg_list, messages_frame, entry_field, HOST, PORT
    #host/port input should disappear, and be replaced with this 
   
    my_msg = StringVar()  # For the messages to be sent.
    my_msg.set("Type your messages here.")
    scrollbar = Scrollbar(messages_frame)  # To navigate through past messages.
    # Following will contain the messages.
    msg_list = Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
    scrollbar.pack(side=RIGHT, fill=Y)
    msg_list.pack(side=LEFT, fill=BOTH)
    msg_list.pack()

    entry_field = Entry(messages_frame, textvariable=my_msg)
    entry_field.bind("<FocusIn>", entry_callback)
    entry_field.bind("<Return>", send)
    entry_field.pack()
    send_button = Button(messages_frame, text="Send", command= send)
    send_button.pack()

    messages_frame.protocol("WM_DELETE_WINDOW", on_closing)
    window.protocol("WM_DELETE_WINDOW", win_on_closing)

    #----Now comes the sockets part----

    ADDR = (HOST, PORT)
    
    
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect(ADDR)

    receive_thread = Thread(target=receive)
    receive_thread.start()
    
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
