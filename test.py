from binance.client import Client
from config import *

client=Client(KEY,SECRET)

status = client.get_account_status(recvWindow=36000)