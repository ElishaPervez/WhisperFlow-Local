from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QGraphicsDropShadowEffect, QHBoxLayout, QWidget
from PyQt6.QtGui import QColor, QPainter, QBrush
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
import random
import math

class Card(QFrame):
    hovered = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        
        # Add a subtle shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

    def enterEvent(self, event):
        self.hovered.emit(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hovered.emit(False)
        super().leaveEvent(event)

class ParticleBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.particles = []
        self.num_particles = 75
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_particles)
        self.timer.start(30) # ~30 FPS
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents) # Let clicks pass through
        self.init_particles()

    def init_particles(self):
        self.particles = []
        # Default to a reasonable size if widget hasn't been sized yet
        w = self.width() if self.width() > 0 else 800
        h = self.height() if self.height() > 0 else 600
        
        for _ in range(self.num_particles):
            self.particles.append({
                'x': random.random() * w,
                'y': random.random() * h,
                'vx': (random.random() - 0.5) * 1.5,
                'vy': (random.random() - 0.5) * 1.5,
                'size': random.random() * 3 + 1,
                'opacity': 0  # Start invisible for fade-in
            })

    def update_particles(self):
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            
            # Fade in logic
            if p['opacity'] < 100:
                p['opacity'] += 2
            
            # Bounce off walls
            if p['x'] < 0 or p['x'] > self.width(): p['vx'] *= -1
            if p['y'] < 0 or p['y'] > self.height(): p['vy'] *= -1
            
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw connections
        painter.setPen(QColor(255, 255, 255, 30))
        for i, p1 in enumerate(self.particles):
            for j, p2 in enumerate(self.particles):
                if i >= j: continue
                
                dx = p1['x'] - p2['x']
                dy = p1['y'] - p2['y']
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist < 100:
                    # Combined opacity based on distance AND fade-in
                    base_opacity = int((1 - dist/100) * 50)
                    fade_factor = min(p1['opacity'], p2['opacity']) / 100.0
                    final_opacity = int(base_opacity * fade_factor)
                    
                    painter.setPen(QColor(255, 255, 255, final_opacity))
                    painter.drawLine(int(p1['x']), int(p1['y']), int(p2['x']), int(p2['y']))
        
        # Draw particles
        painter.setPen(Qt.PenStyle.NoPen)
        for p in self.particles:
            painter.setBrush(QColor(255, 255, 255, int(p['opacity'])))
            painter.drawEllipse(int(p['x']), int(p['y']), int(p['size']), int(p['size']))

class VisualizerOverlay(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setFixedSize(300, 60)
        self.level = 0.0
        self.bars = 20
        
    def set_level(self, level):
        self.level = min(level * 5, 1.0) # Amplify a bit
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background pill
        painter.setBrush(QBrush(QColor(0, 0, 0, 180)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 30, 30)
        
        # Draw bars
        bar_width = 8
        gap = 4
        center_x = self.width() / 2
        
        painter.setBrush(QBrush(QColor(0, 120, 212))) # Blue
        
        for i in range(self.bars):
            dist = abs(i - self.bars/2)
            max_h = 40 - dist * 3
            if max_h < 5: max_h = 5
            
            current_h = max_h * (0.2 + self.level * 0.8)
            
            x = center_x + (i - self.bars/2) * (bar_width + gap)
            y = (self.height() - current_h) / 2
            
            painter.drawRoundedRect(int(x), int(y), int(bar_width), int(current_h), 2, 2)
