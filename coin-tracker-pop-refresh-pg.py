import psycopg2
import requests
import json
import time
import os

def roundStr(numberToRound):
	return "{:.4f}".format(numberToRound) 

class RedditClient(object):
	#def __init__(self):
	def get_subscriber_count(self, endpoint):
		try:
			subreddit = endpoint.replace("http://www.reddit.com/","")
			hdr = {'User-Agent': 'windows:' + subreddit + '.single.result:v1.0(by /u/mmiller3_ar)'}
			url = endpoint + 'about.json'
			req = requests.get(url, headers=hdr)
			json_data = json.loads(req.text)
			return json_data['data']['subscribers']
			
		except exception as e:
			print("Error : " + str(e))
			

def loadConfig(filename):
	config = open(filename)
	data = json.load(config)
	return data
	
	
def PullReddit():
	print("Pulling Reddit subscribers", end="", flush=True)

	dbConfig = loadConfig('C:\AppCredentials\CoinTrackerPython\database.config')
	
	con = psycopg2.connect(dbConfig[0]["postgresql_conn"])
	cursor = con.cursor()

	cursor.execute("select ss.uri, cc.name, cc.symbol, cc.id, ss.id  from crypto_currencies cc, social_sources ss where cc.id = ss.coin_fk and ss.name = 'reddit' order by cc.id asc")
	
	rows = cursor.fetchall()

	if cursor.rowcount == 0:
		print("No Reddit sources found")
		return;
		
	redditApi = RedditClient()
	
	for row in rows:
		print(".", end="", flush=True)
		data_all = redditApi.get_subscriber_count(str(row[0]))

		params = (row[3], row[4], data_all)
		cursor.callproc('refreshpopulation', params)
	cursor.close()
	con.commit()
	con.close()
	print("Done")

	
def main():
	PullReddit()

	
main()



