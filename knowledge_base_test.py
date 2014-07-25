
# -*- coding: utf-8 -*-

#import urllib2 as u2
from pyquery import PyQuery as pq
import os
import urllib
import re
from threading import Thread as Thd
import sys
reload(sys)
sys.setdefaultencoding('utf-8')#用于改变系统默认编码为utf8

class WikipediaTestThread(Thd):
	"""for wiki"""
	def __init__(self, answer, clue):
		super(WikipediaTestThread, self).__init__()
		self.answer = answer
		self.clue = clue
		


class WordlistTestThread(Thd):
	"""docstring for WordlistTestThread"""
	remove_symbles = re.compile('[^0-9A-Za-z ]')
	get_number = re.compile('[0-9]+')
	#答案数据的覆盖度
	total_answer = 0 #总共查询的 answer 数目
	total_clue = 0
	answer_cover = 0 #查询 answer 时结果出现 answer 的数目
	total_word = 0 #answer 出现时它前面的单词总数
	clue_in_answer_discrip = 0 #answer 查询结果中clue出现单词的百分比
	#clue整体与clue的部分（keyword等snippets）的查询结果
	full_clue_matched = 0 #
	part_clue_matched = 0
	#查询结果中答案的存在与否
	def __init__(self, clue, answer):
		super(WordlistTestThread, self).__init__(name = answer)
		self._clue = clue
		self._whole_keyword = self.__class__.remove_symbles.sub(' ', clue).strip()
		self._part_keywords = []#NLP 处理后得到的名词
		self._answer = answer
		self._query_url = 'http://en.wordlist.eu/search/phrase,'
		self._words_url = 'http://en.wordlist.eu/words/letter,'
		self._answer_length = len(self._answer)
		# self.__class__.total_answer += 1


	def _answer_cover(self):
		word_number = 0
		flag = True
		while flag:
			base_url = self._query_url + self._answer + '/min,' + str(self._answer_length) + '/max,' + str(self._answer_length) + '/' + str(word_number)
			try:
				page = pq(base_url)
			except Exception, e:
				# print self._answer + ' answer cover error:' + base_url
				return None
			if (len(page('div.content div.result h2 a')) < 40 or len(page('div.content p.pagination')) == 0 or pq(page('div.content p.pagination')[-1]).text() != '>>'):
				flag = False
				# break

			word_list = page('div.content div.result h2 a')
			for word in word_list:
				href = pq(word).attr('href')
				text = pq(word).text().upper()
				if text == self._answer:
					#answer 存在
					self.__class__.answer_cover += 1
					flag = False
					# answer_rank = word_number + word_list.index(word)
					# self.__class__.total_word += answer_rank
					#clue 相关
					# word_page = pq(href)
					# dis = word_page('dl#definitions').text()

					# count = 0
					# for key in self._part_keywords:
					# 	if key in dis:
					# 		count += 1
					# self.__class__.clue_in_answer_discrip += count #/ len(self._part_keywords)
					break
			word_number += 40
		print 'total_answer:'
		print WordlistTestThread.total_answer
		print 'answer_cover:'
		print WordlistTestThread.answer_cover
		print 'total_word:'
		print WordlistTestThread.total_word
		# print 'clue_in_answer_discrip:'
		# print WordlistTestThread.clue_in_answer_discrip
		print 'total_clue:'
		print WordlistTestThread.total_clue
		print 'full_clue_matched:'
		print WordlistTestThread.full_clue_matched
		# first_letter = self._answer[0]

		# try:
		# except Exception, e:
		# 	return None
		# for i in rang (0, maxpage + 1):
		# 	Thd(target = _answer_cover_helper, args = (base_url, i), name = self._answer + str(i)).start()

	def _full_clue_cover(self):
		base_url = self._query_url + urllib.quote(self._whole_keyword) + '/min,' + str(self._answer_length) + '/max,' + str(self._answer_length) + '/'
		flag = True
		word_number = 0
		while flag:
			url = base_url + str(word_number)
			try:
				page = pq(url)
			except Exception, e:
				# print self._answer + ' full clue cover error:' + url
				return None
			if (len(page('div.content div.result h2 a')) < 40 or len(page('div.content p.pagination')) == 0 or pq(page('div.content p.pagination')[-1]).text() != '>>'):
				falg = False
				# break
			
			word_list = page('div.content div.result h2 a')
			for word in word_list:
				href = pq(word).attr('href')
				text = pq(word).text().upper()
				if text == self._answer:
					flag = False
					answer_rank = word_number + word_list.index(word)
					self.__class__.total_word += answer_rank
					self.__class__.full_clue_matched += 1
					break
			word_number += 40
		print 'total_answer:'
		print WordlistTestThread.total_answer
		print 'answer_cover:'
		print WordlistTestThread.answer_cover
		print 'total_word:'
		print WordlistTestThread.total_word
		# print 'clue_in_answer_discrip:'
		# print WordlistTestThread.clue_in_answer_discrip
		print 'total_clue:'
		print WordlistTestThread.total_clue
		print 'full_clue_matched:'
		print WordlistTestThread.full_clue_matched

	def _part_clue_cover(self):
		part_keyword = ''
		for key in self._part_keywords:
			part_keyword += ' ' + key
		answer_length = len(self._answer)
		base_url = self._query_url + urllib.quote(part_keyword) + '/min,' + str(answer_length) + '/max,' + str(answer_length) + '/'
		flag = True
		word_number = 0
		while flag:
			url = base_url + str(word_number)
			try:
				page = pq(url)
			except Exception, e:
				# print self._answer + ' error:' + url
				return None
			if (len(page('div.content div.result h2 a')) < 40 or len(page('div.content p.pagination')) == 0 or pq(page('div.content p.pagination')[-1]).text() != '>>'):
				flag = False
				# break
			
			word_list = page('div.content div.result h2 a')
			for word in word_list:
				href = pq(word).attr('href')
				text = pq(word).text().upper()
				if text == self._answer:
					flag = False
					self.__class__.part_clue_matched += 1
					break
			word_number += 40
		print 'total_answer:'
		print WordlistTestThread.total_answer
		print 'answer_cover:'
		print WordlistTestThread.answer_cover
		print 'total_word:'
		print WordlistTestThread.total_word
		# print 'clue_in_answer_discrip:'
		# print WordlistTestThread.clue_in_answer_discrip
		print 'total_clue:'
		print WordlistTestThread.total_clue
		print 'full_clue_matched:'
		print WordlistTestThread.full_clue_matched


	def run(self):
		self._answer_cover()
		self.__class__.total_answer += 1
		# print self._answer + ' answer cover finished'
		self._full_clue_cover()
		self.__class__.total_clue += 1
		# print self._answer + ' full clue cover finished'
		# _part_clue_cover(self)

