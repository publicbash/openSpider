from selenium.webdriver.common.keys import Keys
from selenium import webdriver

import validators
import argparse #required for args
import csv 

from datetime import datetime #required for time log


class OpenSpider:

	def __init__(self, driver):
		self.driver = driver
		self.start_time = datetime.now()
		self.results =  []
		


	def crawl_url(self, site_url):
		print(f"Fetching {site_url}...")
		self.driver.get(site_url)

		elems = self.driver.find_elements("xpath", "//a[@href]")

		links = []
		for elem in elems:
			try:
				links.append(elem.get_attribute("href"))
			except Exception as e:
				print('An error occurred:', e)			

		result = {}
		result["url"] = site_url
		result["links"] = links

		self.results.append(result)
		

	def crawl_urls(self, urls):
		count = 1
		for url in urls:
			if validators.url(url):
				print(f'Crawl_url {count}/{len(urls)}: {url.strip()}')
				self.crawl_url(url.strip())
			else:
				print(f'Skip {count}/{len(urls)}: {url}')				
			count += 1
		return self.results	

	def print_result_complete(self, result):
		for link in result["links"]:
			print(link)
		print(f'Site: {result["url"]}')
		print(f'Quantity: {len(result["links"])}')


	def print_result_resume(self, result):
		print(f'Site: {result["url"]}')
		print(f'Quantity: {len(result["links"])}')

	def print_results_complete(self):
		for result in self.results:
			self.print_result_complete(result)

	def print_results_resume(self):
		for result in self.results:
			self.print_result_resume(result)

	def save_file(self, filename): 
		with open(filename, 'w', newline='') as file:
			writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC)
			writer.writerow(["Site", "Link"])
			for result in self.results:
				site = result["url"]
				for link in result["links"]:
					writer.writerow([site, link])
		file.close()

	def read_urls_from_file(self, filename):
		try:
			file1 = open(filename, 'r')
		except FileNotFoundError as e:
			print('File does not exist:', e)
		except Exception as e:
			print('An error occurred:', e)
	
		lines = file1.readlines()
  
		count = 0
		# Strips the newline character
		print("Lines in file:")
		for line in lines:
			count += 1
			line.strip()
			print("{}: {}".format(count, line.strip()))
		return lines


def setup_chrome_driver(args):
	options = webdriver.ChromeOptions()

	options.add_argument("--no-sandbox")
	options.add_argument("--disable-dev-shm-usage")

	options.add_argument('--headless')  #Options
	options.headless = True             #Options

	#The Chromium Team recently added a 2nd headless mode: --headless=chrome which gives you the full functionality of Chrome in headless mode, and even allows extensions. 
	#Use xvfb instead of headless options and install extension

	# Check Proxy
	if args.proxy_anon:
		print(f'Anonymous proxy: {args.proxy_anon}')
		proxy_anon = args.proxy_anon
		options.add_argument('--proxy-server=%s' % proxy_anon)


	options.add_argument('window-size=1920x1080')

	chrome_driver = webdriver.Chrome(options=options)
	return chrome_driver


def main():
	# Create the parser
	parser = argparse.ArgumentParser()
	# Add an argument
	parser.add_argument('--url', type=str)
	parser.add_argument('--o', type=str)
	parser.add_argument('--list', type=str)
	parser.add_argument('--proxy_anon', type=str)
	parser.add_argument('--print', type=str)
	args = parser.parse_args()

	if not args.url and not args.list:
		print("Args --url or --list must be specified")
		exit()
	if args.url and args.list:
		print("Must specify --url OR --list (not both)")
		exit()

	# Check valid url 
	if args.url:
		print(f'url: {args.url}')
		if not validators.url(args.url):
			print("invalid URL")
			exit()


		
	# Start driver and browser
	driver = setup_chrome_driver(args)
	os = OpenSpider(driver) 

	# Check input
	if args.list:
		urls = os.read_urls_from_file(args.list)
		os.crawl_urls(urls)
		#os.print_results_complete(results)
		os.print_results_resume()

	if args.url:
		url = args.url
		os.crawl_url(url)
		#os.print_result_complete(result)
#		os.print_results_complete()
		os.print_results_resume()
	

	# File output
	if args.o:
		print(f'Saving results in {args.o}')
		os.save_file(args.o)
		print("Saved")

	if args.print:
		os.print_results_complete()
		os.print_results_resume()

#	if args.proxy_anon:
#		print('Proxy not implemented yet')  


main()
