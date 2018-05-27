import requests
import threading
import time
import datetime
from multiprocessing.pool import ThreadPool
from config import *
from binance.client import Client
import sys

#logfile
#sys.stdout=open('log', 'w')


PRICE_POOL=ThreadPool()
ORDER_POOL=ThreadPool()

LAST_ETH=0
LAST_BTC=0
LAST_USD=0

BASE="https://api.binance.com"
BUY="bids"
SELL="asks"
FEE=0.05/100

QTY=0.0015
INCR=0.000001
DECR=0.000001
U_INCR=0.01
U_DECR=0.01

_SHUTDOWN=False
_time=lambda: datetime.datetime.now()

client=Client(KEY,SECRET)


def check_order(o):
	global client
	try:
		client.cancel_order(
			symbol=o['symbol'],
			orderId=o['orderId'],
			recvWindow=36000)
	except:
		pass


def buy(symbol, b):
	global client

	o=client.order_limit_buy(
		symbol=symbol,
		quantity=b[0],
		price=b[1],
		recvWindow=36000)

	time.sleep(3)
	check_order(o)


def sell(symbol, b):
	global client

	o=client.order_limit_sell(
    	symbol=symbol,
		quantity=b[0],
	    price=b[1],
	    recvWindow=36000)

	time.sleep(3)
	check_order(o)


def start(eth,btc,usd):
	amt_eth, price_eth = eth
	amt_btc, price_btc = btc
	amt_usd, price_usd = usd

	new_eth=round(float(price_eth), 6)
	new_usd=round(float(price_usd), 2)
	new_btc=round(float(price_btc), 2)

	#print(str(new_btc) + ' ' + str(round(amt_btc,6)))
	#print(str(new_eth) + ' ' + str(round(amt_eth,3)))
	#print(str(new_usd) + ' ' + str(round(amt_usd,5)))

	o1 = threading.Thread(target=buy, args=("ETHBTC", [round(amt_eth,3), new_eth]))
	o1.start()
	o2 = threading.Thread(target=sell, args=("ETHUSDT", [round(amt_usd,5), new_usd]))
	o2.start()
	o3 = threading.Thread(target=buy, args=("BTCUSDT", [round(amt_btc,6), new_btc]))
	o3.start()

def get_order_book(symbol):
	params={"symbol":symbol, "limit":5}

	return requests.get(BASE+"/api/v1/depth",params=params).json()


def run():
	while 1:
		eth=PRICE_POOL.apply_async(get_order_book, ("ETHBTC",))
		btc=PRICE_POOL.apply_async(get_order_book, ("BTCUSDT",))
		usd=PRICE_POOL.apply_async(get_order_book, ("ETHUSDT",))

		logic(eth.get(),btc.get(),usd.get())


def logic(eth,btc,usdt):
	price_eth=float(eth[BUY][0][0])+INCR
	amt_eth = float(QTY)/price_eth
	_eth=(amt_eth, price_eth)

	price_usd=float(usdt[SELL][0][0])-U_DECR
	amt_usd=float(amt_eth)
	_usd=(amt_usd, price_usd)
	qty_usd=float(amt_eth)*price_usd

	price_btc=float(btc[BUY][0][0])+U_INCR
	amt_btc=float(qty_usd)/price_btc
	_btc=(amt_btc, price_btc)


	if (1-(FEE*3)) * amt_btc>QTY+0.000001:
		print("[%s] FOUND ARBITRAGE %s" % (str(_time()),str(amt_btc)))
		t=threading.Thread(target=start, args=(_eth,_btc,_usd))
		t.start()
	else:
		print("[%s] NO ARBITRAGE %s" % (str(_time()),str(amt_btc)))



run()
