import sqlite3
import datetime
import os
import pandas as pd



def get_image_attachments_with_details(db_location:str , verbose:bool=False) -> pd.DataFrame:
    # Connect to the database
    conn = sqlite3.connect(db_location)
    cursor = conn.cursor()

    # Query to get image attachments along with sender, date, and group details
    query = """
    SELECT 
        attachment.filename, 
        attachment.mime_type, 
        attachment.total_bytes, 
        attachment.transfer_name,
        message.date,
        message.is_from_me,
        handle.id AS sender_id,
        chat.display_name AS group_name
    FROM 
        message
    LEFT JOIN 
        message_attachment_join ON message.ROWID = message_attachment_join.message_id
    LEFT JOIN 
        attachment ON attachment.ROWID = message_attachment_join.attachment_id
    LEFT JOIN 
        handle ON message.handle_id = handle.ROWID
    LEFT JOIN 
        chat_message_join ON message.ROWID = chat_message_join.message_id
    LEFT JOIN 
        chat ON chat.ROWID = chat_message_join.chat_id
    WHERE 
        attachment.mime_type LIKE 'image/%'
    """

    results = cursor.execute(query).fetchall()

    # Make a db to store the results
    df = pd.DataFrame(results, columns=['filename', 'mime_type', 'total_bytes', 'transfer_name', 'date', 'is_from_me', 'sender_id', 'group_name'])

    for result in results:
        filename, mime_type, total_bytes, transfer_name, date, is_from_me, sender_id, group_name = result

        # Replace the ~ with the actual home directory path
        filename = filename.replace('~', '/Users/pierrenikitits')

        # Check if the file exists at the filename location
        if os.path.exists(filename):
            full_path = filename
            print(f'\nFile found: {full_path}') if verbose else None

            # Determine sender information
            sender = 'Me' if is_from_me else sender_id

            # Convert the iMessage date format to a human-readable format
            date_string = '2001-01-01'
            mod_date = datetime.datetime.strptime(date_string, '%Y-%m-%d')
            unix_timestamp = int(mod_date.timestamp())*1000000000
            new_date = int((date+unix_timestamp)/1000000000)
            readable_date = datetime.datetime.fromtimestamp(new_date).strftime("%Y-%m-%d %H:%M:%S")

            # Add the results to the DataFrame
            df.loc[len(df)] = {'filename': full_path, 'mime_type': mime_type, 'total_bytes': total_bytes, 'transfer_name': transfer_name, 'date': readable_date, 'is_from_me': is_from_me, 'sender_id': sender, 'group_name': group_name}

            # Display the details
            print(f"Sent by: {sender}") if verbose else None
            print(f"Date: {readable_date}") if verbose else None
            print(f"Group Name: {group_name if group_name else 'No Group (Direct Message)'}") if verbose else None
        else:
            print(f"File not found: {filename}") if verbose else None
            continue

    conn.close()
    print("\nImage retrieval completed.") if verbose else None
    print(df.shape) if verbose else None
    return df



def get_last_image(group_name:str , db_location:str) -> str:
    df = get_image_attachments_with_details(db_location)
    df = df[df['group_name'] == group_name]
    
    # drop dates that are ints
    df = df[~df['date'].astype(str).str.isdigit()]
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date')
    
    # reset the index
    df = df.reset_index(drop=True)

    # get the last image
    last_image = df.iloc[-1]
    return last_image['filename'] , last_image['date'] , last_image['group_name'] , last_image['sender_id'] , last_image['total_bytes'] , last_image['transfer_name']