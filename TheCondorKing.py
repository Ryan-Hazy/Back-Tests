import pandas as pd
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import csv
import time

# si dictates what stock is being read in the csv
si = 0

# this is the file that i get stock names from
stocks = pd.read_csv (r'C:\Users\KRAZY\Downloads\cboesymboldirweeklys.csv')

for i in range (0,566):
	#these are all of the variables use in the program
	rtc = 0
	rts = 0
	at = 0
	ii = 0
	change = 0
	ci = 0
	us = 0
	ls = 0
	sn = 0
	tds = 0
	sd = 0
	periods = 14
	period = 50
	priod = 200

	# api key
	key = 'GL6KHBOY3QPGD4QL'

	# this gets the weekly stock information to find the average and standard deviation
	ts = TimeSeries(key, output_format = 'pandas')
	data_tw, meta_tw = ts.get_weekly(stocks[' Stock Symbol'].iloc[si])

	# this makes it so i can work with the columns
	columns = ['open', 'high', 'low', 'close', 'volume']
	data_tw.columns = columns

	data_td, meta_td = ts.get_daily(stocks[' Stock Symbol'].iloc[si])

	columns = ['open', 'high', 'low', 'close', 'volume']
	data_td.columns = columns

# this fetches the last rsi value
	ti = TechIndicators(key, output_format = 'pandas')
	data_rsi, meta_data_rsi = ti.get_rsi(symbol = stocks[' Stock Symbol'].iloc[si], interval = 'daily', time_period = periods, series_type = 'close')
	data_rsi = data_rsi.iloc[::-1]
	
	# this is so that some of the key values can be  used in an if statement
	rsi = float(data_rsi.iloc[0])
	price = float(data_td['close'].iloc[0])

	df = data_td['close'].iloc[0:90]

	ivn = 0
	rico = 0

	for i in range(0, 89):
		qc = df.iloc[ivn] - df.iloc[ivn + 1]
		rico = qc + rtc
		ivn = ivn + 1

	cap = rico / df.iloc[0]

	sv = abs((cap / 90) * 10000)

	#this if statement is just one big filter
	if (rsi < 60) and (rsi > 40) and (sn < 20):

		# this finds the average rate of change over a 30 day period
		for i in range (0,29):
			change = abs((data_tw['close'].iloc[ii]- data_tw['open'].iloc[ii]))
			rtc = rtc + change
			ii =  ii + 1
		at = rtc/30

		#this finds the standard deviation of the average change per week over that 30 day period
		for i in range (0,29):
			tds = tds + ((abs((data_tw['close'].iloc[sn]) - (data_tw['open'].iloc[sn])) - at)**2)
			sd = (tds/29)**.5

		# this finds the 90% confidence interval for the strike prices
		ci = at + (1.645* (sd/5.477))
		
		# this is another filtering device, it gives each stock a score based on the prices to leg length ratio
		score = price/ci

		# this creates a csv file to write the stock information on
		with open(r'C:\Users\KRAZY\Downloads\080921.csv', 'a', newline='') as f:
			fieldnames = ['Ticker', 'Length', 'Score']
			thewriter = csv.DictWriter(f, fieldnames = fieldnames)

			# this part writes the information into the csv file
			thewriter.writerow({'Ticker' : stocks[' Stock Symbol'].iloc[si], 'Length' : ci, 'Score' : score})

	# this changes the stock for the next go around
	si = si + 1

	# this prints what number the program has completed last to see that it is working
	# and to see where it left off incase of an error, so i can start it from the last spot
	print(si)
		
