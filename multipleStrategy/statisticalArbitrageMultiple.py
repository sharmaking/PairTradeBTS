#!/usr/bin/python
# -*- coding: utf-8 -*-
#statisticalArbitrageMultiple.py
import baseMultiple
import numpy, copy, csv

class CStatisticalArbitrageMultiple(baseMultiple.CBaseMultiple):
	#------------------------------
	#继承重载函数
	#------------------------------
	#自定义初始化函数
	def customInit(self):
		self.name = "statisticalArbitrageMultiple"
		self.parameters = []
		self.loadPara()
	#行情数据触发函数
	def onRtnMarketData(self, data):
		#计算S
		self.countS(data)
		pass
	def dayEnd(self):
		pass
	#自动保存缓存触发函数
	def autosaveCache(self):
		self.saveCache(parameters = self.parameters)
		pass
	#----------------------
	#实现函数体
	#----------------------
	def loadPara(self):
		reader = csv.reader(open("filtPara.csv"))
		for line in reader:
			self.parameters.append({
				"stocks"	: [line[0][:6], line[0][7:13]],
				"Beta"		: float(line[1]),
				"Mean"		: float(line[2]),
				"STD"		: float(line[3]),
				"OPEN"		: float(line[5]),
				"CLOSE"		: float(line[6]),
				"ODD"		: float(line[7]),
				"staute"	: 0,
				"tradeType"	: [None, None],
				"price"		: [0,0],
				"S"			: (0,0)
				})
	def countS(self, data):
		for parameter in self.parameters:
			Pa = self.getStockPrice(parameter["stocks"][0])
			Pb = self.getStockPrice(parameter["stocks"][1])
			if Pa and Pb:
				St = numpy.log(Pa) - parameter["Beta"]*numpy.log(Pb)
				S = (St - parameter["Mean"])/parameter["STD"]
				parameter["price"] = [Pa, Pb]
				parameter["S"] = (data["dateTime"], S)
				#self.sendS(S, parameter["stocks"][0], data["dateTime"], Pa, Pb)
				self.countTrade(parameter, S)
	def getStockPrice(self, stockCode):
		if self.actuatorDict[stockCode].signalObjDict["baseSignal"].MDList:
			return copy.copy(self.actuatorDict[stockCode].signalObjDict["baseSignal"].MDList[-1]["close"])
		return None
	def countTrade(self, parameter, S):
		if parameter["staute"] == 0:	#还没开仓
			if S > parameter["OPEN"]:
				self.openTrade(parameter, True)			#正
			elif S < -parameter["OPEN"]:
				self.openTrade(parameter, False)		#反
		elif parameter["staute"] == 1:	#已经开仓
			if parameter["tradeType"][0] == "Sell":		#正
				if S < parameter["CLOSE"]:	#平
					self.closeTrade(parameter)
				if S > parameter["ODD"]:	#止损
					self.stopLossTrade(parameter)
			elif parameter["tradeType"][0] == "Buy":	#反
				if S > -parameter["CLOSE"]:	#平
					self.closeTrade(parameter)
				if S < -parameter["ODD"]:	#止损
					self.stopLossTrade(parameter)
		if parameter["staute"] != 2:
			if S > parameter["ODD"] or S < -parameter["ODD"]:
				self.stopLossTrade(parameter)
	def sendS(self, S, stockCode, dateTime, Pa, Pb):
		self.sendMessageToClient("0_%s_%s_%s_%f_%f"%(stockCode, str(S)[:6], dateTime, Pa, Pb))
	def openTrade(self, parameter, isTrue):
		parameter["staute"] = 1
		if isTrue:		#正
			parameter["tradeType"] = ["Sell", "Buy"]
		else:			#反
			parameter["tradeType"] = ["Buy", "Sell"]
		self.sendMessageToClient("%s-%s,%s,Open:,%s,%s,%s, %s,%s,%s"%(
			parameter["stocks"][0], parameter["stocks"][1], str(parameter["S"][0]),
			parameter["stocks"][0], parameter["tradeType"][0], parameter["price"][0],
			parameter["stocks"][1], parameter["tradeType"][1], parameter["price"][1]))
	def closeTrade(self, parameter):
		self.sendMessageToClient("%s-%s,%s,Close:,%s,%s,%s, %s,%s,%s"%(
			parameter["stocks"][0], parameter["stocks"][1], str(parameter["S"][0]),
			parameter["stocks"][0], parameter["tradeType"][1], parameter["price"][0],
			parameter["stocks"][1], parameter["tradeType"][0], parameter["price"][1]))
		parameter["staute"]		= 0
		parameter["tradeType"]	= [None, None]
	def stopLossTrade(self, parameter):
		self.sendMessageToClient("%s-%s,%s,StopLoss:,%s,%s,%s, %s,%s,%s"%(
			parameter["stocks"][0], parameter["stocks"][1], str(parameter["S"][0]),
			parameter["stocks"][0], parameter["tradeType"][1],parameter["price"][0],
			parameter["stocks"][1], parameter["tradeType"][0],parameter["price"][1]))
		parameter["staute"]		= 2
		parameter["tradeType"]	= [None, None]
	def exceptionTrade(self, parameter):
		self.sendMessageToClient("%s-%s,%s,StopLoss:,%s,%s,%s, %s,%s,%s"%(
			parameter["stocks"][0], parameter["stocks"][1], str(parameter["S"][0]),
			parameter["stocks"][0], parameter["tradeType"][1],parameter["price"][0],
			parameter["stocks"][1], parameter["tradeType"][0],parameter["price"][1]))
		parameter["staute"]		= 2
		parameter["tradeType"]	= [None, None]

	def sendMessageToClient(self, string):
		print self.MDList[-1]["dateTime"], string
		logFile = open("tradePointsFinal.csv", "a")
		content = string + "\n"
		logFile.write(content)
		logFile.close()
		pass
