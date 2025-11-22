
DARK_THEME = """
QMainWindow {
    background-color: #1e1e1e;
    color: #ffffff;
}

QWidget {
    background-color: #1e1e1e;
    color: #ffffff;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}

QFrame#Card {
    background-color: #2d2d2d;
    border-radius: 10px;
    border: 1px solid #3d3d3d;
}

QLabel {
    color: #e0e0e0;
}

QLabel#Title {
    font-size: 18px;
    font-weight: bold;
    color: #ffffff;
}

QPushButton {
    background-color: #0078d4;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #1084d9;
}

QPushButton:pressed {
    background-color: #006cc1;
}

QPushButton#SecondaryButton {
    background-color: #3d3d3d;
    color: #ffffff;
}

QPushButton#SecondaryButton:hover {
    background-color: #4d4d4d;
}

QComboBox {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 5px;
    padding: 5px;
    color: #ffffff;
}

QComboBox::drop-down {
    border: none;
}

QComboBox::down-arrow {
    image: none; /* Use a custom arrow if needed, or default */
    border-left: 1px solid #3d3d3d;
    width: 0px;
    height: 0px;
}

QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    color: #ffffff;
    selection-background-color: #0078d4;
    selection-color: #ffffff;
    border: 1px solid #3d3d3d;
}

QLineEdit {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 5px;
    padding: 5px;
    color: #ffffff;
}

QProgressBar {
    border: none;
    background-color: #2d2d2d;
    border-radius: 2px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #0078d4;
    border-radius: 2px;
}

QCheckBox {
    spacing: 8px;
    color: #e0e0e0;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #555;
    border-radius: 4px;
    background: #2d2d2d;
}

QCheckBox::indicator:unchecked:hover {
    border: 1px solid #0078d4;
}

QCheckBox::indicator:checked {
    background-color: #0078d4;
    border: 1px solid #0078d4;
}
"""
