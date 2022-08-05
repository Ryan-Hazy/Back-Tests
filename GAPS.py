import pandas as pd
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import csv
import numpy as np
from scipy.stats import norm
import math

key = 'GL6KHBOY3QPGD4QL'

# this section is getting data from the API
ts = TimeSeries(key, output_format='pandas')
data_td, meta_td = ts.get_daily('SPY', outputsize = 'full')
columns = ['open', 'high', 'low', 'close', 'volume']
data_td.columns = columns
data_td['TradeDate'] = data_td.index.date

data_vix = pd.read_csv(r'C:\Users\KRAZY\Downloads\VIX_History.csv')
colmuns = ['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE']
data_vix.columns = colmuns
data_vix = data_vix.iloc[::-1]

oytr = pd.read_csv(r'C:\Users\KRAZY\Downloads\DGS1.csv')
colims = ['DATE', 'DGS1']
oytr.columns = colims
oytr = oytr.iloc[::-1]

#this section makes all of the frames the same length
data_td_index = data_td.index
nbr = int(len(data_td_index))

price_df = data_td.iloc[9:nbr-4006]
price_df = price_df.iloc[::-1]
oytr_df = oytr['DGS1'].iloc[0:nbr-4006]
oytr_df = oytr_df.iloc[::-1]
vix_df = data_vix.iloc[0:nbr-4006]
vix_df = vix_df.iloc[::-1]

dte = float(30)
nob = 0
length = 0
iv = 30
wins = float(0)
win = float(0)
losses = float(0)
loss = float(0)
wp = float(0)
wlr = float(0)
kelly = float(0)
actval = float(30000)

