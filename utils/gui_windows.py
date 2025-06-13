import dearpygui.dearpygui as dpg


def show_main_window(config, token_valid):
    status_text = "✅ Connected" if token_valid else "❌ Invalid token — please update config."

    dpg.create_context()
    dpg.create_viewport(title="DocHub Uploader", width=600, height=400)

    with dpg.window(label="DocHub Uploader", width=600, height=400):
        dpg.add_text(f"Connected to: {config['alation_url']}")
        dpg.add_text(f"Token Status: {status_text}", tag="token_status")

        dpg.add_button(label="Load Template", callback=load_template)
        dpg.add_button(label="Undo Last Upload", callback=undo_last_upload)

        dpg.add_button(label="Exit", callback=lambda: dpg.stop_dearpygui())

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

def load_template():
    print("Load template clicked — to be implemented.")

def undo_last_upload():
    print("Undo last upload clicked — to be implemented.")
