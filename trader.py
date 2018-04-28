import requests
import threading
import time
import datetime
from multiprocessing.pool import ThreadPool
from config import *
from binance.client import Client
from binance.websockets import BinanceSocketManager


PRICE_POOL=ThreadPool()
ORDER_POOL=ThreadPool()

LAST_ETH=0
LAST_BTC=0
LAST_USD=0

BASE="https://api.binance.com"
BUY="bids"
SELL="asks"
FEE=0.05/100

QTY=0.002
INCR=0.0000001
DECR=0.0000001
U_INCR=0.01
U_DECR=0.01

_SHUTDOWN=False
_time=lambda: datetime.datetime.now()

client=Client(KEY,SECRET)


def check_order(o):
	global client
	if get_orders():
		client.cancel_order(
			symbol=o['symbol'],
			orderId=o['orderId'])
		return False
	else:
		return True


def buy(symbol, b):
	global client

	o=client.order_limit_buy(
		symbol=symbol,
		quantity=b[0],
		price=b[1])

	time.sleep(3)
	check_order(o)


def sell(symbol, b):
	global client

	o=client.order_limit_sell(
    	symbol=symbol,
		quantity=b[0],
	    price=b[1])

	time.sleep(3)
	check_order(o)


def start(eth,btc,usd):
	amt_eth, price_eth = eth
	amt_btc, price_btc = btc
	amt_usd, price_usd = usd

	new_eth=round(float(price_eth), 6)
	new_usd=round(float(price_usd), 2)
	new_btc=round(float(price_btc), 2)

	o2=None

	o1 = ORDER_POOL.apply_async(buy, ("ETHBTC", [round(amt_eth,3), new_eth])).get()
	if o1:	
		o2 = ORDER_POOL.apply_async(sell, ("ETHUSDT", [round(amt_usd,3), new_usd])).get()
	if o2:
		o3 = ORDER_POOL.apply_async(buy, ("BTCUSDT", [round(amt_btc,6), new_btc])).get()


def get_order_book(symbol):
	params={"symbol":symbol, "limit":5}

	return requests.get(BASE+"/api/v1/depth",params=params).json()


def get_orders():
	global client

	o1=client.get_open_orders(symbol='BTCUSDT')
	o2=client.get_open_orders(symbol='ETHBTC')
	o3=client.get_open_orders(symbol='ETHUSDT')

	_len = len(o1) + len(o2) + len(o3)
	if _len > 0:
		return True
	else:
		return False

def run():
	global _SHUTDOWN

	while not get_orders():
		eth=PRICE_POOL.apply_async(get_order_book, ("ETHBTC",))
		btc=PRICE_POOL.apply_async(get_order_book, ("BTCUSDT",))
		usd=PRICE_POOL.apply_async(get_order_book, ("ETHUSDT",))

		logic(eth.get(),btc.get(),usd.get())


def logic(eth,btc,usdt):
	price_eth=float(eth[BUY][0][0])+INCR
	amt_eth = (1-FEE)*(float(QTY)/float(price_eth))
	_eth=(amt_eth, price_eth)

	price_usd=float(usdt[SELL][0][0])-U_DECR
	amt_usd=(1-FEE)*(float(amt_eth)*float(price_usd))
	_usd=(amt_usd, price_usd)

	price_btc=float(btc[BUY][0][0])+U_INCR
	amt_btc=(1-FEE)*(float(amt_usd)/float(price_btc))
	_btc=(amt_btc, price_btc)


	if round(amt_btc,6)>round(QTY,6):
		print("[%s] FOUND ARBITRAGE %f" % (str(_time()),round(amt_btc,6)))
		start(_eth,_btc,_usd)
	else:
		print("[%s] NO ARBITRAGE %f" % (str(_time()),amt_btc))


run()