import asyncio
import websockets
import time
import csv
import json

ws_url = "wss://localhost:7070/com.emotiv.son"

cortex_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBJZCI6ImNvbS5lbW90aXYuY29uc3VtZXJhcHAiLCJhcHBWZXJzaW9uIjoiMS4wLjAiLCJleHAiOjE3MjQ5MzYxMzcsIm5iZiI6MTcyNDY3NjkzNywidXNlcklkIjoiYjE5YWE1MmEtMDk0Zi00NzAwLWIzYzYtZWZiMmMxMzEwYjJkIiwidXNlcm5hbWUiOiJzb25kb2hvOTciLCJ2ZXJzaW9uIjoiMi4wIn0.UutQystUYyWfwvGYQsEonNTks3Ibt8CIDrn-cX3JruU"
num_tests = 10

api_methods = [
    {
        "method": "queryDaySnapshots",
        "params": {
            "startDate": "2024-08-22",
            "endDate": "2024-10-22",
            "cortexToken": cortex_token
        }
    }
    ,
    {
        "method": "queryHourSnapshots",
        "params": {
            "startDate": "2024-07-22",
            "endDate": "2024-08-22",
            "cortexToken": cortex_token
        }
    }
    ,
    {
        "method": "queryWeekSnapshots",
        "params": {
            "cortexToken": cortex_token
        }
    }
    ,
    {
        "method": "querySnapshotsOfDate",
        "params": {
            "startDate": "2024-09-01",
            "endDate": "2024-09-02",
            "cortexToken": cortex_token
        }
    }
    ,
    {
        "method": "queryFirstSnapshot",
        "params": {
            "cortexToken": cortex_token
        }
    }
]

async def send_request(ws, method, params):
    request = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": method,
        "params": params
    }
    start_time = time.time()
    await ws.send(json.dumps(request))
    response = await ws.recv()
    end_time = time.time()
    response_data = json.loads(response)
    if "error" in response_data and response_data["error"]["code"] < 0:
        print(f"Error for {method}: {response_data['error']['message']}")
        return None
    return end_time - start_time

async def benchmark_api(ws, method, params):
    times = []
    for _ in range(num_tests):
        elapsed_time = await send_request(ws, method, params)
        if elapsed_time is not None:
            times.append(elapsed_time)
    return times

async def main():
    async with websockets.connect(ws_url, max_size=None) as ws:
        results = []
        for api in api_methods:
            method = api["method"]
            params = api["params"]
            # Exclude the token from the params
            filtered_params = {k: v for k, v in params.items() if k != "cortexToken"}
            times = await benchmark_api(ws, method, params)
            if times:
                average_time = sum(times) / len(times)
                results.append([method, json.dumps(filtered_params)] + times + [average_time])
        
        with open('benchmark_results.csv', 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            header = ['Method', 'Params'] + [f'Time_{i+1} (sec)' for i in range(num_tests)] + ['Average_Time (sec)']
            csvwriter.writerow(header)
            csvwriter.writerows(results)

if __name__ == "__main__":
    asyncio.run(main())