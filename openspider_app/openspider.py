from datetime import datetime #required for time log
import csv 
import validators
from typing import Set
from rich.console import Console

from tracking_app.database import Posting, PostingRepository
from hashlib import sha1

console = Console()

class OpenSpider:

	def __init__(self, driver):
		self.driver = driver
		self.start_time = datetime.now()
		self.results =  []
		


	def crawl_url(self, site_url):
		print(f"Fetching {site_url}...")
		
		try:
			self.driver.get(site_url)
		except Exception as e:
			print('An error occurred on get:', e)			

		elems = self.driver.find_elements("xpath", "//a[@href]")

		links = []
		for elem in elems:
			try:
				links.append(elem.get_attribute("href"))
			except Exception as e:
				print('An error occurred on get_attribute("href"):', e)			

		result = {}
		result["url"] = site_url
		result["links"] = links

		self.print_result_resume(result)

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

	def save_new_in_db(self) -> Set[Posting]:

		today_date = datetime.today()
		formatted_today = today_date.strftime('%Y-%m-%d')

		postings = set()
		posting_repository = PostingRepository()
		for result in self.results:
			for link in result["links"]:
				#print('Link: {} - URL: {}'.format(result["links"], result["url"]))
				'''Get a SHA1 hash to identify each object.'''
				sha = sha1(link.lower().encode('utf-8')).hexdigest()

				if posting_repository.get_posting_by_sha(sha):
                    #print(sha)
					continue


				new_posting = Posting(
					sha=sha,
					url=link,
					site=result["url"],
					date_found=formatted_today,
				)
				postings.add(new_posting)

		console.log(f'About to save {len(postings)} urls')
		for posting in postings:
			posting_repository.create_posting(posting)
		console.log('Urls saved successfully!', style='green')
		return postings                    


	def read_urls_from_file(self, filename):
		try:
			file1 = open(filename, 'r')
		except FileNotFoundError as e:
			print('File does not exist:', e)
		except Exception as e:
			print('An error occurred on Open File:', e)
	
		lines = file1.readlines()
		lines = [line.strip() for line in lines]

		count = 0
		# Strips the newline character
		print("Lines in file:")
		for line in lines:
			count += 1
			line.strip()
			print("{}: {}".format(count, line.strip()))
		return lines