import os
import subprocess



def send_message(message, phone_number, group_chat = False):
    # creating a file - note: text files end up being sent as normal text messages, so this is handy for
    # sending messages that osascript doesn't like due to strange formatting or characters
    file_path = os.path.abspath('imessage_tmp.txt')

    with open(file_path, 'w') as f:
        f.write(message)

    if not group_chat:
        command = f'tell application "Messages" to send (read (POSIX file "{file_path}") as «class utf8») to buddy "{phone_number}"'
    else:
        command = f'tell application "Messages" to send (read (POSIX file "{file_path}") as «class utf8») to chat "{phone_number}"'

    subprocess.run(['osascript', '-e', command])

    print(f"Sent message to {phone_number}: {message}")

    os.remove(file_path)



# if __name__ == '__main__':
#     message = "_"
#     phone_number = "QG direction 🚜👨🏻‍🌾"
#     send_message(message, phone_number , group_chat=True)
#     os.remove('imessage_tmp.txt')