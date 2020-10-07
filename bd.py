from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
import socket
import urllib
import json
import hashlib
import sqlite3
import os.path
from datetime import datetime
from time import sleep

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)
inf = []

if os.path.isfile('./new_base.db') == False:
	with open('./new_base.db', 'w', encoding='utf-8') as f:
		pass

conn = sqlite3.connect('./new_base.db')
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS urls(
						urlid INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
						url TEXT UNIQUE);
			""")
conn.commit()
cur.execute("""CREATE TABLE IF NOT EXISTS info(
						infoid INTEGER PRIMARY KEY AUTOINCREMENT,
						urlid TEXT,
						ip TEXT,
						url TEXT,
						country TEXT,
						body_hash TEXT,
						data TEXT,
						time TEXT);
			""")
conn.commit()

cur.execute("""INSERT INTO urls(url) VALUES(?) ON CONFLICT DO NOTHING;""", ['https://www.google.com'])
conn.commit()

cur.execute("""INSERT INTO urls(url) VALUES(?) ON CONFLICT DO NOTHING;""", ['https://www.yandex.ru'])
conn.commit()

cur.execute("""INSERT INTO urls(url) VALUES(?) ON CONFLICT DO NOTHING;""", ['https://www.mail.ru'])
conn.commit()

cur.execute("""INSERT INTO urls(url) VALUES(?) ON CONFLICT DO NOTHING;""", ['https://www.vk.com'])
conn.commit()

cur.execute("""INSERT INTO urls(url) VALUES(?) ON CONFLICT DO NOTHING;""", ['https://www.mirea.ru'])
conn.commit()

print(cur.execute('SELECT * FROM urls').fetchall())

for addr in cur.execute('SELECT * FROM urls').fetchall():
	print(addr[1])
	sleep(10)
	try: driver.get(addr[1])
	except: continue

	for request in driver.requests:
		url = request.url.split('/')
		try: ip = socket.gethostbyname(url[2])
		except: continue
		print("IP: " + ip)

		try: response = urllib.request.urlopen("http://ipwhois.app/json/" + ip)
		except: continue

		try: ipgeolocation = json.load(response)
		except: continue

		print("Country: " + ipgeolocation["country"])
		if request.response:
			if request.response.body:
				print("Body_hash: ", hashlib.sha256(request.response.body).hexdigest())
				hash_obj = hashlib.sha256(request.response.body)
				hash_body = hash_obj.hexdigest()
			else:
				hash_body = "NO BODY"
		else:
			hash_body = "NO RESPONSE"
		cur.execute("""INSERT INTO info(urlid, ip, url, country, body_hash, data, time)
							VALUES(?, ?, ?, ?, ?, ?, ?);""",
							[addr[0], ip, request.url, ipgeolocation["country"],
							hash_body, datetime.now().date().strftime("%d/%m/%Y"),
							datetime.now().time().strftime("%H:%M:%S")])
		conn.commit()

		inf.append({"ip": ip,"url":request.url,"country":ipgeolocation["country"], "body_hash": hash_body})

		with open('inf.json', 'w+') as file:
			json.dump(inf, file)

	#print(inf)
conn.close()
driver.close()
