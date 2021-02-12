# This is a sample Python script to demonstrate basic websocket integration with RFC OS.
# We are using the STOMP messaging protocol over websockets for real time comms.

import random
import stomper
import asyncio
import websockets
import base64
import logging

from websockets.http import Headers

logger = logging.getLogger('websockets')
logger.setLevel(logging.WARN)
logger.addHandler(logging.StreamHandler())


async def connect_websocket():
    rfcos_uri = "ws://127.0.0.1:8888/websockets/messaging/websocket"

    user_name = 'admin'
    password = 'admin'
    authorization = user_name + ':' + password
    encoded_bytes = base64.b64encode(authorization.encode("utf-8"))
    encoded_str = str(encoded_bytes, "utf-8")
    headers = Headers({'Authorization': 'Basic ' + encoded_str})

    async with websockets.connect(rfcos_uri, extra_headers=headers) as websocket:
        await websocket.send('CONNECT\naccept-version:1.1,1.0\nheart-beat:10000,10000\n\n\u0000')
        connect_msg = await websocket.recv()
        print("Successfully connected the websocket {0}".format(connect_msg))

        v = str(random.randint(0, 1000))

        # Instead of the '*' wildcard a region id can be used to receive messages for a specific region
        sub = stomper.subscribe('/topic/tagBlinkLite.*', v, ack='auto')

        await websocket.send(sub)

        while True:
            d = await websocket.recv()
            msg_dict = stomper.unpack_frame(d)
            print(f"< {msg_dict['body']}")

            # Send a message back to the server to let it know we are still alive
            await websocket.send('\n')


if __name__ == '__main__':
    print('Starting up the websocket')
    asyncio.get_event_loop().run_until_complete(connect_websocket())
