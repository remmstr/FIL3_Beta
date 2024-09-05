# Internal modules
from core.config import LoggerSettings
from ui.utils import CTkLoggingHandler
from ui.widgets.panel import ButtonHeader, PanelTemplate
from ui.widgets.table import TableOfCasques
from ui.panels import LogConsole
from core.resource import FontLibrary, IconLibrary
from devices import CasquesManager  # Importer pour accéder à la gestion des casques

# Requirements modules
from customtkinter import (
    CTkOptionMenu,
    CTkFrame,
    CTkLabel
)

# Built-in modules
import logging
import os
import threading
import time

class Home(PanelTemplate):
    def __init__(self, parent, title) -> None:
        # Initialize inherited class
        super().__init__(
            parent=parent,
            title=title,
            fg_color=('#CCD7E0', '#313B47')
        )
        
        # Set instance logger
        self.log = logging.getLogger('.'.join([__name__, type(self).__name__]))

        

        # Dropdown for APK selection
        self.selectbox_apk = CTkOptionMenu(self.header.widgets_frame, values=[], command=self.update_apk_folder)
        self.selectbox_apk.pack(anchor='e', side='right', padx=4)
        self.populate_folders()  # Remplir les dossiers APK

        # Label for APK version
        self.description_apk = CTkLabel(self.header.widgets_frame, text="Version de l'apk : ", font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 12), anchor='w')
        self.description_apk.pack(anchor='n', expand=True, side='right', fill='x', padx=3)


        self.main_frame = CTkFrame(self, fg_color=('#E7EBEF', '#293138'), corner_radius=4)
        self.main_frame.pack(anchor='nw', expand=True, fill='both', side='top', padx=6, pady=8)

        # Set the Table for the list of casques
        self.TableOfCasques = TableOfCasques(self.main_frame)
        self.TableOfCasques.pack(expand=True, side='top', fill='both', padx=4, pady=8)

        self.button_install = ButtonHeader(self.header.widgets_frame, text='Installation de tous les casques', tooltip='Installer tous les casques', icon_name='upload', command= self.TableOfCasques.installer_apks_et_solutions)
        self.button_install.pack(anchor='e', side='right', padx=25)

        # Create a separate frame for the console at the bottom
        self.console_frame = CTkFrame(self.main_frame, fg_color=('#E7EBEF', '#293138'), corner_radius=4)
        self.console_frame.pack(anchor='sw', expand=False, side='bottom', fill='x', padx=4, pady=8)

        self.console = LogConsole(self.console_frame, 'Console') 
        self.console.pack(anchor='sw', expand=True, fill='both', padx=4, pady=8)

        self.casques = CasquesManager()
        refresh_thread = threading.Thread(target=self.threadind_refresh_casque_and_UI, daemon=True).start()


    def threadind_refresh_casque_and_UI(self):

        while(1):
            self.casques.refresh_casques()
            self.TableOfCasques.refresh_table()
            time.sleep(2)



    def populate_folders(self):
        apk_dir = "APK"

        folders = [d for d in os.listdir(apk_dir) if os.path.isdir(os.path.join(apk_dir, d))]
        self.selectbox_apk.configure(values=folders)

        if folders:
            default_folder = folders[0]
            self.selectbox_apk.set(default_folder)
            self.update_apk_folder(default_folder)
            self.log.info(f"[DEBUG] Default folder set to: {default_folder}")  # Debugging line added

    def update_apk_folder(self, selected_folder):
        self.log.info(f"[DEBUG] Updating APK folder to: {selected_folder}")  # Debugging line added

        casques_manager = CasquesManager()
        casques_manager.set_apk_folder(selected_folder)