def main():
	thread_list = []
	files = os.listdir('./')
	#os.chdir('./')
	files.remove('knowledge_base_test.py')
	for f in files:
		print 'File:' + f
		fin = open(f, 'r')
		for line in fin:
			answer = line.split(' , ', 1)[0]
			clue = line.split(' , ', 1)[1]
			print answer + ' , ' + clue.replace('\n', '')
			thread_list.append(WordlistTestThread(clue, answer))
	for th in thread_list:
		th.start()
	for th in thread_list:
		th.join(40)
		# print 'joined'
	print '\n\n\n\n\n\n\n\ntotal_answer:'
	print WordlistTestThread.total_answer
	print 'answer_cover:'
	print WordlistTestThread.answer_cover
	print 'total_word:'
	print WordlistTestThread.total_word
	# print 'clue_in_answer_discrip:'
	# print WordlistTestThread.clue_in_answer_discrip
	print 'total_clue:'
	print WordlistTestThread.total_clue
	print 'full_clue_matched:'
	print WordlistTestThread.full_clue_matched

# 	total_answer = 0 #总共查询的 answer 数目
# 	answer_cover = 0 #查询 answer 时结果出现 answer 的数目
# 	total_word = 0 #answer 出现时它前面的单词总数
# 	clue_in_answer_discrip = 0 #answer 查询结果中clue出现单词的百分比
# #clue整体与clue的部分（keyword等snippets）的查询结果
# 	full_clue_matched = 0 #
# 	part_clue_matched = 0



