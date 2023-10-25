import aiohttp
import asyncio
import csv
import os
from datetime import datetime
import threading
from queue import Queue

OUTPUT_FOLDER = "output"

async def send_post_request(url, body):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=body) as response:
                response_text = await response.text()
                return response_text
    except Exception as e:
        return f"Error sending POST request: {str(e)}"

def process_records(thread_id, queue):
    while not queue.empty():
        record = queue.get()
        url, body = record
        response_text = asyncio.run(send_post_request(url, body))

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response_file = os.path.join(OUTPUT_FOLDER, f"response_{thread_id}.txt")

        with open(response_file, "a") as file:
            file.write(f"Timestamp: {timestamp}\nURL: {url}\nResponse: {response_text}\n\n")

def main():
    csv_file = "/workspaces/chatGPT-experiments/parallel/input.csv"
    queue = Queue()

    try:
        if not os.path.exists(OUTPUT_FOLDER):
            os.makedirs(OUTPUT_FOLDER)
        else:
            for filename in os.listdir(OUTPUT_FOLDER):
                if filename.endswith(".txt"):
                    os.remove(os.path.join(OUTPUT_FOLDER, filename))

        with open(csv_file, "r") as csvfile:
            csv_reader = csv.reader(csvfile)
            header = next(csv_reader)  # Read the header row

            for row in csv_reader:
                if len(row) >= 2:
                    url, body = row
                    queue.put((url, body))
                else:
                    print(f"Invalid record in the CSV: {row}")

        # Create and start three threads for processing records
        threads = []
        for i in range(3):
            thread = threading.Thread(target=process_records, args=(i + 1, queue))
            threads.append(thread)
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

    except FileNotFoundError:
        print(f"File {csv_file} not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