for i in range(0,nbr-4006):
  priceopen = float(price_df['open'].iloc[iv])
  priceclose = float(price_df['close'].iloc[iv])
  prevhigh = float(price_df['high'].iloc[iv-1])
  prevlow = float(price_df['low'].iloc[iv-1])
  vixopen = float(vix_df['OPEN'].iloc[iv])
  vixclose = float(vix_df['CLOSE'].iloc[iv])

  if(priceopen > prevhigh):
      nob = 1
      volly = float(vixopen/100)
      strikeprice = math.floor(priceopen)
      riskfreerate = float(oytr_df.iloc[iv]/100)
      years = float(dte/365)

      topleft = float(np.log((priceopen/strikeprice)))
      topright = float((((volly**2)/2) + riskfreerate) * years)
      top = float(topleft + topright)
      bottom = float(volly*(years**.5))

      done = float(top/bottom)
      dtwo = float(done - bottom)

      x = done
      y = dtwo

      donecdf = float(norm.cdf(x))
      dtwocdf = float(norm.cdf(y))

      bsright = float(donecdf*priceopen)
      bsleftone = float(dtwocdf*strikeprice)
      bslefttwo = float(np.exp(-1*riskfreerate*years))
      bsleft = float(bsleftone*bslefttwo)

      callbuyvalue = bsright - bsleft
      aos = float(math.floor((actval * .27) / callbuyvalue))

      volly = float(vixclose / 100)
      riskfreerate = float(oytr_df.iloc[iv]/100)
      years = float((dte-length)/365)
      if (years <= 0):
          years = 1
      topleft = float(np.log((priceclose / strikeprice)))
      topright = float((((volly ** 2) / 2) + riskfreerate) * years)
      top = float(topleft + topright)
      bottom = float(volly * (years ** .5))

      done = float(top / bottom)
      dtwo = float(done - bottom)

      x = done
      y = dtwo

      donecdf = float(norm.cdf(x))
      dtwocdf = float(norm.cdf(y))

      bsright = float(donecdf * priceclose)
      bsleftone = float(dtwocdf * strikeprice)
      bslefttwo = float(np.exp(-1 * riskfreerate * years))
      bsleft = float(bsleftone * bslefttwo)

      callsellvalue = bsright - bsleft

      if (years <= 0):
          gain = float(0-callbuyvalue)
      gain = float((callsellvalue - callbuyvalue)*aos)
      profit = float(gain/callbuyvalue)
      actval = float(actval + gain)
      if (gain > 0):
          wins = float(wins + 1)
          win = float(win + gain)
      if (gain < 0):
          losses = float(losses + 1)
          loss = float(loss + gain)
      if (losses == 0 and wins > 0):
          wp = float(1)
          wlr = float(69)
      else:
          wp = float(wins/(wins + losses))
          wlr = float(win/abs(loss))
          if wlr == 0:
              kelly = 69
          else:
              kelly = float(wp - ((1 - wp) / wlr))
      with open(r'C:\Users\KRAZY\Downloads\debuggedgaps.csv', 'a', newline='') as f:
          fieldnames = ['Date', 'Buy Price', 'Sell Price', 'Gain', 'Profit', 'Length', 'Winning Probability', 'Win Loss Ratio', 'Kelly Criterion', 'Account Value']
          thewriter = csv.DictWriter(f, fieldnames=fieldnames)

          thewriter.writerow({'Date': price_df['TradeDate'].iloc[iv], 'Buy Price': callbuyvalue, 'Sell Price': callsellvalue, 'Gain': gain, 'Profit': profit, 'Length': length, 'Winning Probability': wp, 'Win Loss Ratio': wlr, 'Kelly Criterion': kelly, 'Account Value': actval})
  if(priceopen < prevlow):
      nob = 1
      volly = float(vixopen/100)
      strikeprice = math.floor(priceopen)
      riskfreerate = float(oytr_df.iloc[iv]/100)
      years = float(dte/365)

      topleft = float(np.log((priceopen/strikeprice)))
      topright = float((((volly**2)/2) + riskfreerate) * years)
      top = float(topleft + topright)
      bottom = float(volly*(years**.5))

      done = float(top/bottom)
      dtwo = float(done - bottom)

      x = done
      y = dtwo

      donecdf = float(norm.cdf(x))
      dtwocdf = float(norm.cdf(y))

      bsright = float(donecdf*priceopen)
      bsleftone = float(dtwocdf*strikeprice)
      bslefttwo = float(np.exp(-1*riskfreerate*years))
      bsleft = float(bsleftone*bslefttwo)

      putbuyvalue = bsleft - bsright
      aos = float(math.floor((actval * .27) / putbuyvalue))

      volly = float(vixclose / 100)
      riskfreerate = float(oytr_df.iloc[iv]/100)
      years = float((dte-1)/365)
      if (years <= 0):
          years = 1
      topleft = float(np.log((priceclose / strikeprice)))
      topright = float((((volly ** 2) / 2) + riskfreerate) * years)
      top = float(topleft + topright)
      bottom = float(volly * (years ** .5))

      done = float(top / bottom)
      dtwo = float(done - bottom)

      x = done
      y = dtwo

      donecdf = float(norm.cdf(x))
      dtwocdf = float(norm.cdf(y))

      bsright = float(donecdf * priceclose)
      bsleftone = float(dtwocdf * strikeprice)
      bslefttwo = float(np.exp(-1 * riskfreerate * years))
      bsleft = float(bsleftone * bslefttwo)

      putsellvalue = bsleft - bsright

      if (years <= 0):
          gain = float(0-putbuyvalue)
      gain = float((putsellvalue - putbuyvalue)*aos)
      profit = float(gain/putbuyvalue)
      actval = float(actval + gain)
      if (gain > 0):
          wins = float(wins + 1)
          win = float(win + gain)
      if (gain < 0):
          losses = float(losses + 1)
          loss = float(loss + gain)
      if (losses == 0 and wins > 0):
          wp = float(1)
          wlr = float(69)
      else:
          wp = float(wins/(wins + losses))
          wlr = float(win/abs(loss))
          if wlr == 0:
              kelly = 69
          else:
              kelly = float(wp - ((1 - wp) / wlr))
      with open(r'C:\Users\KRAZY\Downloads\debuggedgaps.csv', 'a', newline='') as f:
          fieldnames = ['Date', 'Buy Price', 'Sell Price', 'Gain', 'Profit', 'Length','Winning Probability','Win Loss Ratio','Kelly Criterion', 'Account Value']
          thewriter = csv.DictWriter(f, fieldnames=fieldnames)

          thewriter.writerow({'Date': price_df['TradeDate'].iloc[iv], 'Buy Price': putbuyvalue, 'Sell Price': putsellvalue, 'Gain': gain, 'Profit': profit, 'Length' : length, 'Winning Probability': wp, 'Win Loss Ratio': wlr, 'Kelly Criterion': kelly, 'Account Value' : actval})
      length = 0

  iv = iv + 1
  print(iv)

