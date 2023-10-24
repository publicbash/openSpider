from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from seleniumwire import webdriver as sw_webdriver

from rich.console import Console
import argparse #required for args

import typer


from tracking_app.database import create_database, create_db_and_tables, PostingRepository

from openspider_app.openspider import OpenSpider


console = Console()

def setup_chrome_driver(args):
	options = webdriver.ChromeOptions()

	options.add_argument("--no-sandbox")
	options.add_argument("--disable-dev-shm-usage")

	options.add_argument('--headless')  #Options
#	options.headless = True             #Options

	options.add_argument('window-size=1920x1080')

	# Check Proxy
	if args.proxy_auth:
		print(f'Auth proxy: {args.proxy_auth}')
		proxy_auth = args.proxy_auth
		options_wire = {
			'proxy': {
				'http': proxy_auth,
				'https': proxy_auth,
				'no_proxy': 'localhost,127.0.0.1' # excludes
			}

		}
		chrome_driver = sw_webdriver.Chrome(options=options, seleniumwire_options=options_wire)


	if args.proxy_anon:
		print(f'Anonymous proxy: {args.proxy_anon}')
		proxy_anon = args.proxy_anon
		options.add_argument('--proxy-server=%s' % proxy_anon)

	if not args.proxy_auth:
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
	parser.add_argument('--proxy_auth', type=str)
	parser.add_argument('--print', type=str)
	parser.add_argument('--print_new', type=str)	
	parser.add_argument('--db', type=str)
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

	#
	# INPUT: URL / URL List File
	#

	# Check input
	if args.list:
		urls = os.read_urls_from_file(args.list)
		console.log(f'URL List Loaded. {len(urls)} lines', style='italic bold green')
		print(urls)
		os.crawl_urls(urls)
		#os.print_results_complete(results)
		os.print_results_resume()

	if args.url:
		url = args.url
		os.crawl_url(url)
		#os.print_result_complete(result)
#		os.print_results_complete()
		os.print_results_resume()
	
	#
	# OUTPUT: File / Database / Console
	#

	# File output
	if args.o:
		print(f'Saving results in {args.o}')
		os.save_file(args.o)
		print("Saved")

	# Database Output and tracking
	if args.db:
		create_database(args.db)
		# LOAD DATABASE
		create_db_and_tables()
		console.log('Database loaded', style='italic bold green')

		postings = os.save_new_in_db()
		#print(postings)


	#
	# NOTIFY
	#
	if args.print_new:
		posting_repository = PostingRepository()
		unsent_postings = posting_repository.get_unsent_postings()	

		console.log(f'Found [u]{len(unsent_postings)}[/u] new urls', style='italic bold green')
		for posting in unsent_postings:
			print(posting.url)
			posting_repository.set_posting_as_sent(posting.sha)

	if args.print:
		os.print_results_complete()
		os.print_results_resume()

#	if args.proxy_anon:
#		print('Proxy not implemented yet')  

main()
#if __name__ == '__main__':
#    typer.run(main)