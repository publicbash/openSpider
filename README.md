**Install:**

python3 -m venv ./venv

source venv/bin/activate

pip3 install -r requirements.txt

**Use:**

python3 openSpider.py [-h] [--url URL] [--o O] [--list LIST] [--proxy PROXY]
                     [--print PRINT] [--db DB_NAME] [--print_new Y]


**Examples:**

**input**
--url www.anyweb.com
--list url_list.txt

**output**
--o output.txt

**database**
--db database_name
--print_new

**proxy**
--proxy_auth http://user:pass@ip:port 
--proxy_anon ip:port 

**console**
--print x  <- screen
--print_new x  <- only works with --db


**Examples:**

--url http://www.clarin.com
--list url_list.txt

--o output.txt

--print x  <- screen

python3 main.py --list url_list.txt  --o output.txt --db db_test --print_new y 





