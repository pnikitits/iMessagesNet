import os
import pandas as pd
from ...imessages.get_messages import read_messages



def get_messages(contact_dict):
    db_path = os.path.expanduser('~/Library/Messages/chat.db')
    data = read_messages(db_path, n=1000)

    # Remove messages where the body is empty
    data = [msg for msg in data if msg['body'] != '']

    # Remove the messages if it contains the following words
    words_to_remove = ['a ajouté un' , 'an image']
    data = [msg for msg in data if not any(word in msg['body'] for word in words_to_remove)]


    # contact_dict: keys are names, values are a list of phone numbers for that contact
    # Raplace phone numbers with names
    for msg in data:
        if msg['is_from_me']:
            msg['sender'] = 'Me'
        else:
            for name, phone_numbers in contact_dict.items():
                if msg['phone_number'] in phone_numbers:
                    msg['sender'] = name
                    break
            else:
                msg['sender'] = msg['phone_number']

    return pd.DataFrame(data)


def get_unique_chats(messages_df):
    individual_chats = messages_df[messages_df['group_chat_name'] == '']['phone_number'].unique()
    group_chats = messages_df[messages_df['group_chat_name'] != '']['group_chat_name'].unique()
    return list(individual_chats) + list(group_chats)


