#!/usr/bin/python

#ok so you want to review 650 press releases

import urllib2
import BeautifulSoup
import re
from textblob.classifiers import NaiveBayesClassifier

base_url = 'http://www.virtualpressoffice.com/showJointPage.do?page=jp&showId=2990&newsStartIndex='
domain = 'http://www.virtualpressoffice.com'

#they live under the base_url, in pages of 50, incremented by newsStartIndex
#the following lists constitute the training data for the classifier

disruptionstrategy_keywords = [(i, 'Disruptive') for i in ['disruption', 'disruptive', 'transformation', 'transformational', 'global', 'agile', 'broadband', 'regulation', 'strategy', 'metrics', 'KPIs', 'innovation', 'future', 'competition', 'consolidation', 'cloud', 'spectrum', 'Ericsson', 'Huawei', 'Cisco', 'Nokia', 'Alcatel-Lucent']]

customerexperience_keywords = [(i, 'Customer_Experience') for i in ['commerce', 'marketing', 'advertising', 'couponing', 'payments', 'money', 'transactions', 'PayPal', 'analytics', 'retail', 'retailing', 'call centre', 'contact centre', 'NFC', 'BLE', 'Bluetooth Low Energy', 'local', 'hyperlocal', 'BSS', 'OSS', 'Apple', 'Amazon', 'media', 'campaign']]

telco2index_keywords = [(i, 'Telco2_Index') for i in ['collaboration', 'revenue', 'LTE', 'M2M', 'telcos', 'carriers', 'merger', 'roaming', 'stakeholders', 'AT&T', 'Verizon', 'Vodafone', 'SingTel', 'Bharti', 'Orange', 'Telefonica', 'NTT DoCoMo', 'Ooredoo', 'competition', 'benchmarking', 'growth', 'results', 'voice', 'traffic', 'data', 'digital']]

enterprisemob_keywords = [(i, 'Enter_Mob') for i in ['MDM', 'device management', 'enterprise', 'fleet', 'security', 'apps', 'VMWare', 'Airwatch', 'BlackBerry', 'Microsoft', 'SMB', 'SME', 'VPN', 'small cells', 'WiFi', 'WLAN', 'SAP', 'Oracle', 'Microsoft', 'SIP', 'VoIP', 'PBX', 'applications platform', 'BYOD', 'tablet', 'managed']]

marketingworkshops_keywords = [(i, 'Market_Workshops') for i in ['advertising', 'search', 'discovery', 'marketing', 'video', 'audio', 'display', 'proximity', 'local', 'register', 'mCommerce', 'm-commerce', 'engagement', 'tracking', 'loyalty', 'service', 'social media', 'augmented reality', 'AR', 'WebRTC', 'mall']] 

bigdata_keywords = [(i, 'Big_Data') for i in ['analytics', 'big data', 'Big Data', 'cloud', 'storage', 'virtualisation', 'virtualization', 'insights', 'Hadoop', 'Pig', 'machine learning', 'optimisation', 'personal', 'identity', 'ID', 'customer data', 'Internet of Things']]

shitbucket = [(i, 'shitbucket') for i in ['awards', 'records', 'Click here to view', 'GSMA', 'Press Kit']]

outputs = {'Disruptive': [], 'Customer_Experience': [], 'Telco2_Index': [], 'Enter_Mob': [], 'Market_Workshops': [], 'Big_Data': []}
# this dict of dicts will contain the results

train_set = disruptionstrategy_keywords + customerexperience_keywords + telco2index_keywords + enterprisemob_keywords + marketingworkshops_keywords + bigdata_keywords + shitbucket
#concat the training data

classifier = NaiveBayesClassifier(train_set)
#train the classifier
		
def classy(slug):
	c = classifier.prob_classify(slug)
	f = c.max()
	s = c.prob(f)
	return (f, s)
#helper that accepts the text to be classified, runs the classifier, and returns the decision and the probability

def add(uri, slug, score, flag):
	odict = dict(uri=uri, hed=slug, score=score)
	outputs[flag].append(odict)
#stores info in the dict stack

def parse(index):
	page = urllib2.urlopen(base_url + str(index))
	soup = BeautifulSoup.BeautifulSoup(page)
	s = soup.findAll('font', 'stdLarge')
	for group in s:	
			if group.a and group.a.string:
				uri = domain + group.a['href']
				slug = group.a.string
				flag, score = classy(slug.strip(' \r\n\t'))
				add(uri, slug, score, flag)

#make the URI for the relevant page, dig out links and slugs with Bs, call the classifier for each one, store results
		

def sort_and_rank(queue):
	queue.sort(key=lambda x:x['score'], reverse=True)
	q = queue[:20]
	return q
#sorts a bucket of results by probability and returns best 15, filtered for uniques

for i in range(0,650,50):
	parse(i)
	
#flow control - step through grabbing the uris and processing	
with open('mwc_miner_output.tsv', 'w') as f:
	for o in outputs.keys():
		print o, ' ', len(outputs[o])
		results = sort_and_rank(outputs[o])
		for item in results:
			print >> f, o, '\t', 'headline: ', str(item['hed']).lstrip(), '\t', ' score: ', item['score'], '\t', ' URI: ', item['uri'], '\t'
	f.close()
#take each list of results in turn, sort and get top 15, print category and results to a file
