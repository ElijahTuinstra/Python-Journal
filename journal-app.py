"""
TODO:
1. Add in logout button that will sit with quit button
2. Add in password part of program
3. Add in journal entry part of program. Will save date with journal entry. to pull out journal entry, it will show user
    a numbered list of entries, found by searching for journal entries in the journal database under the same username as user
    then will order them into a list (will show like the past 20 most recent ones). user will then enter a number or a name of a
    journal entry, which will then show user the entry

"""
# region App Config
import atexit #used to safely close app suddenly
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


#allows bottom_frm to be bottom left of root
push_bottom_frm = tk.Frame(root, bg="black")
push_bottom_frm.pack(side="bottom", fill="x") #pushes to the bottom

br_frm = tk.Frame(push_bottom_frm, bg="black", padx=20, pady=20)
br_frm.pack(side="right") #pushes right

#Allows frm to be top left of root
push_top_frm = tk.Frame(root, bg="black")
push_top_frm.pack(side="top", fill="both", expand=True) #pushes to the top

tl_frm = tk.Frame(push_top_frm, bg="black", padx=20, pady=20)
tl_frm.pack(side="left", anchor= "nw") #pushes left

"""
NOTE To whom it may concern: 
To make widgets display to the farthest left, top, and not on top of each other I use
push_top_frame: frame pushed to top side
frm: frame pushed to the left side
pack: I pack all the widgets into frm, which makes them go to the next line instead of covering each other
"""

signInProcess = None
active_conn = None
first_username_attempt = None
sentErrorMessage = None

# endregion

# region Database Stuff
def makeDatabaseEntry(database_name, table_name, table_column, entry):
    conn = sqlite3.connect(f"{database_name}.db")
    cursor = conn.cursor()
    
    query = f"INSERT INTO {table_name} ({table_column}) VALUES (?)"
    
    cursor.execute(query, (entry,))
    conn.commit()
    conn.close()

def initializeUsernameDatabase(): #database is fed ex warehouse
    """
    NOTE 1: I will be using fed ex as a analogy cus my brains to fried to remember this database stuff any other way.
    NOTE 2, TO OTHER PEOPLE READING THIS: Yes ik that my analogy is corny, but it's hard to remember all the little things okay
    """
    conn = sqlite3.connect("username.db") #open door to fed ex warehouse and enter

    cursor = conn.cursor() #cursor is the worker in fed ex. Imma just name her carla for easy reference in the future

    """
    ask Carla to to go look for a book case named users. Note that in this case, the shelf can be super tall (one shelf per username), 
    but since we are (currently, as I'm writing this) only storing one thing per username (i.e. their actual username) each row is only one cell long
    """
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL
        )
    """)
    conn.commit() #saves modifications made to the database NOTE: kinda funny to me that they use commit just like github does, or maybe that's common lingo and I'm just too green to know
    conn.close() #exit fedex and close door (without saying goodbye to carla, no less)
"""
def clearDatabase(database_name):
    print(f"{database_name} is being cleared...")
    conn = sqlite3.connect(f"{database_name}.db") #enter fed ex
    cursor = conn.cursor() #rebirth carla

    cursor.execute(f"DELETE FROM {database_name}") #carla destroys the database's contents

    conn.commit() #save changes
    conn.close() #leave

    print(f"{database_name} has been cleared")
