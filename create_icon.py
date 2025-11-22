import sys
from PyQt6.QtGui import QGuiApplication, QImage, QPainter, QColor
from PyQt6.QtCore import Qt

def create_icon():
    app = QGuiApplication(sys.argv)
    
    # Create a 64x64 transparent image
    image = QImage(64, 64, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)

    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Draw a blue circle
    painter.setBrush(QColor(0, 120, 212))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(4, 4, 56, 56)
    
    # Draw a white 'W' (simple representation)
    painter.setPen(QColor(255, 255, 255))
    font = painter.font()
    font.setPixelSize(32)
    font.setBold(True)
    painter.setFont(font)
    painter.drawText(image.rect(), Qt.AlignmentFlag.AlignCenter, "W")

    painter.end()
    
    image.save("icon.png")
    print("icon.png created.")

if __name__ == "__main__":
    create_icon()
