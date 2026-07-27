import sqlite3 #used to store usernames and journal entries
import hashlib #used to store passwords
import tkinter as tk

root = tk.Tk() #base window
root.state("zoomed")
root.title("Python-Journal")

root.config(bg="black")

root.option_add("*Foreground", "#C9D1D9") #makes light grey text deafult, it's the same color used by github and I like it
root.option_add("*Entry.insertBackground", "#C9D1D9") #sets color of the blinky line thingy in text boxes
root.option_add("*Button.activeForeground", "#C9D1D9") #sets color of the text on buttons

root.option_add("*Background", "black") #black background
root.option_add("*Button.activeBackground", "black") #black button background

#Allows frm to be top left of root
push_top_frm = tk.Frame(root, bg="black")
push_top_frm.pack(side="top", fill="x") #pushes to the top
tl_frm = tk.Frame(push_top_frm, bg="black", padx=20, pady=20)
tl_frm.pack(side="left") #pushes left

#allows bottom_frm to be bottom left of root
push_bottom_frm = tk.Frame(root, bg="black")
push_bottom_frm.pack(side="bottom", fill="x") #pushes to the bottom
br_frm = tk.Frame(push_bottom_frm, bg="black", padx=20, pady=20)
br_frm.pack(side="right") #pushes right

quit_button = tk.Button(br_frm, text="Quit", name="doNotDelete", command=root.destroy)
quit_button.pack(anchor="e")

"""
NOTE To whom it may concern: 
To make widgets display to the farthest left, top, and not on top of each other I use
push_top_frame: frame pushed to top side
frm: frame pushed to the left side
pack: I pack all the widgets into frm, which makes them go to the next line instead of covering each other
"""

signInProcess = None

def fullscreenToggle(event=None):
    currently_fullscreen = root.attributes("-fullscreen") #returns true if fullscreen, false if not fullscreen
    root.attributes("-fullscreen", not currently_fullscreen) #switches fullscreen mode on if it's off, and off if it's on

def clearAllWidgets(area): #destroys all widgets in the entered area
    for widget in area.winfo_children():
            if "doNotDelete" in str(widget): #used to preserve widgets I don't want deleted
                continue #skips over the forget part

            widget.pack_forget()
            widget.grid_forget()
            widget.place_forget()

def unbindAll(area): #unbinds all custom keybinds in given area, ex: root
    for sequence in area.bind():
        if "Control" in sequence: #if F11 is in the sequence
            continue #skips over the unbind part
        area.unbind(sequence)


def grabInput(event, entry_widget):
      user_text = entry_widget.get()
      print(user_text) #NOTE TO SELF: remove later when done checking if terminal receives it
      return user_text

def setupProgram():
    global signInProcess

    clearAllWidgets(tl_frm)
    unbindAll(root)
    signInProcess = 0
    root.bind("<Control-f>", fullscreenToggle)

def nextSignInStep(event=None):
    global signInProcess
    clearAllWidgets(tl_frm)
    unbindAll(root)
    signInProcess += 1
    nextSignInPath()

def nextSignInPath():
    global signInProcess 
    if signInProcess == 1:
        introduction()
    elif signInProcess == 2:
        preexistingUsernameCheck()
    
def introduction():
    def ytcon(): #this was a super confusing part to write, sorry in advance if there's excessive comments
        ytcon_label = tk.Label(tl_frm, text="Y/y to continue") #ycon stands for y-to-continue
        ytcon_label.pack(anchor="w") #packs in the y to continue message
        ytcon_entry = tk.Entry(tl_frm) #entry box for user to type into
        ytcon_entry.pack(anchor="w")

        sent_error_message = False

        def process_input(event):
            nonlocal sent_error_message
            returned_text = grabInput(event, ytcon_entry) #takes input from the entry box

            if returned_text.lower() == "y": #if the returned text, converted into lowercase (so that entering a capitilized Y works too) is y
                nextSignInStep() #start process to run next step
            else: #if the returned text isn't y, and 
                ytcon_entry.delete(0, "end") #clear entry box
                if not sent_error_message: #if sent_error_message is false (used to avoid sending multiple errors messages
                    entry_error_label = tk.Label(tl_frm, text="please input a valid answer")
                    entry_error_label.pack(anchor="w")
                    sent_error_message = True

        root.bind("<Return>", process_input)
    
    initial_message_label = tk.Label(tl_frm, text="Welcome to Python-Journal, a project made by ET for a ysws known as #portputer")
    initial_message_label.pack(anchor="w")
    ytcon()

def preexistingUsernameCheck():
    existing_username_check = tk.Label(tl_frm, text="Do you already have an username with us?")
    existing_username_check.pack(anchor="w")

setupProgram()
nextSignInStep() #kickstarts rest of code

root.mainloop()