main()

#下面的是旧代码，不用管了
#wordlist的查询url：
	#interface = 'http://en.wordlist.eu/search/phrase,word/min,4/max,30/metaphone,RCT/soundex,R630/chars,aeiou/without_chars,yt'
# def py_get_page(URL = ''):
# 	if URL == '':
# 		return None
# 	else:
# 		try:
# 			res = pq(URL)
# 		except Exception, e:
# 			return None
# 		return res

# def py_post_page(URL = '', para_dict = {}):
# 	if URL == '' | len(para_dict) == 0:
# 		return None
# 	else:
# 		try:
# 			res = pq(URL, para_dict, method='post', verify=True)
# 		except Exception, e:
# 			return None
# 		return res

# def main():
# 	result = {'match_count':{'wordlist':0, 'wikipedia':0, 'dbpedia':0, 'freebase':0, 'wordnet':0, 'yago':0}, 'total_count':{'wordlist':0, 'wikipedia':0, 'dbpedia':0, 'freebase':0, 'wordnet':0, 'yago':0}}
# 	files = os.listdir('./')
# 	files.remove('knowledge_base_test.py')
# 	for f in files:
# 		print 'File:' + f
# 		fin = open(f, 'r')
# 		for line in fin:
# 			answer = line.split(' , ', 1)[0]
# 			clue = remove_symble.sub('', line.split(' , ', 1)[1])
# 			uclue = urllib.quote(clue)
# 		#wordlist
# 			wordlist_url = 'http://en.wordlist.eu/search/phrase,' + uclue
# 			page_offset = 40
# 			page_number = 0
# 			flag = True
# 			while flag:
# 				page = py_get_page(wordlist_url + '/' + str(page_offset * page_number))
# 				if page:
# 					result['total_count']['wordlist'] += 1
# 					for word in page('div.result h2'):
# 						# print pq(word).text().upper() + ' , ' + answer
# 						if pq(word).text().upper() == answer:
# 							result['match_count']['wordlist'] += 1
# 							flag = False
# 							break
# 					page_number += 1
# 					if page('.pagination').text().rfind('next') == -1:
# 						flag = False
# 				else:
# 					break
									
# 		#wikipedia
# 			wikipedia_url = 'http://en.wikipedia.org/w/index.php?title=Special:Search&limit=100000000&offset=0&profile=default&search=' + uclue
# 			flag = True
# 			while flag:
# 				page = py_get_page(wordlist_url + '/' + str(page_offset * page_number))
# 				if page:
# 					result['total_count']['wordlist'] += 1
# 					for word in page('div.result h2'):
# 						# print pq(word).text().upper() + ' , ' + answer
# 						if pq(word).text().upper() == answer:
# 							result['match_count']['wordlist'] += 1
# 							flag = False
# 							break
# 					page_number += 1
# 					if page('.pagination').text().rfind('next') == -1:
# 						flag = False
# 				else:
# 					break
			
# 		#Dbpedia  **post  ?q = **
# 			dbpedia_url = 'http://dbpedia.org/fct/facet.vsp'
# 			para = {'p':clue}
# 		#freebase
# 			freebase_url = 'https://www.freebase.com/search?query=' + uclue
# 		#wordnet
# 			wordnet_url = 'http://wordnetweb.princeton.edu/perl/webwn?s=' + uclue
# 		#YAGO
# 			yago_url = 'https://gate.d5.mpi-inf.mpg.de/webyagospotlx/SvgBrowser?codeIn=eng&entityIn=' + uclue
# 		fin.close()
# 	print result
