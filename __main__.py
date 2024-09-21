from PyQt6.QtWidgets import QApplication
import sys
from .ui.split.chat_window import ChatApp



if __name__ == '__main__':
    """
    Main entry point for the application.
    Run `python -m iMessagesNet` to start the application.
    """
    app = QApplication(sys.argv)
    chat_app = ChatApp()
    chat_app.show()
    sys.exit(app.exec())