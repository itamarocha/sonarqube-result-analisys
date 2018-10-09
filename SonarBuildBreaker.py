import requests, json, re, subprocess, sys, os

class Sonar:
	sonar_server = ""
	key = ""
	total_issues = 0
	total_blockers = 0
	total_critical = 0
	total_major = 0
	total_minor = 0
	total_info = 0

	def __init__(self, sonar_server, key):
		self.sonar_server = sonar_server
		self.key = key

	def getTotalResponsePages(self, key):
		url = self.sonar_server+"/api/issues/search?id="+key
		r = requests.get(url)
		
		data = json.loads(r.text)
		self.total_issues = data['total']
		return data['paging']['total']

	def findIssues(self, key):
		print ("Finding issues from SonarQube") 
		url = self.sonar_server+"/api/issues/search?id="+key
		
		self.totalPages = self.getTotalResponsePages(key)
		pageIndex=1
		while (pageIndex <= self.totalPages):
			url2 = url+"&pageIndex="+str(pageIndex)	
			r = requests.get(url2)	
			data = json.loads(r.text)
			self.total_blockers += len(re.findall("BLOCKERS", str(data)))
			self.total_critical += len(re.findall("CRITICAL", str(data)))
			self.total_major += len(re.findall("MAJOR", str(data)))
			self.total_minor += len(re.findall("MINOR", str(data)))
			self.total_info += len(re.findall("INFO", str(data)))
			pageIndex+=1

	def printResults(self):
		print ("\n")
		print ("Total Issues   : ",self.total_issues)
		print ("Total Blcokers : ",self.total_blockers)
		print ("Total Critical : ",self.total_critical)
		print ("Total Majors   : ",self.total_major)
		print ("Total Minor    : ",self.total_minor)
		print ("Total Info     : ",self.total_info)
		print ("\n")


print ("Sonar URL   : ", sys.argv[1])
print ("Key   : ", sys.argv[2])
print ("\n")
print ("Analysis")

post = Sonar(sys.argv[1], sys.argv[2])
post.findIssues(sys.argv[2])
post.printResults()

url = sys.argv[1]+"/api/qualitygates/project_status?projectKey="+sys.argv[2]
r = requests.get(url)	
parsed_json = json.loads(r.text)
gate = parsed_json['projectStatus']['status']


if (gate == 'ERROR'):
	print ("Analysis result : FAILED")
	print ("Refer report :" +sys.argv[1]+"/api/issues/search?id="+sys.argv[2])
	exit (1)
else:
	print ("Analysis result : PASSED")
	print ("Refer report : "+sys.argv[1]+"/api/issues/search?id="+sys.argv[2])
