"""
NOTE(s) TO OTHERS:
    1.I try to use camel case for global variables and functions (e.g. globalVariableName), and underscores for local variables 
        and functions (e.g. local_variable_name).
    2.
TODO:
1. remove print part from introduction/change it to just say "introduction sucessfully completed" when sucessfully completed
"""
# region App Config
import atexit #used to safely close app suddenly
import sqlite3 #used to store usernames and journal entries
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
first_username_attempt = None
sentErrorMessage = None

# endregion

# region Database Stuff NOTE: SQLite is super confusing, so I've left some extra comments to help you - and future me - out
def initializeJournalDatabase():
    """
    NOTE 1: I'll be using a fed ex (the shipping company) warehouse as an analogy, as it helps in remembering this database stuff
    NOTE 2, TO OTHER PEOPLE READING THIS: Yes ik that my analogy is corny, but it works for me
    """
    conn = sqlite3.connect("journal.db") #open door to fed ex warehouse and enter

    cursor = conn.cursor() #cursor is the worker in fed ex. Imma just name her Carla for easy reference in the future

    """
    ask Carla to to go look for a book case (table) named users, and if one doesn't exist, to create one. 
    In this case the shelf (column) is only one box wide, and will gain rows as new entries are made
    """
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL
        )
    """)
    conn.commit() #saves modifications made to the database NOTE: kinda funny to me that they use commit just like github does, or maybe that's common lingo and I'm just too green to know
    conn.close() #exit fedex and close door (without saying goodbye to carla, no less)

    conn_journal = sqlite3.connect("journal.db")
    cursor_journal = conn_journal.cursor()

    cursor_journal.execute("""
    CREATE TABLE IF NOT EXISTS journals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        journal_name TEXT NOT NULL,
        enciphered_text TEXT NOT NULL,
        FOREIGN KEY (username) REFERENCES users (username)
    )
    """)

    conn_journal.commit()
    conn_journal.close()

def usernameExistenceCheck(username):
    conn = sqlite3.connect("journal.db") #enter warehouse

    cursor = conn.cursor() #rebirth Carla

    """
    #carla will look for row with username on it, and will return "1" if it exists. 
    # NOTE: 1 can be replaced with any number, or with any word if word is in single quotes ex: 'word'
    """
    cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))

    row = cursor.fetchone() #if username found, set row to 1 as placeholder

    conn.close() #exit fedex

    # if row with username exists, will return a value of "True". if there isn't a row with the username, will return a value of "false" (i.e. username is new).
    return row is not None

def createNewUsername(new_username):
    conn = sqlite3.connect("journal.db") #enter warehouse
    cursor = conn.cursor() #rebirth carla

    query = "INSERT INTO users (username) VALUES (?)" #creates empty row in column 'username' in table 'users'

    cursor.execute(query, (new_username,)) #fills in empty row with the new username
    conn.commit() #save changes
    conn.close() #close connection

def makeDatabaseEntry(database_name, table_name, table_column, entry):
    conn = sqlite3.connect(f"{database_name}.db")
    cursor = conn.cursor()
    
    query = f"INSERT INTO {table_name} ({table_column}) VALUES (?)"
    
    cursor.execute(query, (entry,))
    conn.commit()
    conn.close()

def saveJournalEntry(username, journal_entry_name, enciphered_entry):
    conn = sqlite3.connect("journal.db")
    cursor = conn.cursor()

    query = "INSERT INTO journals (username, journal_name, enciphered_text) VALUES (?, ?, ?)"

    cursor.execute(query, (username, journal_entry_name, enciphered_entry))
    conn.commit()
    conn.close()

def clearEntireDatabase(database_name): #used to clear everything inside of a given database's tables
    print(f"Destroying all data inside of '{database_name}.db'")

    try:
        conn = sqlite3.connect(f"{database_name}.db") #connect to database
        cursor = conn.cursor() #rebirth carla

        """
        Buckle up boys and girls (and future me probably) because the information I'm about to unload onto you is a tough pill to swallow:
            Knowledge you need/preface:
                1.SQLite creates it's own special table called 'sqlite_master' inside every .db file you make using it. 
                    Inside of 'sqlite_master' SQLite stores info about every Database Object you create (database objects include 
                    tables, indexes, views, and structural triggers)
                2.To grab a specific type of database object from 'sqlite_master', you use WHERE type='x'. e.g. WHERE type='table'
                3.SQLite creates its own private tables that it uses to track various things, and should not be deleted. their tables
                    ALWAYS start with the prefix: sqlite_
            
            Basically the line asks Carla to: 
            a.return the names(SELECT name)
            b.that listed in sqlite_master (FROM sqlite_master)
            c.that are tables (WHERE type='table')
            d.that are not made my sqlite automatically (AND name NOT LIKE 'sqlite_%')
        Good lord that took me like half an hour to write, but now at least I (and hopefully you) understand SQLite a little better
        """
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")

        tables = cursor.fetchall() #takes names found during the search for tables, and puts them into a python list

        for table in tables: #for each table
            table_name = table[0] #get table name
            cursor.execute(f"DELETE FROM {table_name}")
            print(f"Sucessfully cleared '{table_name}'")

        conn.commit() #save changes
        conn.close() #close database
    except Exception as e:
        print(f"Failed to clear '{e}'")
    print("cleared")

def clearDatabaseTable(database_name, table_name):
    print(f"'{table_name}' table in '{database_name}' is being cleared...")
    conn = sqlite3.connect(f"{database_name}.db") #enter fed ex
    cursor = conn.cursor() #rebirth carla

    cursor.execute(f"DELETE FROM {table_name}") #destroys the users shelf's entire contents

    conn.commit() #save changes
    conn.close() #leave

    print(f"{table_name} table in '{database_name}' has been cleared")

def closeDatabases():
    sql_databases = ["journal"]
    i = 0
    while i < len(sql_databases):
        db_name = f"{sql_databases[i]}.db"
        try:
            conn = sqlite3.connect(db_name)
            conn.execute("SELECT 1")
            conn.close()
            print(f"{db_name} closed")
        except Exception:
            print(f"uh oh, lwk couldn't process {db_name}.db")
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
    initializeJournalDatabase()
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

        list_of_keybind_label = tk.Label(tl_frm, text="List of Keybinds:")
        list_of_keybind_label.pack(anchor="w")
        keybinds = ["control-f: Fullscreen", "enter: submit entry"]
        for item in keybinds:
            keybind_list_item_label = tk.Label(tl_frm, text=item)
            keybind_list_item_label.pack(anchor="w")


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
        global first_username_attempt
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
            root.after(1500, lambda: nextSignInStep(2))
        else:
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
                createNewUsername(entered_username)
                username_created_label = tk.Label(tl_frm, text=f"Created username entry for '{entered_username}'.")
                username_created_label.pack(anchor="w")
                root.unbind("<Return>")
                root.after(1500, lambda: nextSignInStep())
            except Exception as e:
                print(f"Database insertion failed: {e}")
                database_error_label = tk.Label(tl_frm, text=f"Something went wrong when trying to create a username entry for '{entered_username}'. Try again.")
                database_error_label.pack(anchor="w")
            
        else:
            confirm_username_entry.delete(0, "end")
            if not sentErrorMessage: #if sent_error_message is false (used to avoid sending multiple errors messages
                entry_error_label = tk.Label(tl_frm, text="Usernames do not match. Please try again.")
                entry_error_label.pack(anchor="w")
                sentErrorMessage = True




    root.bind("<Return>", process_username_confirmation)

def createOrReadEntry():
    enquiry_cOR_label = tk.Label(tl_frm, text="Press 1 for new journal entry. Press 2 to read previous entries")
    enquiry_cOR_label.pack(anchor="w")

    confirm_username_entry = tk.Entry(tl_frm)
    confirm_username_entry.pack(anchor="w")
    confirm_username_entry.focus()

def newJournalEntry():
    print("end project so far")
    end_label = tk.Label(tl_frm, text=f"end project")
    end_label.pack(anchor="w")

def viewJournalEntries():
    print("end project so far")
    end_label = tk.Label(tl_frm, text=f"end project")
    end_label.pack(anchor="w")

def nextSignInPath():
    global signInProcess 
    if signInProcess == 1:
        introduction()
    elif signInProcess == 2:
        preexistingUsernameCheck()
    elif signInProcess == 3:
        confirmNewUsername()
    elif signInProcess == 4:
        createOrReadEntry()


# endregion

quit_button = tk.Button(br_frm, text="Quit", name="doNotDelete", command=root.destroy)
quit_button.pack(side="right")
clearUsernameDatabase_button = tk.Button(br_frm, text="Clear Journal Database", name="doNotDelete2", command=lambda: clearEntireDatabase("journal"))
clearUsernameDatabase_button.pack(side="right")

setupProgram()
nextSignInStep() #kickstarts rest of code

root.mainloop()