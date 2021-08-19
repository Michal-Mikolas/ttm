from os import linesep
import ccxt
import ttm
from datetime import datetime, timedelta
from pprint import pprint
import csv
import re

#
# Init
#
days_history = [30, 90, 180, 365, 500]

data_folder = 'output/find_pairs_statistics'

storage = ttm.storage.JSONFile("%s/storage.json" % (data_folder))

exchange = ccxt.okex()

#
# Get Data
#
pairs = ttm.Tools.get_pairs(exchange) #; print('# PAIRS:') ; pprint(pairs) ; print(len(pairs))
stats = {}
for pair in pairs:
	if ('USD' not in pair) and ('EUR' not in pair):
		continue

	print(pair)

	since = exchange.milliseconds() - (max(days_history) * 24 * 60 * 60 * 1000)
	ohlcvs_all = exchange.fetch_ohlcv(pair, '1d', since)
	stats[pair] = {
		'candles_count': len(ohlcvs_all),
	}

	for days in days_history:
		stats[pair][days] = {
			'candles_count': 0,
			'volatility_total': 0.0,
			'volatility_up': 0.0,
			'volatility_down': 0.0,
			'volatility_total_avg': 0.0,
		}

		ohlcvs = ohlcvs_all[-days:]
		if len(ohlcvs) < days:
			print('- skipping %d, only %d days history' % (days, len(ohlcvs)))
			continue

		for ohlcv in ohlcvs:
			(dt, _open, high, low, close, volume) = ohlcv

			if close > _open:
				volatility = high / low - 1
			else:
				volatility = low / high - 1

			stats[pair][days]['candles_count'] += 1
			stats[pair][days]['volatility_total'] += abs(volatility)
			if volatility > 0.0:
				stats[pair][days]['volatility_up'] += volatility
			if volatility < 0.0:
				stats[pair][days]['volatility_down'] += volatility

		stats[pair][days]['volatility_total_avg'] = stats[pair][days]['volatility_total'] / stats[pair][days]['candles_count']
		print('%d: %f' % (days, stats[pair][days]['volatility_total_avg']))

	stats[pair].update({
		'volatility_total': 0.0,
		'volatility_up': 0.0,
		'volatility_down': 0.0,
		'volatility_total_avg': 0.0,
	})
	for days in days_history:
		stats[pair]['volatility_total_avg'] += stats[pair][days]['volatility_total_avg']
		stats[pair]['volatility_total'] += stats[pair][days]['volatility_total']
		stats[pair]['volatility_up'] += stats[pair][days]['volatility_up']
		stats[pair]['volatility_down'] += stats[pair][days]['volatility_down']

	stats[pair]['volatility_total_avg'] = stats[pair]['volatility_total_avg'] / len(days_history)

	print('TOTAL: %f' % (stats[pair]['volatility_total_avg']))
	print('')

#
# Save stats
#

# JSON
stats = {pair:stats[pair] for pair in sorted(stats, key=lambda pair: stats[pair]['volatility_total_avg'], reverse=True)}
storage.save('stats', stats)

# CSV
with open("%s/results.csv" % (data_folder), 'w+', newline='') as file:
	writer = csv.writer(file)

	# Header
	header = ['Pair']
	for d in days_history:
		header.append('%d Volatility Total' % d)
		header.append('%d Volatility Up' % d)
		header.append('%d Volatility Down' % d)
		header.append('%d Volatility Total Avg' % d)
	header.append('Volatility Total Avg')
	header.append('Volatility Total')
	header.append('Volatility Up')
	header.append('Volatility Down')

	writer.writerow(header)

	for pair, stat in stats.items():
		row = [pair]
		for d in days_history:
			row.append(stat[d]['volatility_total'])
			row.append(stat[d]['volatility_up'])
			row.append(stat[d]['volatility_down'])
			row.append(stat[d]['volatility_total_avg'])
		row.append(stat['volatility_total_avg'])
		row.append(stat['volatility_total'])
		row.append(stat['volatility_up'])
		row.append(stat['volatility_down'])

		writer.writerow(row)
