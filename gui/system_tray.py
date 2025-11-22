from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QCoreApplication
import os
import webbrowser

class SystemTray(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set icon
        icon_path = os.path.join(os.getcwd(), "icon.png")
        if os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
        
        self.setVisible(True)
        
        # Context Menu
        self.menu = QMenu()
        
        dashboard_action = QAction("Open Dashboard", self)
        dashboard_action.triggered.connect(self.open_dashboard)
        self.menu.addAction(dashboard_action)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QCoreApplication.instance().quit)
        self.menu.addAction(quit_action)
        
        self.setContextMenu(self.menu)
        
        # Click handling is now done in controller or here
        # self.activated.connect(self.on_activated) 

    def open_dashboard(self):
        webbrowser.open("http://127.0.0.1:8000")

    def on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.open_dashboard()
