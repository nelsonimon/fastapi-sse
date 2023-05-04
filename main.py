import logging

from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
from datetime import datetime
import asyncio
import uvicorn

#globals
MESSAGE_STREAM_DELAY = 1  # second
MESSAGE_STREAM_RETRY_TIMEOUT = 15000  # milisecond

logging.basicConfig(format='\n%(asctime)s\n   %(levelname)s\n   %(funcName)s(%(lineno)d)\n      %(message)s',
                    filename='sse_log.txt')
logging.getLogger('sse').setLevel(logging.DEBUG)

app = FastAPI()

def get_message():
    date_now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return date_now, True


@app.get("/stream")
async def message_stream(request: Request):
    async def event_generator():
        message_id:int=0

        while True:
            if await request.is_disconnected():
                logging.getLogger("sse").debug("Disconected")
                message_id:int=1
                break
            
            # Checks for new messages and return them to client if any
            date_now, exists = get_message()
            if exists:
                logging.getLogger("sse").debug("New Message")
                message_id+=1
                yield {
                    "event": "new_message",
                    "id": message_id,
                    "retry": MESSAGE_STREAM_RETRY_TIMEOUT,
                    "data": f"Now is {date_now}",
                }
            else:
                yield {
                    "event": "new_message",
                    "id": message_id,
                    "retry": MESSAGE_STREAM_RETRY_TIMEOUT,
                    "data": f"Now is {date_now}",
                }

            await asyncio.sleep(MESSAGE_STREAM_DELAY)

    return EventSourceResponse(event_generator())


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)