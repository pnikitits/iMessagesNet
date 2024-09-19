from PyQt6.QtWidgets import QPushButton, QTextEdit, QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor



def create_chat_button(chat, switch_chat_callback, colors, name):
    btn = QPushButton(f'{name}')
    btn.clicked.connect(lambda _, x=chat: switch_chat_callback(x))
    btn.setStyleSheet(f"""
        background-color: {colors['button_background']};
        color: {colors['button_text']};
        padding: 10px;
        margin: 2px;
        border: none;
        text-align: left;
        border-radius: 10px; /* Rounded corners */
    """)
    btn = apply_shadow_effect(btn, 'black', 10, 0, 0)
    return btn


def apply_shadow_effect(widget, color, blur_radius, x_offset=0, y_offset=0):
    shadow_effect = QGraphicsDropShadowEffect()
    shadow_effect.setBlurRadius(blur_radius)
    shadow_effect.setXOffset(x_offset)
    shadow_effect.setYOffset(y_offset)

    # change the color transparency to 0.5
    color = QColor(color)
    color.setAlphaF(0.5)

    shadow_effect.setColor(color)
    # Apply the shadow effect to the button
    widget.setGraphicsEffect(shadow_effect)
    return widget


def create_chat_area(colors):
    text_edit = QTextEdit()
    text_edit.setReadOnly(True)
    text_edit.setStyleSheet(f"""background-color: {colors['chat_background']};
                                border: none;""")
    return text_edit