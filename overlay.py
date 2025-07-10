from PyQt5 import QtWidgets, QtCore, QtGui
import sys

class MinimizedButton(QtWidgets.QWidget):
    def __init__(self, restore_callback):
        super().__init__(None)
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.button = QtWidgets.QPushButton('⎯', self)
        self.button.setFixedSize(28, 28)
        self.button.setStyleSheet('''
            QPushButton {
                background-color: rgba(0,0,0,180);
                color: white;
                border: none;
                font-size: 18px;
                font-weight: bold;
                border-radius: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.15);
            }
        ''')
        self.button.clicked.connect(restore_callback)
        self.resize(28, 28)
        self.position_button()
        self.show()

    def position_button(self):
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = screen.height() - self.height() - 20
        self.move(x, y)

    def resizeEvent(self, event):
        self.position_button()
        super().resizeEvent(event)

class CaptionOverlay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.text = ''
        self.font = QtGui.QFont('American Typewriter', 12, QtGui.QFont.Bold)  # Changed to American Typewriter
        self.margin = 60  # Margin from bottom
        self.height = 38  # More compact bar height
        self.width_ratio = 0.6  # 60% of screen width
        self.minimized_button = None
        self.is_minimized = False
        self.is_paused = False
        self.on_pause_toggle = None
        self.resize_overlay()
        self.create_close_button()
        self.create_minimize_button()
        self.create_pause_button()
        self.show()

    def resize_overlay(self):
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        bar_width = int(screen.width() * self.width_ratio)
        bar_x = (screen.width() - bar_width) // 2
        bar_y = screen.height() - self.height - self.margin
        self.setGeometry(bar_x, bar_y, bar_width, self.height)
        if hasattr(self, 'close_button'):
            self.position_close_button()
        if hasattr(self, 'minimize_button'):
            self.position_minimize_button()
        if hasattr(self, 'pause_button'):
            self.position_pause_button()

    def create_close_button(self):
        self.close_button = QtWidgets.QPushButton('✕', self)
        self.close_button.setFixedSize(28, 28)
        self.close_button.setStyleSheet('''
            QPushButton {
                background-color: rgba(0,0,0,0);
                color: white;
                border: none;
                font-size: 18px;
                font-weight: bold;
                border-radius: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.15);
            }
        ''')
        self.close_button.clicked.connect(self.exit_app)
        self.position_close_button()

    def create_minimize_button(self):
        self.minimize_button = QtWidgets.QPushButton('⎯', self)
        self.minimize_button.setFixedSize(28, 28)
        self.minimize_button.setStyleSheet('''
            QPushButton {
                background-color: rgba(0,0,0,0);
                color: white;
                border: none;
                font-size: 18px;
                font-weight: bold;
                border-radius: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.15);
            }
        ''')
        self.minimize_button.clicked.connect(self.minimize_overlay)
        self.position_minimize_button()

    def create_pause_button(self):
        self.pause_button = QtWidgets.QPushButton('⏸', self)
        self.pause_button.setFixedSize(28, 28)
        self.pause_button.setStyleSheet('''
            QPushButton {
                background-color: rgba(0,0,0,0);
                color: white;
                border: none;
                font-size: 18px;
                font-weight: bold;
                border-radius: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.15);
            }
        ''')
        self.pause_button.clicked.connect(self.toggle_pause)
        self.position_pause_button()

    def set_pause_callback(self, callback):
        self.on_pause_toggle = callback

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_button.setText('▶')
        else:
            self.pause_button.setText('⏸')
        if self.on_pause_toggle:
            self.on_pause_toggle(self.is_paused)

    def position_close_button(self):
        margin = 8
        self.close_button.move(self.width() - self.close_button.width() - margin, margin)
        self.close_button.raise_()

    def position_minimize_button(self):
        margin = 8
        self.minimize_button.move(self.width() - self.close_button.width() - self.minimize_button.width() - 2*margin, margin)
        self.minimize_button.raise_()

    def position_pause_button(self):
        margin = 8
        self.pause_button.move(self.width() - self.close_button.width() - self.minimize_button.width() - self.pause_button.width() - 3*margin, margin)
        self.pause_button.raise_()

    def resizeEvent(self, event):
        self.position_close_button()
        self.position_minimize_button()
        self.position_pause_button()
        super().resizeEvent(event)

    def set_caption(self, text, timeout=5000):
        self.text = text
        self.update()
        if not self.is_minimized:
            self.show()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        rect = self.rect().adjusted(0, 0, 0, 0)
        color = QtGui.QColor(0, 0, 0, 180)
        painter.setBrush(color)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(rect, 20, 20)
        painter.setFont(self.font)
        painter.setPen(QtCore.Qt.white)
        text_rect = rect.adjusted(30, 0, -110, 0)  # leave space for close, minimize, pause buttons
        metrics = QtGui.QFontMetrics(self.font)
        max_width = text_rect.width()
        # Try to fit on one line, else wrap to two lines
        elided = metrics.elidedText(self.text, QtCore.Qt.ElideRight, max_width)
        if metrics.width(elided) <= max_width:
            # Fits on one line
            y = text_rect.y() + (text_rect.height() - metrics.height()) // 2 + metrics.ascent()
            painter.drawText(text_rect.x(), y, max_width, metrics.height(), QtCore.Qt.AlignHCenter, elided)
        else:
            # Wrap to two lines if needed
            words = self.text.split()
            line1 = ''
            line2 = ''
            for word in words:
                test_line = (line1 + ' ' + word).strip()
                if metrics.width(test_line) <= max_width:
                    line1 = test_line
                else:
                    if not line2:
                        line2 = word
                    else:
                        test_line2 = (line2 + ' ' + word).strip()
                        if metrics.width(test_line2) <= max_width:
                            line2 = test_line2
                        else:
                            line2 = metrics.elidedText(line2 + ' ' + word, QtCore.Qt.ElideRight, max_width)
                            break
            if line2:
                total_height = metrics.height() * 2
                y_offset = (text_rect.height() - total_height) // 2
                painter.drawText(text_rect.x(), text_rect.y() + y_offset + metrics.ascent(), max_width, metrics.height(), QtCore.Qt.AlignHCenter, line1)
                painter.drawText(text_rect.x(), text_rect.y() + y_offset + metrics.height() + metrics.ascent(), max_width, metrics.height(), QtCore.Qt.AlignHCenter, line2)
            else:
                y = text_rect.y() + (text_rect.height() - metrics.height()) // 2 + metrics.ascent()
                painter.drawText(text_rect.x(), y, max_width, metrics.height(), QtCore.Qt.AlignHCenter, line1)

    def minimize_overlay(self):
        self.is_minimized = True
        self.hide()
        if not self.minimized_button:
            self.minimized_button = MinimizedButton(self.restore_overlay)
        self.minimized_button.show()

    def restore_overlay(self):
        self.is_minimized = False
        self.show()
        if self.minimized_button:
            self.minimized_button.hide()

    def exit_app(self):
        QtWidgets.QApplication.quit()
        sys.exit(0)

    def hide(self):
        super().hide()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    overlay = CaptionOverlay()
    overlay.set_caption('Live captions will appear here...')
    sys.exit(app.exec_()) 