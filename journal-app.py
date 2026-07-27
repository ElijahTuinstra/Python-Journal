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

push_top_frame = tk.Frame(root, bg="black")
push_top_frame.pack(side="top", fill="x") #pushes to the top

frm = tk.Frame(push_top_frame, bg="black", padx=20, pady=20)
frm.pack(side="left") #pushes left



"""
NOTE To whom it may concern: 
To make widgets display to the farthest left, top, and not on top of each other I use
push_top_frame: frame pushed to top side
frm: frame pushed to the left side
pack: I pack all the widgets into frm, which makes them go to the next line instead of covering each other
"""

signInProcess = 0

def clearScreenAll(): #destroys all widgets. NOTE TO SELF: Use "if widget != 'widgetname'" to save a widget from being destroyed
    for widget in frm.winfo_children():
            widget.pack_forget()
            widget.grid_forget()
            widget.place_forget()

def unbindAll(widget): #unbinds all custom keybinds
    for sequence in widget.bind():
        widget.unbind(sequence)

def grabInput(event, entry_widget):
      user_text = entry_widget.get()
      print(user_text) #NOTE TO SELF: remove later when done checking if terminal receives it
      return user_text

def nextSignInStep(event=None):
    global signInProcess
    clearScreenAll()
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
        ytcon_label = tk.Label(frm, text="Y/y to continue") #ycon stands for y-to-continue
        ytcon_label.pack(anchor="w") #packs in the y to continue message
        ytcon_entry = tk.Entry(frm) #entry box for user to type into
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
                    entry_error_label = tk.Label(frm, text="please input a valid answer")
                    entry_error_label.pack(anchor="w")
                    sent_error_message = True

        root.bind("<Return>", process_input)
    
    initial_message_label = tk.Label(frm, text="Welcome to Python-Journal, a project made by ET for a ysws known as #portputer")
    initial_message_label.pack(anchor="w")
    ytcon()

def preexistingUsernameCheck():
    existing_username_check = tk.Label(frm, text="Do you already have an username with us?")
    existing_username_check.pack(anchor="w")

nextSignInStep() #kickstarts rest of code

root.mainloop()