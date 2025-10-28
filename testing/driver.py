import asyncio
from task_executor.models.request import Request
from task_executor.models.task import IMMEDIATE_PRIORITY, ROUTINE_PRIORITY

from uas_messenger.publisher import Publisher
from uas_messenger.message import Message

async def main():
    pub = Publisher(host="127.0.0.1", port=5556)
    seq = 0
    print("Enter a task (or 'exit' to quit) ('!' for immediate execution): ")
    while True:
        task = input("> ")

        task_parts = task.split()
        if task_parts[0] == 'exit':
            break

        immediate = "!" in task

        if len(task_parts) < 1:
            print("Invalid input. Please enter a task.")
            continue

        elif len(task_parts) == 1:
            task_id = task_parts[0].replace("!", "")
            params = []

        else:
            task_id = task_parts[0].replace("!", "")
            try:
                params = [int(param) for param in task_parts[1:]]
            except ValueError:
                print("Invalid parameters. Please enter integers for parameters.")
                continue
            
        req = Request(
            request_id=seq,
            task_id=task_id,
            params=params,
            priority=IMMEDIATE_PRIORITY if immediate else ROUTINE_PRIORITY
        )
        msg = Message(topic="task_request", header=req.model_dump())
        print(f"Sending request: {req}")
        pub.send(msg)
        seq += 1

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")