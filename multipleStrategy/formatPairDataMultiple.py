#!/usr/bin/python
# -*- coding: utf-8 -*-
#formatPairDataMultiple.py
import baseMultiple
import os, csv, copy, datetime

class CFormatPairDataMultiple(baseMultiple.CBaseMultiple):
	#------------------------------
	#继承重载函数
	#------------------------------
	#自定义初始化函数
	def customInit(self):
		self.name = "formatPairDataMultiple"
		self.rzrq = []
		self.loadRzrq()
		self.outputFilePath = "F:\\backTestData\\"
		self.fistData = False
		self.preDateTime = 0
		self.timeInterval = datetime.timedelta(seconds = 1)
		self.allFormartedDatas = []

	#行情数据触发函数
	def onRtnMarketData(self, data):
		if not self.fistData:
			self.fistData = True
			self.preDateTime = copy.copy(data["dateTime"])
		self.creatBarData(data)
	def dayEnd(self):
		if self.preDateTime:
			print self.preDateTime.date()
	#自动保存缓存触发函数
	def autosaveCache(self):
		pass
		#self.saveCache(parameters = self.parameters)
	#----------------------
	#实现函数体
	#----------------------
	def loadRzrq(self):
		reader = csv.reader(open("rzrq.csv")) 
		for line in reader:
			if line[0]:
				self.rzrq.append(line[0])
	def creatBarData(self, data):
		while (data["dateTime"].second != self.preDateTime.second or\
				(data["dateTime"].second == self.preDateTime.second and\
				data["dateTime"].minute != self.preDateTime.minute)) and\
				data["dateTime"].day == self.preDateTime.day:
			self.createFormatData()
			self.preDateTime = self.preDateTime + self.timeInterval
	def createFormatData(self):
		formatDataTime = self.preDateTime.replace(microsecond = 0)
		formatData = [formatDataTime]
		for stock in self.rzrq:
			formatData.append(self.getStockPrice(stock))
		#保存数据
		if self.allFormartedDatas and self.allFormartedDatas[-1][0] == formatDataTime:
			self.allFormartedDatas[-1] = formatData
		else:
			self.allFormartedDatas.append(formatData)
			if len(self.allFormartedDatas) > 2:
				self.saveFormatDatas(self.allFormartedDatas[-2])
			if len(self.allFormartedDatas) > 100:
				del self.allFormartedDatas[0]
	def getStockPrice(self, stockCode):
		if self.actuatorDict[stockCode].signalObjDict["baseSignal"].MDList:
			return copy.copy(self.actuatorDict[stockCode].signalObjDict["baseSignal"].MDList[-1]["close"])
		return None
	def saveFormatDatas(self, formatData):
		if self.fistData:
			outputFilePath = self.outputFilePath + str(self.preDateTime.date()) + ".csv"
			if not os.path.exists(outputFilePath):
				outputFile = open(outputFilePath, "a")
				content = "Time,"
				for stock in self.rzrq:
					content = content + stock + "," 
				content = content[:-2] + "\n"
				outputFile.write(content)
				outputFile.close()
			outputFile = open(outputFilePath, "a")
			content = ""
			for data in formatData:
				content = content + str(data) + ","
			content = content[:-2] + "\n"
			outputFile.write(content)
			outputFile.close()