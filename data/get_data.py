import requests
from bs4 import BeautifulSoup
import html5lib
import pandas as pd
import numpy as np
import time
from datetime import datetime

# funkcja pobiera i zwraca unikalne identyfikatowy produktów oraz linki do ofert
def getIds(url, check_end, domain_name):

	response = requests.get(url, headers={'User-agent': 'Mozilla/5.0'})

	if response.status_code != requests.codes.ok:
		exit(response.status_code)

	if response.url.find(check_end) < 0:
		return pd.DataFrame()
		
	soup = BeautifulSoup(response.text, 'html5lib')

	items = soup.find_all('div', {'class':'product-tile js-UA-product'})

	if len(items) < 1:
		return pd.DataFrame()

	plus = [int(item['data-product-plu']) for item in items]
	ids = [int(item['data-product-id']) for item in items]
	hrefs = [f'https://{domain_name}' + item['data-product-href'] for item in items]

	return pd.DataFrame({'plu': plus, 'product_id': ids, 'href': hrefs})

# funkcja na podstawie postarczonego identyfikatora pobiera i zwraca cene, rabat, kod rabatowy
def getPrices(productId, domain_name):

	regular, discount, discount_amount, discount_proc, discount_code, availability = None, None, None, None, None, None

	response = requests.get(f'https://{domain_name}/web-cached/product-detail/sticky-header.ltr?productId={productId}', headers={'User-agent': 'Mozilla/5.0'})
	
	if response.status_code != requests.codes.ok:
		return False

	soup = BeautifulSoup(response.text, 'html5lib')

	if soup.find('div', {'class':'price-old'}) and soup.find('div', {'class':'product-price'}):

		regular = float(''.join(soup.find('div', {'class':'price-old'}).text.split()).replace(',','.').replace('zł', ''))
		discount = float(''.join(soup.find('div', {'class':'product-price'}).text.split()).replace(',','.').replace('zł', ''))
		discount_amount = regular - discount
		discount_proc = round((1 - (discount / regular))*100, 2)

	elif not soup.find('div', {'class':'price-old'}) and soup.find('div', {'class':'product-price'}):

		regular = float(''.join(soup.find('div', {'class':'product-price'}).text.split()).replace(',','.').replace('zł', ''))
		discount, discount_amount, discount_proc = 0, 0, 0

	else:

		regular, discount, discount_amount, discount_proc = np.nan, np.nan, np.nan, np.nan

	# discount_code

	if soup.find('strong'):

		discount_code = soup.find('strong').text.strip()

	else:

		discount_code = np.nan

	# availability

	if soup.find('div', {'class':'action-section'}):

		availability = soup.find('div', {'class':'action-section'}).text.strip().lower()

	else:

		availability = np.nan

	if None in [regular, discount, discount_amount, discount_proc, discount_code, availability]:
		return False
	else:
		return {
			'regular': regular,
			'discount': discount,
			'discount_amount': discount_amount,
			'discount_proc': discount_proc,
			'discount_code': discount_code,
			'availability': availability
		}

# funkcja pobiera i zwraca aktualny kod promocji
def getCode(url):

	response = requests.get(url, headers={'User-agent': 'Mozilla/5.0'})

	if response.status_code != requests.codes.ok:
		exit(response.status_code)
		
	soup = BeautifulSoup(response.text, 'html5lib')

	links = soup.find_all('a')

	for link in links:

		if link['href'].find('/search/agd,d11.bhtml?keyword=') > -1:
			return link['href'].split('=')[-1]

	return False

if __name__ == '__main__':

	# sprawdzamy czy promocja jest aktualna i jaki ma kod
	code = getCode('https://www.euro.com.pl/cms/nocna-promocja.bhtml')

	if code == False:
		exit()

	# jesli promocja jest aktualna tworzymy pomocnicze zmienne do przechowania danych i inne
	data, new_data = pd.DataFrame(), pd.DataFrame()
	page = 1

	# strona po stronie pobierane są identyfikatory i linki do ofert
	while True:

		url = f'https://www.euro.com.pl/search,strona-{page}.bhtml?keyword={code}'

		check_end = url.split(',')[0].split('/')[-1]
		domain_name = url.split('/')[2]

		part = getIds(url, check_end, domain_name)

		if part.empty:
			break

		part['domain_name'] = domain_name

		data = pd.concat([data, part], ignore_index=True)
		page += 1

	data['regular'] = 0
	data['discount'] = 0
	data['discount_amount'] = 0
	data['discount_proc'] = 0
	data['discount_code'] = ''
	data['availability'] = ''
	data['category'] = ''


	# pobierane sa ceny, rabaty, kody rabatowe z zebranych ofert link po linku
	for index, row in data.iterrows():

		prices = getPrices(row['product_id'], row['domain_name'])

		row['regular'] = prices['regular']
		row['discount'] = prices['discount']
		row['discount_amount'] = prices['discount_amount']
		row['discount_proc'] = prices['discount_proc']
		row['discount_code'] = prices['discount_code']
		row['availability'] = prices['availability']
		row['category'] = row['href'].split('/')[3]
		row['scraping_time'] = datetime.now()

		new_data = new_data.append(row)

	if new_data.empty:
		exit()

	# change columns order
	new_data = new_data[[
		'product_id',
		'plu',
		'regular',
		'discount',
		'discount_amount',
		'discount_proc',
		'discount_code',
		'availability',
		'href',
		'category',
		'domain_name',
		'scraping_time'
	]].sort_values(by=['discount_proc'], ascending=False)

	# zebrane dane zapisywane są w pliku csv
	new_data.to_csv(f'nocna-{datetime.now().strftime("%Y%m%d")}.csv', index=False)