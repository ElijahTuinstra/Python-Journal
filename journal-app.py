# region App Config
"""
MISCELLANEOUS NOTE(s) TO OTHERS:
    1.I try to use camel case for global variables and functions (e.g. globalVariableName), and underscores for local variables 
        and functions (e.g. local_variable_name).
"""
import atexit #used to safely close app suddenly
import sqlite3 #used to store usernames and journal entries
import tkinter as tk
import string #used to define encryptable characters in the cipher part of code

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
current_user_username = None
sentErrorMessage = None
sentBlankErrorMessage = None

# endregion

# region Vigenere Cipher
"""
NOTE: This is probably the most notable piece of code in this program, and besides the SQLite database stuff, its
also probably the most confusing part of code in the program. I added a lot of extra comments to help me understand,
and hopefully they'll help you too
"""
def vigenereCipher(entered_text, cipher_key, mode):
    alphabet = string.ascii_letters + string.digits + string.punctuation + " " #defines encryptable alphabet, including all upper and lowercase letters, all numbers, and all punctuation
    alphabet_length = len(alphabet) #measures length of the previously defined 'alphabet'

    entered_text_length = len(entered_text)
    
    output_list = [] #makes empty list to store the encrypted characters

    for i in range(entered_text_length): #makes this loop repeat a number of times equal to the length of the text inputed to be processed
        current_char = entered_text[i] #grabs current character in inputed text, the next one to be encrypted/decrypted

        if current_char not in alphabet: #if the current character isn't in the defined alphabet,
            output_list.append(current_char) #just adds unencrypted stuff to the end
            continue #skip rest of code in loop to prevent further issues

        entered_text_position = alphabet.index(current_char) #set equal to what the current character's number is in alphabet string
        key_char = cipher_key[i % len(cipher_key)] #set the key_char to correct letter of cipher_key, using % to loop the key NOTE: fun fact the modulus (%) is also used in the processing language to do the same thing!
        cipher_key_position = alphabet.index(key_char) #sets ckp to however much different it is than your initial letter

        if mode in ["encrypt", "e"]: #if mode is 'encrypt' or 'e'
            new_positions = (entered_text_position + cipher_key_position) % alphabet_length #sets new positions
        elif mode in ["decrypt", "d"]: #if mode IS NOT 'encrypt' or 'e', then if mode is 'decrypt' or 'd'
            new_positions = (entered_text_position - cipher_key_position) % alphabet_length #sets new positions

        output_list.append(alphabet[new_positions])

    output_text = "".join(output_list)  
    return output_text

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
        encrypted_text TEXT NOT NULL,
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

def saveJournalEntry(username, journal_entry_name, encrypted_entry):
    conn = sqlite3.connect("journal.db")
    cursor = conn.cursor()

    query = "INSERT INTO journals (username, journal_name, encrypted_text) VALUES (?, ?, ?)"

    cursor.execute(query, (username, journal_entry_name, encrypted_entry))
    conn.commit()
    conn.close()

