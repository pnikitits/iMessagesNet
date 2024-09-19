from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QScrollArea, QTextEdit, QPushButton, QApplication, QMenuBar
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut, QAction
from datetime import datetime
import pandas as pd
from .message_utils import get_messages, get_unique_chats
from .ui_components import create_chat_button, create_chat_area , apply_shadow_effect
from .config import COLORS
from ...imessages.contacts import fetch_contacts
from ...llm.prompts import df_to_prompt , correction_prompt
from ...llm.current_llm import LLMAgent
from ...imessages.send_messages import send_message
import threading


class ChatApp(QWidget):
    response_signal = pyqtSignal(str)


    def __init__(self):
        super().__init__()
        self.contact = fetch_contacts() # keys are names, values are a list of phone numbers for that contact

        self.messages_df = get_messages(contact_dict=self.contact)


        self.chats = get_unique_chats(self.messages_df)
        self.last_update_time = datetime.now()
        
        # Color customization
        self.colors = COLORS

        self.initUI()
        
        # Set up timer for periodic updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_messages)
        self.timer.start(5000)  # Update every 5 seconds

        self.llm_is_busy = False
        self.response_signal.connect(self.update_input_area)


        # Set up keyboard shortcuts
        self.full_screen_shortcut = QShortcut(QKeySequence('Ctrl+F'), self)
        self.full_screen_shortcut.activated.connect(self.enter_fullscreen)

        self.escape_shortcut = QShortcut(QKeySequence('Escape'), self)
        self.escape_shortcut.activated.connect(self.exit_fullscreen)

        self.is_fullscreen = False
        self.left_area_visible = True

        self.left_area_shortcut = QShortcut(QKeySequence('Ctrl+B'), self)
        self.left_area_shortcut.activated.connect(self.toggle_left_area)

        


    def get_name_from_number(self, number):
        for name, numbers in self.contact.items():
            if number in numbers:
                return name # If the number is found, return the name
        return number # If the name is not found, return the number


    def initUI(self):
        self.setWindowTitle('Chat Application')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet(f"background-color: {self.colors['app_background']};")

        # Create main layout
        main_layout = QHBoxLayout()

        # Create scrollable button area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Style the scroll bars
        scroll_bar_style = f"""
            QScrollBar:vertical {{
                background: {self.colors['scroll_bar_background']};
                width: 5px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.colors['scroll_bar_handle']};
                min-height: 20px;
                border-radius: 2px;
            }}
            QScrollBar::add-line:vertical {{
                height: 0px;
            }}
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            """
        # Apply the style to the whole application
        app = QApplication.instance()
        app.setStyleSheet(scroll_bar_style)
        
        button_widget = QWidget()
        self.button_layout = QVBoxLayout(button_widget)
        
        self.buttons = []
        for chat in self.chats:
            btn = create_chat_button(chat, self.switch_chat, self.colors, self.get_name_from_number(chat))
            self.button_layout.addWidget(btn)
            self.buttons.append(btn)
        self.button_layout.addStretch(1)
        
        scroll_area.setWidget(button_widget)
        scroll_area.setMinimumWidth(200)
        scroll_area.setStyleSheet("border: none;")

        # Create chat area
        self.chat_areas = {}
        chat_layout = QVBoxLayout()
        for chat in self.chats:
            text_edit = create_chat_area(self.colors)
            chat_layout.addWidget(text_edit)
            self.chat_areas[chat] = text_edit
            if chat != self.chats[0]:
                text_edit.hide()
        

        # Create input area
        self.input_area = QTextEdit()
        self.input_area.setFixedHeight(50)
        self.input_area.setStyleSheet(f"""
            background-color: {self.colors['input_background']};
            color: {self.colors['input_text']};
            border-radius: 10px;
        """)
        self.input_area = apply_shadow_effect(self.input_area, 'black', 10, 0, 0)

        send_button = QPushButton('Send')
        send_button.clicked.connect(self.send_message)
        send_button.setStyleSheet(f"""
            background-color: {self.colors['button_background']};
            color: {self.colors['button_text']};
            padding: 10px;
            margin: 2px;
            border: none;
            text-align: left;
            border-radius: 10px; /* Rounded corners */
        """)
        send_button = apply_shadow_effect(send_button, 'black', 10, 0, 0)


        self.button_1 = QPushButton('Analyze chat')
        self.button_1.clicked.connect(self.analyze_chat)
        self.button_1.setStyleSheet(f"""
            background-color: {self.colors['button_background']};
            color: {self.colors['button_text']};
            padding: 10px;
            margin: 2px;
            border: none;
            text-align: left;
            border-radius: 10px; /* Rounded corners */
        """)
        self.button_1 = apply_shadow_effect(self.button_1, 'black', 10, 0, 0)


        self.button_2 = QPushButton('Correct input')
        self.button_2.clicked.connect(self.correct_input)
        self.button_2.setStyleSheet(f"""
            background-color: {self.colors['button_background']};
            color: {self.colors['button_text']};
            padding: 10px;
            margin: 2px;
            border: none;
            text-align: left;
            border-radius: 10px; /* Rounded corners */
        """)
        self.button_2 = apply_shadow_effect(self.button_2, 'black', 10, 0, 0)



        input_layout = QHBoxLayout()
        input_layout.addWidget(self.button_2)
        input_layout.addWidget(self.button_1)
        input_layout.addWidget(self.input_area)
        input_layout.addWidget(send_button)

        # Combine chat and input layouts
        chat_input_layout = QVBoxLayout()
        chat_input_layout.addLayout(chat_layout)
        chat_input_layout.addLayout(input_layout)

        # Create a splitter for resizable areas
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(scroll_area)

        chat_widget = QWidget()
        chat_widget.setLayout(chat_input_layout)
        self.splitter.addWidget(chat_widget)

        # Set stretch factors
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 4)

        main_layout.addWidget(self.splitter)
        self.setLayout(main_layout)

        self.current_chat = self.chats[0]
        self.populate_chats()

        # switch to the first chat
        self.switch_chat(self.current_chat)

        # self.create_menu_bar(main_layout)


    def switch_chat(self, chat):
        self.chat_areas[self.current_chat].hide()
        self.chat_areas[chat].show()
        self.current_chat = chat

        # clear the input area
        self.input_area.clear()

        
        for button in self.buttons:
            if button.text() == self.get_name_from_number(chat):
                # Change the color of the button to indicate that it is the current chat (to red)
                button.setStyleSheet(f"""
                    background-color: {self.colors['button_selected']};
                    color: {self.colors['white']};
                    padding: 10px;
                    margin: 2px;
                    border: none;
                    text-align: left;
                    border-radius: 10px; /* Rounded corners */
                    border: 2px solid black;
                """)
            else:
                button.setStyleSheet(f"""
                    background-color: {self.colors['button_background']};
                    color: {self.colors['button_text']};
                    padding: 10px;
                    margin: 2px;
                    border: none;
                    text-align: left;
                    border-radius: 10px; /* Rounded corners */
                """)


        



    def send_message(self):
        message = self.input_area.toPlainText().strip()
        if message:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.add_message_to_chat(self.current_chat, "You", now, message, True)
            self.input_area.clear()
            # Here you would typically add code to save this message to your data source

            current_chat_is_group = self.current_chat in self.messages_df['group_chat_name'].unique()

            if current_chat_is_group:
                # Send message to group chat
                print(f"Sending message to {self.current_chat}")
                print(f"Message: {message}")
                # send_message(message, self.current_chat, group_chat=True)
            else:
                # Send message to individual chat
                print(f"Sending message to {self.current_chat}")
                print(f"Message: {message}")
                send_message(message, self.current_chat, group_chat=False)


    def analyze_chat(self):
        if self.llm_is_busy:
            return
        self.llm_is_busy = True

        self.button_1.setText("Analyzing...")

        def run_analysis():
            # Get all messages for the current chat
            current_chat_is_group = self.current_chat in self.messages_df['group_chat_name'].unique()

            current_chat_messages = None
            if current_chat_is_group:
                current_chat_messages = self.messages_df[self.messages_df['group_chat_name'] == self.current_chat]
            else:
                current_chat_messages = self.messages_df[self.messages_df['phone_number'] == self.current_chat]
                current_chat_messages = current_chat_messages[current_chat_messages['group_chat_name'] == '']

            last_five_messages_by_date = current_chat_messages.sort_values('date').tail(5)
            # reset index
            last_five_messages_by_date = last_five_messages_by_date.reset_index(drop=True)

            # AI
            prompt = df_to_prompt(last_five_messages_by_date)

            agent = LLMAgent()
            response = agent.run_model(prompt)
            del agent
            self.llm_is_busy = False

            # put the response in the input_area
            self.response_signal.emit(response)

        # Start a new thread to run the analysis
        analysis_thread = threading.Thread(target=run_analysis)
        analysis_thread.start()

    def update_input_area(self, response):
        self.input_area.clear()
        self.input_area.setText(response)
        self.button_1.setText("Analyze chat")
        self.button_2.setText("Correct input")



    def correct_input(self):
        if self.input_area.toPlainText().strip() == "" or self.llm_is_busy:
            return
        self.llm_is_busy = True

        self.button_2.setText("Correcting...")

        def run_correction():
            current_text = self.input_area.toPlainText().strip()
            prompt = correction_prompt(current_text)

            agent = LLMAgent()
            response = agent.run_model(prompt)
            del agent
            self.llm_is_busy = False

            # put the response in the input_area
            self.response_signal.emit(response)

        # Start a new thread to run the correction
        correction_thread = threading.Thread(target=run_correction)
        correction_thread.start()




    def populate_chats(self):
        for chat in self.chats:
            self.update_chat_area(chat)


    def update_chat_area(self, chat):
        # chat_messages = self.messages_df[(self.messages_df['group_chat_name'] == chat) | (self.messages_df['phone_number'] == chat)]

        all_group_chat_names = self.messages_df['group_chat_name'].unique() # Get all unique group chat names
        all_group_chat_names = [chat for chat in all_group_chat_names if chat != ''] # Remove empty group chat names

        if chat in all_group_chat_names:
            chat_messages = self.messages_df[self.messages_df['group_chat_name'] == chat] # Get all messages for the group chat
        else:
            chat_messages = self.messages_df[self.messages_df['phone_number'] == chat] # Get all messages for the individual chat
            chat_messages = chat_messages[chat_messages['group_chat_name'] == ''] # Filter out messages that are part of a group chat



        chat_messages = chat_messages.sort_values('date')
        self.chat_areas[chat].clear()
        for _, message in chat_messages.iterrows():

            

            sender = "You" if message['is_from_me'] else f"{message['sender']}"
            self.add_message_to_chat(chat, sender, message['date'], message['body'], message['is_from_me'])



    def add_message_to_chat(self, chat, sender, date, body, is_from_me):
        background_color = "lightblue"
        text_color = "black"

        self.chat_areas[chat].append(
            f'<div style="background-color: {background_color}; padding: 5px; margin: 5px; border-radius: 10px; color: {text_color}">'
            f'<strong>{sender}</strong> ({date}):<br>{body}</div>'
        )
    






    def update_messages(self):
        new_messages_df = get_messages(contact_dict=self.contact)
        
        # Filter for new messages
        new_messages = new_messages_df[pd.to_datetime(new_messages_df['date']) > self.last_update_time]
        
        if not new_messages.empty:
            self.messages_df = pd.concat([self.messages_df, new_messages]).drop_duplicates().reset_index(drop=True)
            new_chats = get_unique_chats(self.messages_df)
            
            for chat in new_chats:
                if chat not in self.chats:
                    self.chats.append(chat)
                    self.add_new_chat_button(chat)
                    self.add_new_chat_area(chat)
            
            for chat in self.chats:
                self.update_chat_area(chat)
            
            self.last_update_time = datetime.now()

    def add_new_chat_button(self, chat):
        btn = create_chat_button(chat, self.switch_chat, self.colors, self.get_name_from_number(chat))
        self.buttons.append(btn)
        self.button_layout.insertWidget(len(self.buttons) - 1, btn)

    def add_new_chat_area(self, chat):
        text_edit = create_chat_area(self.colors)
        text_edit.hide()
        self.chat_areas[chat] = text_edit
        self.layout().itemAt(0).widget().widget().layout().itemAt(1).widget().layout().insertWidget(len(self.chat_areas) - 1, text_edit)
        

    def enter_fullscreen(self):
        if not self.is_fullscreen:
            self.showFullScreen()
            self.is_fullscreen = True
    
    def exit_fullscreen(self):
        if self.is_fullscreen:
            self.showNormal()
            self.is_fullscreen = False


    def toggle_left_area(self):
        # toggle the visibility of the scroll_area
        if self.left_area_visible:
            self.splitter.widget(0).hide()
            self.left_area_visible = False
        else:
            self.splitter.widget(0).show()
            self.left_area_visible = True


    # def create_menu_bar(self, layout):
    #     # Create a menu bar
    #     menubar = QMenuBar()

    #     # Create 'View' menu
    #     view_menu = menubar.addMenu("View")

    #     # Fullscreen action (Cmd+F)
    #     fullscreen_action = QAction("Enter Full Screen", self)
    #     fullscreen_action.setShortcut(QKeySequence('Ctrl+F'))  # Cmd+F on macOS
    #     fullscreen_action.triggered.connect(self.enter_fullscreen)
    #     view_menu.addAction(fullscreen_action)
        
    #     # Toggle sidebar action (Cmd+B)
    #     toggle_sidebar_action = QAction("Toggle Sidebar", self)
    #     toggle_sidebar_action.setShortcut(QKeySequence('Ctrl+B'))  # Cmd+B on macOS
    #     toggle_sidebar_action.triggered.connect(self.toggle_left_area)
    #     view_menu.addAction(toggle_sidebar_action)

    #     # # Exit fullscreen action (Escape)
    #     # exit_fullscreen_action = QAction("Exit Full Screen", self)
    #     # exit_fullscreen_action.setShortcut(QKeySequence('Escape'))
    #     # exit_fullscreen_action.triggered.connect(self.exit_fullscreen)
    #     # view_menu.addAction(exit_fullscreen_action)

    #     # Add the menu bar to the layout
    #     layout.setMenuBar(menubar)