""" #work on this part later
def clearDatabaseTable(database_name, table_name):
    print(f"'{table_name}' table in '{database_name}' is being cleared...")
    conn = sqlite3.connect(f"{database_name}.db") #enter fed ex
    cursor = conn.cursor() #rebirth carla

    cursor.execute(f"DELETE FROM {table_name}") #destroys the users shelf's entire contents

    conn.commit() #save changes
    conn.close() #leave

    print(f"{table_name} table in '{database_name}' has been cleared")

def usernameExistenceCheck(username):
    global active_conn
    conn = sqlite3.connect("username.db") #enter fedex

    cursor = conn.cursor() #remember carla?

    """
    #carla will look for row with username on it, and will return "1" if it exists. 
    # NOTE: 1 can be replaced with any number, or with any word if word is in single quotes ex: 'word'
    """
    cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))

    row = cursor.fetchone() #sets row equal to what you got from the cursor.execute part, if you got nothing (i.e. username does not exist), then row will be empty (None)

    conn.close() #exit fedex

    # if row with username exists, will return a value of "True". if there isn't a row with the username, will return a value of "false" (i.e. username is new).
    return row is not None

def closeDatabases():
    sql_databases = ["username"]
    i = 0
    while i < len(sql_databases):
        db_name = f"{sql_databases[i]}.db"
        try:
            conn = sqlite3.connect(db_name)
            conn.execute("SELECT 1")
            conn.close()
            print(f"{db_name} closed")
        except Exception:
            print(f"uh oh, lwk couldn't process {db_name}")
        i += 1

def clean_up():
    closeDatabases()
    print("app finished, shutting down...")

atexit.register(clean_up) #runs upon window being closed, either from user pressing the X on the window, or on the quit button

# endregion

# region Program Functions
def fullscreenToggle(event=None):
    currently_fullscreen = root.attributes("-fullscreen") #returns true if fullscreen, false if not fullscreen
    root.attributes("-fullscreen", not currently_fullscreen) #switches fullscreen mode on if it's off, and off if it's on

def clearAllWidgets(area): #destroys all widgets in the entered area
    for widget in area.winfo_children():
            widget_name = str(widget).split(".")[-1]
            if widget_name.startswith("doNotDelete"): #used to preserve widgets I don't want deleted
                continue #skips over the forget part
            widget.destroy()

def unbindAll(area): #unbinds all custom keybinds in given area, ex: root
    for sequence in area.bind():
        if "Control-Key-f" in sequence: #if F11 is in the sequence
            continue #skips over the unbind part
        area.unbind(sequence)

def clearTLF(): #stands for clear top left frame
    clearAllWidgets(tl_frm)
    unbindAll(root)

def grabInput(event, entry_widget):
      user_text = entry_widget.get()
      print(user_text) #NOTE TO SELF: remove later when done checking if terminal receives it
      return user_text

def setupProgram():
    initializeUsernameDatabase()
    global signInProcess

    clearTLF()
    signInProcess = 0
    root.bind("<Control-f>", fullscreenToggle)

def nextSignInStep(step_skip=None, event=None):
    global signInProcess, sentErrorMessage
    sentErrorMessage = False
    clearTLF()
    if step_skip == None:
        signInProcess += 1
    else:
        signInProcess += step_skip
    nextSignInPath()
    
def introduction():
    def ytcon(): #this was a super confusing part to write, sorry in advance if there's excessive comments
        ytcon_label = tk.Label(tl_frm, text="Y/y to continue.") #ycon stands for y-to-continue
        ytcon_label.pack(anchor="w") #packs in the y to continue message
        ytcon_entry = tk.Entry(tl_frm) #entry box for user to type into
        ytcon_entry.pack(anchor="w")
        ytcon_entry.focus()

        def process_ytcon_input(event):
            global sentErrorMessage
            returned_text = grabInput(event, ytcon_entry) #takes input from the entry box

            if returned_text.lower() == "y": #if the returned text, converted into lowercase (so that entering a capitilized Y works too) is y
                root.unbind("<Return>")
                nextSignInStep() #start process to run next step
            else: #if the returned text isn't y, and 
                ytcon_entry.delete(0, "end") #clear entry box
                if not sentErrorMessage: #if sent_error_message is false (used to avoid sending multiple errors messages
                    entry_error_label = tk.Label(tl_frm, text="Please input a valid answer.")
                    entry_error_label.pack(anchor="w")
                    sentErrorMessage = True

        root.bind("<Return>", process_ytcon_input)
    
    initial_message_label = tk.Label(tl_frm, text="Welcome to Python-Journal, a project made by ET for a ysws known as #portputer")
    initial_message_label.pack(anchor="w")
    ytcon()

def preexistingUsernameCheck():
    existing_username_check_label = tk.Label(tl_frm, text="Please enter owned or desired username.")
    existing_username_check_label.pack(anchor="w")

    username_entry = tk.Entry(tl_frm) #entry box for user to type into
    username_entry.pack(anchor="w")
    username_entry.focus()

    def process_username_input(event):
        entered_username = username_entry.get().strip().lower()

        if not entered_username:
            invalid_username_label = tk.Label(tl_frm, text="Field cannot be blank.")
            invalid_username_label.pack(anchor="w")
            return

        root.unbind("<Return>")

        username_exists = usernameExistenceCheck(entered_username)
        if username_exists:
            welcome_back_label = tk.Label(tl_frm, text=f"Welcome back {entered_username}.")
            welcome_back_label.pack(anchor="w")
            root.unbind("<Return>")
            print("end project")
            end_label = tk.Label(tl_frm, text=f"end project")
            end_label.pack(anchor="w")
            
            #nextSignInStep(2) #skips to password step NOTE MAY HAVE TO CHANGE NUMBER OF STEPS SKIPPED LATER
        else:
            global first_username_attempt
            first_username_attempt = entered_username
            nextSignInStep()


    root.bind("<Return>", process_username_input)

def confirmNewUsername():
    confirm_username_label = tk.Label(tl_frm, text="It doesn't seem like that username exists yet. Please re-enter the username to confirm its creation.")
    confirm_username_label.pack(anchor="w")

    confirm_username_entry = tk.Entry(tl_frm)
    confirm_username_entry.pack(anchor="w")
    confirm_username_entry.focus()

    def process_username_confirmation(event):
        entered_username = confirm_username_entry.get().strip().lower()

        if not entered_username:
            invalid_username_label = tk.Label(tl_frm, text="Field cannot be blank.")
            invalid_username_label.pack(anchor="w")
            return


        if entered_username == first_username_attempt:
            try:
                makeDatabaseEntry("username", "users", "username", entered_username)
                username_created_label = tk.Label(tl_frm, text=f"Created username entry for '{entered_username}'.")
                username_created_label.pack(anchor="w")
                root.unbind("<Return>")
                print("end project")
                end_label = tk.Label(tl_frm, text=f"end project")
                end_label.pack(anchor="w")
                #root.after(1500, nextSignInStep)
            except Exception as e:
                print(f"Database insertion failed: {e}")
                database_error_label = tk.Label(tl_frm, text=f"Something went wrong on our side when trying to create a database entry for the username '{entered_username}'. Try again.")
                database_error_label.pack(anchor="w")
            
        else:
            confirm_username_entry.delete(0, "end")
            if not sentErrorMessage: #if sent_error_message is false (used to avoid sending multiple errors messages
                entry_error_label = tk.Label(tl_frm, text="Usernames do not match. Please try again.")
                entry_error_label.pack(anchor="w")
                sentErrorMessage = True




    root.bind("<Return>", process_username_confirmation)

def nextSignInPath():
    global signInProcess 
    if signInProcess == 1:
        introduction()
    elif signInProcess == 2:
        preexistingUsernameCheck()
    elif signInProcess == 3:
        confirmNewUsername()


# endregion

quit_button = tk.Button(br_frm, text="Quit", name="doNotDelete", command=root.destroy)
quit_button.pack(side="right")
clearUsernameDatabase_button = tk.Button(br_frm, text="Clear Username Database", name="doNotDelete2", command=lambda: clearDatabaseTable("username", "users"))
clearUsernameDatabase_button.pack(side="right")

setupProgram()
nextSignInStep() #kickstarts rest of code

root.mainloop()