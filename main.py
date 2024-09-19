from PyQt6.QtWidgets import QApplication
import sys
from .ui.split.chat_window import ChatApp



if __name__ == '__main__':
    app = QApplication(sys.argv)
    chat_app = ChatApp()
    chat_app.show()
    sys.exit(app.exec())