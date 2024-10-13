import re
from datetime import datetime, date as dt_date
import pandas as pd

def process_data(messages):
    messages = messages.splitlines()
    
    # Regular expression to extract date, time, sender, and message
    pattern = r'(\d{2})/(\d{2})/(\d{4}), (\d{1,2}:\d{2}\s*[apAP][mM]) - (.*?): (.*)'

    data = []  # List to store parsed messages

    # Loop through each message
    for message in messages:
        match = re.match(pattern, message)
        if match:
            date = match.group(1)          # Date (day)
            month_number = match.group(2)  # Month number (to be used for both the number and the full name)
            month = datetime.strptime(month_number, "%m").strftime("%B")  # Full month name
            year = match.group(3)          # Year
            time = match.group(4)          # Time
            sender = match.group(5)        # Sender
            text = match.group(6)          # Message

            # Combine date (day), month_number, and year into a valid date object
            only_date = dt_date(int(year), int(month_number), int(date))  # Renamed date function to avoid conflict
            day_name = only_date.strftime("%A")
            
            # Convert Time to 24-hour format and extract the hour
            hour = datetime.strptime(time, '%I:%M %p').hour

            # Determine the period based on the hour
            if hour == 23:
                period = f"{hour}:00 - 00:00"
            elif hour == 0:
                period = "00:00 - 01:00"
            else:
                period = f"{hour}:00 - {hour + 1}:00"

            # Append parsed message to the list
            data.append([date, month, year, time, sender, text, month_number, only_date, day_name, period])

    # Create DataFrame from parsed data
    df = pd.DataFrame(data, columns=['Date','month', 'year', 'Time', 'Sender', 'Message', 'month_number', 'only_date', 'day_name', 'period'])

    # Convert Time to 24-hour format
    df['Time'] = df['Time'].apply(lambda x: datetime.strptime(x, '%I:%M %p').strftime('%H:%M'))

    return df