import tkinter as tk
from ld_train import *
from ld_probe import *

root = tk.Tk()
# root.geometry('720x900')

# ld train buttons
make_ld_train_buttons(tk, root)

# ld probe buttons
make_ld_probe_buttons(tk, root)

root.mainloop()
