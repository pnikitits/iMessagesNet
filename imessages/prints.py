def print_messages(messages):
    for message in messages:
        print(f"RowID: {message['rowid']}")
        print(f"Body: {message['body']}")
        print(f"Phone Number: {message['phone_number']}")
        print(f"Is From Me: {message['is_from_me']}")
        print(f"Cache Roomname: {message['cache_roomname']}")
        print(f"Group Chat Name: {message['group_chat_name']}")
        print(f"Date: {message['date']}")
        print("\n")