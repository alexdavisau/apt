# main.py
import dearpygui.dearpygui as dpg
import config
import ui
import sys
import traceback

def run_application():
    try:
        print(f"Running Python version: {sys.version}")
        
        # Create context first
        dpg.create_context()
        
        try:
            # Create viewport
            dpg.create_viewport(title="Alation Dochub Uploader", width=800, height=600)
            dpg.setup_dearpygui()
            
            # Create windows after viewport setup
            ui.create_config_window()
            ui.create_main_window()
            
            # Determine initial window
            if config.config_exists():
                print("Config found — loading main window.")
                dpg.configure_item("config_window", show=False)
                dpg.configure_item("main_window", show=True)
            else:
                print("Config not found — showing config setup.")
                dpg.configure_item("config_window", show=True)
                dpg.configure_item("main_window", show=False)
            
            # Show viewport and start event loop
            dpg.show_viewport()
            dpg.start_dearpygui()
            
        except Exception as e:
            print(f"Error in DearPyGui operations: {e}")
            traceback.print_exc()
        finally:
            # Always clean up context
            dpg.destroy_context()
            
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    run_application()
