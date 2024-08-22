import json
import uuid
import datetime
import websocket
import copy

# WebSocket URL
ws_url = "wss://localhost:7070/com.emotiv.son"

# Load the data sample
with open('/Users/sondh/data/data_sample.json') as f:
    data_sample = json.load(f)

# Helper function to generate consumer insights data
def generate_consumer_data(data_type, start_date, end_date):
    entry = copy.deepcopy(data_sample)
    entry['uuid'] = str(uuid.uuid4())
    entry['data']['dateTime'] = [start_date.isoformat(), end_date.isoformat()]
    # print("nosh ", entry['data']['dateTime'])
    entry['data']['date'] = start_date.strftime('%Y-%m-%d')
    entry['dataType'] = data_type
    return entry

# Generate data for the entire year
def generate_yearly_data():
    current_year = datetime.datetime.now().year
    start_of_year = datetime.datetime(current_year, 1, 1)
    data_list = []

    # Minutes
    for i in range(525960):
        start = start_of_year + datetime.timedelta(minutes=i)
        end = start + datetime.timedelta(minutes=1)
        data_list.append(generate_consumer_data("consumerMetrics:minute", start, end))

    # Hours
    for i in range(8766):
        start = start_of_year + datetime.timedelta(hours=i)
        end = start + datetime.timedelta(hours=1)
        data_list.append(generate_consumer_data("consumerMetrics:hour", start, end))

    # Days
    for i in range(365):
        start = start_of_year + datetime.timedelta(days=i)
        end = start + datetime.timedelta(days=1)
        data_list.append(generate_consumer_data("consumerMetrics:date", start, end))

    # Weeks
    for i in range(52):
        start = start_of_year + datetime.timedelta(weeks=i)
        end = start + datetime.timedelta(weeks=1)
        print("son", i, start, end) 
        data_list.append(generate_consumer_data("consumerMetrics:week", start, end))

    # Months
    for i in range(12):
        start = datetime.datetime(current_year, i+1, 1)
        end = (start + datetime.timedelta(days=32)).replace(day=1)
        data_list.append(generate_consumer_data("consumerMetrics:month", start, end))

    # Year
    data_list.append(generate_consumer_data("consumerMetrics:year", start_of_year, start_of_year.replace(year=current_year + 1)))

    # All Time
    data_list.append(generate_consumer_data("consumerMetrics:allTime", start_of_year, start_of_year.replace(year=current_year + 1)))

    return data_list

# Helper function to split list into chunks
def chunk_list(data_list, chunk_size):
    for i in range(0, len(data_list), chunk_size):
        yield data_list[i:i + chunk_size]

# Function to send data via WebSocket in batches
def save_consumer_insights(data_list, cortex_token, chunk_size=100):
    print("Connecting to WebSocket...")
    ws = websocket.create_connection(ws_url)
    for chunk in chunk_list(data_list, chunk_size):
        request = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "saveConsumerInsights",
            "params": {
                "cortexToken": cortex_token,
                "consumerInsightsList": chunk
            }
        }
        ws.send(json.dumps(request))
        result = ws.recv()
        print("Batch result:", result)
    ws.close()

# Generate the data for the year
consumer_data = generate_yearly_data()

# print ("Data generated" ,len(consumer_data))
# with open('consumer_data.json', 'a') as file:
#     file.write(json.dumps(consumer_data, indent=4))
#     file.write('\n')

# Save the data via WebSocket
cortex_token = "YOUR_CORTEX_TOKEN"
result = save_consumer_insights(consumer_data, cortex_token)
print("Result:", result)
