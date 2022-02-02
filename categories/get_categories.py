import requests
from bs4 import BeautifulSoup
import html5lib
from datetime import datetime

def getCategories(parent_category, link):

	print(parent_category, link)
		
	url = 'https://www.euro.com.pl' + link
	response = requests.get(url, headers={'User-agent':'Mozilla/5.0'})
	soup = BeautifulSoup(response.text, 'html5lib')
	anchors = soup.find_all('a', {'class':'category-list-box-link'})
	divs = soup.find('div', {'class':'category-list-box-number'})
	count = soup.find('div', {'class':'count'})
	if count:
		count = count.text.strip()[1:-1]
	else:
		count = ''

	if not anchors:
		links.append([parent_category, link, count])
	else:
		anchor_hrefs = [anchor['href'] for anchor in anchors]

		if link in anchor_hrefs:
			links.append([parent_category, link, count])
		else:	
			for i, href in enumerate(anchor_hrefs):
				getCategories(parent_category, href)


if __name__ == '__main__':

	start_links = [
		'/agd.bhtml',
		'/agd-do-zabudowy.bhtml',
		'/agd-male.bhtml',
		'/rtv.bhtml',
		'/telefony-i-nawigacja-gps.bhtml',
		'/komputery.bhtml',
		'/gry-i-konsole.bhtml'
	]

	links = []
	categories_with_parent = []

	for link in start_links:
		getCategories(link, link)

	for item in links:
		parent = item[0][1:-6]
		child = item[1][1:-6]
		categories_with_parent.append(f'{parent_category},{child},{item[1]},{item[2]}')

	napis = 'parent,category,link_to_category,offers_count\n'
	napis += '\n'.join(categories_with_parent)

	with open('categories.csv', 'w') as f:
		f.write(napis)