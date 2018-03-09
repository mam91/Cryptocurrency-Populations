import pyodbc
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
	
	con = pyodbc.connect(dbConfig[0]["sql_conn"])
	cursor = con.cursor()
	
	cursor.execute("SELECT t2.url, t1.name FROM [CoinTracker].[dbo].[Market] t1, CoinTracker.dbo.RedditSources t2 where t1.id = t2.coin_fk")
	rows = cursor.fetchall()

	if cursor.rowcount == 0:
		print("No Reddit sources found")
		return;
		
	redditApi = RedditClient()
	
	for row in rows:
		print(".", end="", flush=True)
		data_all = redditApi.get_subscriber_count(str(row[0]))
		params = (str(row[1]), str(data_all), str(row[0]))
		cursor.execute("{CALL RefreshMarketPopulations (?,?,?)}", params)
		cursor.commit()
		
	print("Done")

	
def main():
	PullReddit()

	
main()



