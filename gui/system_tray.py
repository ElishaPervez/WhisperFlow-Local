from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QCoreApplication
import os

class SystemTray(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set icon
        icon_path = os.path.join(os.getcwd(), "icon.png")
        if os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
        else:
            print("Warning: icon.png not found")
            
        self.setVisible(True)
        
        # Context Menu
        self.menu = QMenu()
        
        show_action = QAction("Settings", self)
        show_action.triggered.connect(parent.show)
        self.menu.addAction(show_action)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QCoreApplication.instance().quit)
        self.menu.addAction(quit_action)
        
        self.setContextMenu(self.menu)
        
        self.activated.connect(self.on_activated)

    def on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.parent().show()
            self.parent().activateWindow()
