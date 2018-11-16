from tkinter import *
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

#menu
menu = Menu(window)


filemenu = Menu(menu, tearoff=False)
menu.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="New", command=command_new)
filemenu.add_command(label="Open", command=callback)
filemenu.add_separator()
filemenu.add_command(label="Exit", command= lambda: command_exit(window))

helpmenu = Menu(menu, tearoff=False)
menu.add_cascade(label="Help", menu=helpmenu)
helpmenu.add_command(label="About...", command=callback)

window.config(menu=menu)

back = Canvas(window, width=640, height=480)
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

status.set("%d (%s)'s turn", player+1, (colors[player]))

#mouse click events
def find_closest(x,y):
    width = back.winfo_width()/3
    height = back.winfo_height()/3

def test(event):
    print("test")

def stop_everything(event):
    back.delete("all")

def onclick(event):
    item = back.find_closest(event.x, event.y) # for some reason item is a tuple lol
    tags = back.gettags(item)
    if tags[0] != "filled" and tags[0] != "rect":
        x,y = tags[1],tags[2]
        which = tags[0]
        back.itemconfig(item, fill=colors[player])
        back.itemconfig(item, tags=("filled", which, x, y))
        if logic() ==1:
            status.set("game over, player %d (%s) wins -- click to continue", player, colors[player])
            back.bind('<Button-1>', stop_everything)
            return
        elif logic() == 2:
            status.set("game over, no one wins -- click to continue")
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
                        
    print("---------------")
    
#drawing grid

def start():
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

