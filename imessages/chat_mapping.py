import sqlite3



def get_chat_mapping(db_location: str) -> dict:
    conn = sqlite3.connect(db_location)
    cursor = conn.cursor()
    cursor.execute("SELECT room_name, display_name FROM chat")
    result_set = cursor.fetchall()
    mapping = {room_name: display_name for room_name, display_name in result_set}
    conn.close()
    return mapping