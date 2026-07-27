import tkinter as tk

root = tk.Tk()
root.state("zoomed")
root.title("Locked Journal")
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)
frm = tk.Frame(root, padx = 10, pady = 10)
frm.grid(row=0, column=0, sticky="nsew") #stretches frame around entire screen