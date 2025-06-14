# gui.py

import tkinter as tk
from tkinter import messagebox
from ui import main_window

def start_gui(config, is_token_valid, status_message):
    """
    Initializes and runs the main Tkinter GUI with commands to force a redraw.
    """
    try:
        # 1. Create the root window container
        root = tk.Tk()
        root.title("APT - Alation Power Tools")
        root.geometry("800x600")

        # 2. Create an instance of our main application frame
        app = main_window.MainApplication(
            parent=root,
            config=config,
            is_token_valid=is_token_valid,
            status_message=status_message
        )
        app.pack(fill=tk.BOTH, expand=True)

        # 3. Force the window to update, draw itself, and take focus
        root.update()
        root.deiconify()
        root.lift()
        root.focus_force()

        # 4. Start the Tkinter event loop
        root.mainloop()

    except Exception as e:
        messagebox.showerror("Fatal Error", f"A critical error occurred and the application must close: {e}")
        import traceback
        traceback.print_exc()