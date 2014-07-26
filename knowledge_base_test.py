
# -*- coding: utf-8 -*-

import datetime
from pyquery import PyQuery as pq
import os
import urllib
import re
from threading import Thread as Thd
import wikipedia as wk

import sys
reload(sys)
sys.setdefaultencoding('utf-8')#用于改变系统默认编码为utf8

class WikipediaTestThread(Thd):
	"""for wiki"""
	remove_symbles = re.compile('[^0-9A-Za-z ]')
	remove_brakets = re.compile('\(.+\)')
	space = re.compile(' +')

	total_answer = 0 #总共查询的 answer 数目
	total_clue = 0
	answer_cover = 0 #查询 answer 时结果出现 answer 的数目
	total_word = 0 #answer 出现时它前面的单词总数
	clue_in_answer_discrip = 0 #answer 查询结果中clue出现单词的百分比
	full_clue_matched = 0
	part_clue_matched = 0

	def __init__(self, clue, answer):
		super(WikipediaTestThread, self).__init__(name = answer)
		self._clue = clue
		self._answer = answer
		self._whole_keyword = self.__class__.remove_symbles.sub(' ', clue).strip()
		self._part_keywords = self.__class__.space.split(self._whole_keyword)
		self._keywords_number = len(self._part_keywords)
		self._answer_length = len(answer)

	def _answer_cover(self):
		try:
			sug = wk.suggest(self._answer)
			if type(sug) == str:
				sug = [sug]
		except Exception, e:
			return False
		if sug != None:#建议列表不为空
			for su in sug:
				if su != None and self.__class__.space.sub('', self.__class__.remove_brakets.sub('', su.encode('utf-8'))).upper() == self._answer:
					self.__class__.total_answer += 1
					self.__class__.answer_cover += 1
					return True
		sear = wk.search(self._answer)
		if type(sear) == str:
			sear = [sear]
		self.__class__.total_answer += 1
		if sear == None:#搜索结果为空
			return False
		else:#搜索结果不为空
			for s in sear:
				if s != None and s.encode('utf-8').find('(disambiguation)') != -1:
					continue
				if self.__class__.space.sub('', self.__class__.remove_brakets.sub('', s)).upper() == self._answer:
					self.__class__.answer_cover += 1
					
					try:
						page = wk.page(s)#获取 answer 文章
					except Exception, e:
						continue
					c = page.content
					count = 0
					for word in self._part_keywords:
						if c != None and c.find(word.encode('utf-8')) != -1:
							count += 1
					self.__class__.clue_in_answer_discrip += count / len(self._part_keywords)
					
					return True
		print self._answer + ' answer cover finished'


	def _full_clue_cover(self):
		try:
			sug = wk.suggest(self._whole_keyword)
			if type(sug) != list:
				sug = [sug]
			sear = wk.search(self._whole_keyword)
			if type(sear) != list:
				sear = [sear]
		except Exception, e:
			return False
		self.__class__.total_clue += 1
		l = []
		if sug == None and sear == None:
			return False
		elif sug != None and sear != None:
			try:
				l = sug + sear
			except Exception, e:
				print type(sug)
				print type(sear)
				raise e
		elif sug != None:
			l = sug
		else:
			l = sear

		for a in l:
			if a != None and self.__class__.space.sub('', self.__class__.remove_brakets.sub('', a.encode('utf-8'))).upper() == self._answer:
				self.__class__.full_clue_matched += 1
				return True
		print self._answer + ' full clue cover finished'


	def run(self):
		self._answer_cover()
		self._full_clue_cover()


class WordlistTestThread(Thd):
	"""for Wordlist"""
	remove_symbles = re.compile('[^0-9A-Za-z ]')
	get_number = re.compile('[0-9]+')
	#答案数据的覆盖度
	total_answer = 0 #总共查询的 answer 数目
	total_clue = 0
	answer_cover = 0 #查询 answer 时结果出现 answer 的数目
	total_word = 0 #answer 出现时它前面的单词总数
	clue_in_answer_discrip = 0 #answer 查询结果中clue出现单词的百分比
	#clue整体与clue的部分（keyword等snippets）的查询结果
	full_clue_matched = 0
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


	def _answer_cover(self):
		word_number = 0
		flag = True
		while flag:
			base_url = self._query_url + self._answer + '/min,' + str(self._answer_length) + '/max,' + str(self._answer_length) + '/' + str(word_number)
			try:
				page = pq(base_url)
			except Exception, e:
				return None
			if (len(page('div.content div.result h2 a')) < 40 or len(page('div.content p.pagination')) == 0 or pq(page('div.content p.pagination')[-1]).text() != '>>'):
				flag = False

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
		print self._answer + ' answer cover finished'

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
		print self._answer + ' full clue cover finished'

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
				return None
			if (len(page('div.content div.result h2 a')) < 40 or len(page('div.content p.pagination')) == 0 or pq(page('div.content p.pagination')[-1]).text() != '>>'):
				flag = False
			
			word_list = page('div.content div.result h2 a')
			for word in word_list:
				href = pq(word).attr('href')
				text = pq(word).text().upper()
				if text == self._answer:
					flag = False
					self.__class__.part_clue_matched += 1
					break
			word_number += 40
		print self._answer + ' part clue cover finished'


	def run(self):
		self._answer_cover()
		self.__class__.total_answer += 1
		self._full_clue_cover()
		self.__class__.total_clue += 1
		# _part_clue_cover(self)

def main():
	if len(sys.argv) == 1:
		root = './'
	else:
		root = sys.argv[1]
	print os.path.isdir(root)
	if not (os.path.isdir(root)):
		print 'wrong path format'
		return False
	sys_file = re.compile('(\.|\~).*')
	thread_list = []
	files = os.listdir(root)
	files.remove('knowledge_base_test.py')
	for f in files:
		print 'File:' + f
		fin = open(f, 'r')
		for line in fin:
			answer = line.split(' , ', 1)[0]
			clue = line.split(' , ', 1)[1]
	#wordlist test
			# thread_list.append(WordlistTestThread(clue, answer))
	#wiki test
			thread_list.append(WikipediaTestThread(clue, answer))
		fin.close()
	for th in thread_list:
		th.start()
	for th in thread_list:
		th.join(40)

#wordlist result
	# print '\n\n\n\n\n\n\n\ntotal_answer:'
	# print WordlistTestThread.total_answer
	# print 'answer_cover:'
	# print WordlistTestThread.answer_cover
	# print 'total_word:'
	# print WordlistTestThread.total_word
	# print 'total_clue:'
	# print WordlistTestThread.total_clue
	# print 'full_clue_matched:'
	# print WordlistTestThread.full_clue_matched


#wiki result
	print '\n\n\n\n\n\n\n\ntotal_answer:'
	print WikipediaTestThread.total_answer
	print 'answer_cover:'
	print WikipediaTestThread.answer_cover
	print 'clue_in_answer_discrip:'
	print WikipediaTestThread.clue_in_answer_discrip
	print 'total_clue:'
	print WikipediaTestThread.total_clue
	print 'full_clue_matched:'
	print WikipediaTestThread.full_clue_matched

	os.system("pause")

main()