def clearEntireDatabase(database_name): #used to clear all contents of a given database's tables
    print(f"Destroying all data inside of '{database_name}.db'")

    try:
        conn = sqlite3.connect(f"{database_name}.db") #connect to database
        cursor = conn.cursor() #rebirth carla

        """
        Buckle up people (and future me probably) because the information I'm about to unload onto you is a tough pill to swallow:
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
    print(f"Sucessfully wiped '{database_name}'")

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
      #print(user_text)
      return user_text

def setupProgram():
    initializeJournalDatabase()
    global signInProcess

    clearTLF()
    signInProcess = 0
    root.bind("<Control-f>", fullscreenToggle)

def nextSignInStep(step_skip, event=None):
    global signInProcess, sentErrorMessage, sentBlankErrorMessage
    sentErrorMessage = False
    sentBlankErrorMessage = False
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
            global sentErrorMessage, sentBlankErrorMessage
            entered_answer = ytcon_entry.get().strip().lower()

            if not entered_answer and not sentBlankErrorMessage: #if entry box is blank, go back
                invalid_entry_label = tk.Label(tl_frm, text="Field cannot be blank.", fg="red")
                invalid_entry_label.pack(anchor="w")
                sentBlankErrorMessage = True 
                return
            elif not entered_answer and sentBlankErrorMessage:
                return
            if entered_answer in ("y", "yes"): #if the returned text, converted into lowercase (so that entering a capitilized Y works too) is y
                root.unbind("<Return>")
                nextSignInStep(1) #start process to run next step
            else: #if the returned text isn't y, and 
                ytcon_entry.delete(0, "end") #clear entry box
                if not sentErrorMessage: #if sent_error_message is false (used to avoid sending multiple errors messages
                    entry_error_label = tk.Label(tl_frm, text="Please input a valid answer.", fg="red")
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
        global first_username_attempt, sentBlankErrorMessage
        entered_username = username_entry.get().strip().lower()

        if not entered_username and not sentBlankErrorMessage: #if entry box is blank, go back
            invalid_entry_label = tk.Label(tl_frm, text="Field cannot be blank.", fg="red")
            invalid_entry_label.pack(anchor="w")
            sentBlankErrorMessage = True
            return
        elif not entered_username and sentBlankErrorMessage:
            return

        root.unbind("<Return>")
        username_exists = usernameExistenceCheck(entered_username)

        if username_exists:
            global current_user_username
            current_user_username = entered_username

            welcome_back_label = tk.Label(tl_frm, text=f"Welcome back {current_user_username}.")
            welcome_back_label.pack(anchor="w")
            root.unbind("<Return>")
            root.after(1500, lambda: nextSignInStep(2))
        else:
            first_username_attempt = entered_username
            nextSignInStep(1)


    root.bind("<Return>", process_username_input)

def confirmNewUsername():
    confirm_username_label = tk.Label(tl_frm, text="It doesn't seem like that username exists yet. Please re-enter the username to confirm its creation.")
    confirm_username_label.pack(anchor="w")

    confirm_username_entry = tk.Entry(tl_frm)
    confirm_username_entry.pack(anchor="w")
    confirm_username_entry.focus()

    def process_username_confirmation(event):
        global sentErrorMessage, sentBlankErrorMessage
        entered_username = confirm_username_entry.get().strip().lower()

        if not entered_username and not sentBlankErrorMessage: #if entry box is blank, go back
            invalid_entry_label = tk.Label(tl_frm, text="Field cannot be blank.", fg="red")
            invalid_entry_label.pack(anchor="w")
            sentBlankErrorMessage = True
            return
        elif not entered_username and sentBlankErrorMessage:
            return


        if entered_username == first_username_attempt:
            try:
                global current_user_username
                createNewUsername(entered_username)
                current_user_username = entered_username
                username_created_label = tk.Label(tl_frm, text=f"Created username entry for '{entered_username}'.")
                username_created_label.pack(anchor="w")
                root.unbind("<Return>")
                root.after(1500, lambda: nextSignInStep(1))
            except Exception as e:
                print(f"Database insertion failed: {e}")
                database_error_label = tk.Label(tl_frm, text=f"Something went wrong when trying to create a username entry for '{entered_username}'. Try again.", fg="red")
                database_error_label.pack(anchor="w")
                return
            
        else:
            confirm_username_entry.delete(0, "end")
            if not sentErrorMessage: #if sent_error_message is false (used to avoid sending multiple errors messages
                entry_error_label = tk.Label(tl_frm, text="Usernames do not match. Please try again.", fg="red")
                entry_error_label.pack(anchor="w")
                sentErrorMessage = True
    
    root.bind("<Return>", process_username_confirmation)

def createOrReadEntry():
    enquiry_create_or_read_label = tk.Label(tl_frm, text="'1' for new journal entry '2' to read previous entries")
    enquiry_create_or_read_label.pack(anchor="w")

    enquiry_create_or_read_entry = tk.Entry(tl_frm)
    enquiry_create_or_read_entry.pack(anchor="w")
    enquiry_create_or_read_entry.focus()

    def process_create_or_read(event):
        global sentErrorMessage, sentBlankErrorMessage
        entered_answer = enquiry_create_or_read_entry.get().strip().lower()

        if not entered_answer and not sentBlankErrorMessage: #if entry box is blank, go back
            invalid_entry_label = tk.Label(tl_frm, text="Field cannot be blank.", fg="red")
            invalid_entry_label.pack(anchor="w")
            sentBlankErrorMessage = True 
            return
        elif not entered_answer and sentBlankErrorMessage:
            return
        
        if entered_answer in ("1", "one"):
            root.unbind("<Return>")
            nextSignInStep(1)
        elif entered_answer in ("2", "two"):
            root.unbind("<Return>")
            nextSignInStep(2)
        else:
            enquiry_create_or_read_entry.delete(0, "end")
            if not sentErrorMessage: #if sent_error_message is false (used to avoid sending multiple errors messages
                entry_error_label = tk.Label(tl_frm, text="Please enter a valid answer", fg="red")
                entry_error_label.pack(anchor="w")
                sentErrorMessage = True
    
    root.bind("<Return>", process_create_or_read)

def createNewJournalEntry():
    clearTLF()
    global sentErrorMessage, sentBlankErrorMessage
    sentErrorMessage = False
    sentBlankErrorMessage = False
    print("New journal entry selected")

    journal_entry_name = ""
    plain_journal_entry_text = ""
    cipher_key = ""

    def newJournalName():
        journal_name_enquiry_label = tk.Label(tl_frm, text=f"What would you like to name your new journal entry?")
        journal_name_enquiry_label.pack(anchor="w")

        journal_name_entry = tk.Entry(tl_frm)
        journal_name_entry.pack(anchor="w")
        journal_name_entry.insert(0, journal_entry_name)
        journal_name_entry.focus()

        def name_journal(event):
            entered_answer = journal_name_entry.get().strip().lower()

            if not entered_answer and not sentBlankErrorMessage: #if entry box is blank, go back
                invalid_entry_label = tk.Label(tl_frm, text="Field cannot be blank.", fg="red")
                invalid_entry_label.pack(anchor="w")
                sentBlankErrorMessage = True 
                return
            elif not entered_answer and sentBlankErrorMessage:
                return
            else:
                root.unbind("<Return>")
                nonlocal journal_entry_name
                journal_entry_name = entered_answer
                clearTLF()
                print(f"Sucessfully saved {journal_entry_name} as journal entry name")
                root.after(1, lambda: journal_entry_text())

        root.bind("<Return>", name_journal)

    def journal_entry_text():
        clearTLF()
        global sentErrorMessage, sentBlankErrorMessage
        nonlocal journal_entry_name
        sentErrorMessage = False
        sentBlankErrorMessage = False

        journal_name_display_label = tk.Label(tl_frm, text=f"Journal Entry:{journal_entry_name}")
        journal_name_display_label.pack(anchor="w")

        journal_text_box = tk.Text(tl_frm, height=24, wrap="word")
        journal_text_box.pack(anchor="w", fill="x", expand=True)
        journal_text_box.insert("1.0", plain_journal_entry_text)
        journal_text_box.focus()

        def save_journal_entry(event=None):
            entered_answer = journal_text_box.get("1.0", "end-1c")

            if not entered_answer and not sentBlankErrorMessage: #if entry box is blank, go back
                invalid_entry_label = tk.Label(tl_frm, text="Field cannot be blank.", fg="red")
                invalid_entry_label.pack(anchor="w")
                sentBlankErrorMessage = True 
                return
            elif not entered_answer and sentBlankErrorMessage:
                return
            else:
                save_entry_button.destroy()
                nonlocal plain_journal_entry_text
                plain_journal_entry_text = entered_answer
                clearTLF()
                print(f"Sucessfully saved journal entry text")
                root.after(1, lambda: chooseCipherKey())

        save_entry_button = tk.Button(tl_frm, text="Save and Submit Entry", command= lambda: save_journal_entry())
        save_entry_button.pack(side="left")

    def chooseCipherKey():
        clearTLF()
        global sentErrorMessage, sentBlankErrorMessage
        nonlocal journal_entry_name
        sentErrorMessage = False
        sentBlankErrorMessage = False
        journal_name_display_label = tk.Label(tl_frm, text=f"Journal Entry:{journal_entry_name}")
        journal_name_display_label.pack(anchor="w")

        set_cipher_key_label = tk.Label(tl_frm, text="Please set the key to your cipher.")
        set_cipher_key_label.pack(anchor="w")

        set_cipher_key_warning_label = tk.Label(tl_frm, text="NOTE:You will need this to decode your entry again, please choose something you will remember, or write it down!", fg="red")
        set_cipher_key_warning_label.pack(anchor="w")

        cipher_entry_entry = tk.Entry(tl_frm)
        cipher_entry_entry.pack(anchor="w")
        cipher_entry_entry.insert(0, cipher_key)
        cipher_entry_entry.focus()

        def save_cipher_key(event=None):
            global sentErrorMessage, sentBlankErrorMessage
            entered_answer = cipher_entry_entry.get().strip().lower()

            if not entered_answer and not sentBlankErrorMessage: #if entry box is blank, go back
                invalid_entry_label = tk.Label(tl_frm, text="Field cannot be blank.", fg="red")
                invalid_entry_label.pack(anchor="w")
                sentBlankErrorMessage = True 
                return
            elif not entered_answer and sentBlankErrorMessage:
                return
            else:
                save_cipher_key_button.destroy()
                nonlocal cipher_key
                cipher_key = entered_answer
                clearTLF()
                print(f"Sucessfully saved cipher key")
                root.after(1, lambda: confirmSaveCommit())
        
        save_cipher_key_button = tk.Button(tl_frm, text="Save Cipher Key", command= lambda: save_cipher_key())
        save_cipher_key_button.pack(side="left")

    def confirmSaveCommit():
        clearTLF()
        global sentErrorMessage, sentBlankErrorMessage
        sentErrorMessage = False
        sentBlankErrorMessage = False
        current_user_label = tk.Label(tl_frm, text=f"Current user: '{current_user_username}'")
        current_user_label.pack(anchor="w")

        current_journal_name_label = tk.Label(tl_frm, text=f"Current journal name:'{journal_entry_name}'")
        current_journal_name_label.pack(anchor="w")

        current_cipher_key_label = tk.Label(tl_frm, text=f"Current cipher key:'{cipher_key}'")
        current_cipher_key_label.pack(anchor="w")

        confirm_all_label = tk.Label(tl_frm, text = "Are you sure you want to save and commit this journal entry? y/n")
        confirm_all_label.pack(anchor="w")

        yes_or_no_entry = tk.Entry(tl_frm)
        yes_or_no_entry.pack(anchor="w")
        yes_or_no_entry.focus()
        def yes_or_no(event):
                global sentErrorMessage, sentBlankErrorMessage
                entered_answer = yes_or_no_entry.get().strip().lower()
        
                if not entered_answer and not sentBlankErrorMessage: #if entry box is blank, go back
                    invalid_entry_label = tk.Label(tl_frm, text="Field cannot be blank.", fg="red")
                    invalid_entry_label.pack(anchor="w")
                    sentBlankErrorMessage = True 
                    return
                elif not entered_answer and sentBlankErrorMessage:
                    return                
                if entered_answer in ("y", "yes"):
                    encryptThenSubmit()
                elif entered_answer in ("n", "no"):
                    rewindSteps()
                else:
                    yes_or_no_entry.delete(0, "end")
                    if not sentErrorMessage: #if sent_error_message is false (used to avoid sending multiple errors messages
                        entry_error_label = tk.Label(tl_frm, text="Please enter a valid answer", fg="red")
                        entry_error_label.pack(anchor="w")
                        sentErrorMessage = True
            
        root.bind("<Return>", yes_or_no)

    def rewindSteps():
        clearTLF()
        current_user_label = tk.Label(tl_frm, text=f"Current user: '{current_user_username}'")
        current_user_label.pack(anchor="w")

        current_journal_name_label = tk.Label(tl_frm, text=f"Current journal name:'{journal_entry_name}'")
        current_journal_name_label.pack(anchor="w")

        current_cipher_key_label = tk.Label(tl_frm, text=f"Current cipher key name:'{cipher_key}'")
        current_cipher_key_label.pack(anchor="w")
        
        rewind_intro_label = tk.Label(tl_frm, text=f"Which step would you like to rewind to? 1/2/3/4")
        rewind_intro_label.pack(anchor="w")

        options = ["1:Journal Name", "2:Journal Entry", "3:Cipher Key", "4:Back"]
        for item in options:
            option_label = tk.Label(tl_frm, text=item)
            option_label.pack(anchor="w")

        rewind_option_entry = tk.Entry(tl_frm)
        rewind_option_entry.pack(anchor="w")
        rewind_option_entry.focus()
        def process_create_or_read(event):
            global sentErrorMessage, sentBlankErrorMessage
            entered_answer = rewind_option_entry.get().strip().lower()
        
            if not entered_answer and not sentBlankErrorMessage: #if entry box is blank, go back
                invalid_entry_label = tk.Label(tl_frm, text="Field cannot be blank.", fg="red")
                invalid_entry_label.pack(anchor="w")
                sentBlankErrorMessage = True 
                return
            elif not entered_answer and sentBlankErrorMessage:
                return
        
            if entered_answer in ("1", "one"):
                newJournalName()
            elif entered_answer in ("2", "two"):
                journal_entry_text()
            elif entered_answer in ("3", "three"):
                chooseCipherKey()
            elif entered_answer in ("4", "four"):
                confirmSaveCommit()
            else:
                rewind_option_entry.delete(0, "end")
                if not sentErrorMessage: #if sent_error_message is false (used to avoid sending multiple errors messages
                    entry_error_label = tk.Label(tl_frm, text="Please enter a valid answer", fg="red")
                    entry_error_label.pack(anchor="w")
                    sentErrorMessage = True
            
        root.bind("<Return>", process_create_or_read)

    def encryptThenSubmit():
        nonlocal plain_journal_entry_text, cipher_key
        encrypted_entry_result = vigenereCipher(
            plain_journal_entry_text, cipher_key, "encrypt"
        )
        finalEntry(encrypted_entry_result)

    def finalEntry(encrypted_entry_result):
        global current_user_username
        nonlocal journal_entry_name
        clearTLF()
        saveJournalEntry(current_user_username, journal_entry_name, encrypted_entry_result) #run at end of code
        complete_journal_label = tk.Label(tl_frm, text="Sucessfully saved journal entry!")
        complete_journal_label.pack(anchor="w")
        print("Complete journal entry saved")
        root.after(1500, lambda: nextSignInStep(-1))

    newJournalName()

def viewJournalEntries():
    print("not created yet. WIP")
    end_label = tk.Label(tl_frm, text=f"not created yet")
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
    elif signInProcess == 5:
        createNewJournalEntry()
    elif signInProcess == 6:
        viewJournalEntries()  
    else:
        clearTLF()
        print("oopsies")
# endregion

# region Ran Code
quit_button = tk.Button(br_frm, text="Quit", name="donotdelete_quit", command=root.destroy)
quit_button.pack(side="right")
clearUsernameDatabase_button = tk.Button(br_frm, text="Clear Journal Database", name="donotdelete_clear", command=lambda: clearEntireDatabase("journal"))
clearUsernameDatabase_button.pack(side="right")

setupProgram()
nextSignInStep(1) #kickstarts rest of code

root.mainloop()
# endregion