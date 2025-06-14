# gui.py

import tkinter as tk
from tkinter import messagebox
from ui import main_window


def start_gui(config, is_token_valid, status_message):
    """
    Initializes and runs the main Tkinter GUI with diagnostic prints.
    """
    print("GUI: Starting GUI setup...")
    try:
        # 1. Create the root window container
        print("GUI: Creating root Tk() window...")
        root = tk.Tk()
        print("GUI: Root window created.")

        root.title("APT - Alation Power Tools")
        root.geometry("800x600")

        # 2. Create an instance of our main application frame
        print("GUI: About to create MainApplication frame...")
        app = main_window.MainApplication(
            parent=root,
            config=config,
            is_token_valid=is_token_valid,
            status_message=status_message
        )
        print("GUI: MainApplication frame created.")

        app.pack(fill=tk.BOTH, expand=True)
        print("GUI: MainApplication frame packed into root window.")

        # 3. Start the Tkinter event loop
        print("GUI: Starting mainloop...")
        root.mainloop()
        print("GUI: Mainloop finished.")  # This will print when the app closes

    except Exception as e:
        print(f"GUI: A critical error occurred: {e}")
        messagebox.showerror("Fatal Error", f"A critical error occurred and the application must close: {e}")
        import traceback
        traceback.print_exc()