import asyncio
import websockets
from collections import deque
from validations import *
import queue
from find_ip_address import get_ip_address
from logging_frame import setup_logger
import threading
__version__ = "1.0.0"

logger = setup_logger("chat_client.py", log_file="chat_logging.log")


#  Bot Program
async def bot_client(gp):

    #  Creating websocket connection with server.
    ws = await websockets.connect("ws://" + get_ip_address() + ":8765/")
    try:
        dq = deque([])
        #  Sending name and group.
        name = "YRISC"
        await ws.send(name)
        await ws.send(gp)
        logger.info('Name and Group sent to the chat server')
        while True:
            #  Receiving messages.
            rev = await ws.recv()
            print(rev,"-------------[1]---------------")
            if ': ' not in rev:
                pass
            else:
                logger.info('Message received to YRISC.')
                msg = rev.split(": ")
                print(msg, '---------[1.1]------------')
                name = msg[0]
                cmd = msg[1]
                #  Checking the message is bot command or not.
                if cmd.startswith("#"):
                    async def command_receive(loop, cmd):
                        # cmd_id = user_input["cmdId"]
                        print(cmd, "-------------[2]---------------")
                        bot_cmd = name + '-' + gp + '-' + cmd[1:]       # Formatting as a command for Bot.
                        logger.info('Input is treated as YRISC command ' + bot_cmd)
                        dq.append(bot_cmd)          # Command is appending in to queue.
                        print(bot_cmd, "-------------[3]---------------")
                        logger.info('Input is appended to Q')
                        pop_cmnd = dq.popleft()
                        t_op = queue.Queue()
                        logger.info('calling bot')
                        cmnd_thread = threading.Thread(target=validation, args=(pop_cmnd, t_op, ))
                        cmnd_thread.start()     # Starting the thread with the Bot command in the queue.
                        logger.info('thread started.')
                        result = t_op.get().replace("\n", "<br>")      # Getting the result.
                        logger.info('output received. .')
                        await ws.send(str(result))      # Sending result to the server.
                        logger.info('output sent successfully. . ')
                    loop = asyncio.new_event_loop()
                    thread = threading.Thread(target=loop.run_forever)
                    future = asyncio.run_coroutine_threadsafe(command_receive(loop, cmd), loop)
                    thread.start()
                    future.cancel()
    finally:
        logger.info('connection closed')


# We are calling the Bot using this function.
def bot_call(grp):

    try:
        asyncio.get_event_loop().run_until_complete(bot_client(grp))
        asyncio.get_event_loop().run_forever()

    except RuntimeError:
        pass
