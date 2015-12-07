import urllib, json, re, subprocess,sys
import ConfigParser

class Sonar:
	sonar_server = ""
	total_issues = 0
	total_blockers = 0
	total_critical = 0
	total_major = 0
	total_minor = 0
	total_info = 0

	def __init__(self, sonar_server):
		self.sonar_server = sonar_server

	def getTotalResponsePages(self, groupId, artifactId, branch):
		url = self.sonar_server+"/api/issues/search?componentRoots="+groupId+":"+artifactId+":"+branch
		data = json.loads(urllib.urlopen(url).read())
		self.total_issues = data['total']
		return data['paging']['pages']

	def findIssues(self, groupId, artifactId, branch):
		print "Finding issues from SonarQube"
		url = self.sonar_server+"/api/issues/search?componentRoots="+groupId+":"+artifactId+":"+branch
		self.totalPages = self.getTotalResponsePages(groupId, artifactId, branch)
		pageIndex=1
		while (pageIndex <= self.totalPages):
			url2 = url+"&pageIndex="+str(pageIndex)		
			data = json.loads(urllib.urlopen(url2).read())
			self.total_blockers += len(re.findall("BLOCKERS", str(data)))
			self.total_critical += len(re.findall("CRITICAL", str(data)))
			self.total_major += len(re.findall("MAJOR", str(data)))
			self.total_minor += len(re.findall("MINOR", str(data)))
			self.total_info += len(re.findall("INFO", str(data)))
			pageIndex+=1

	def printResults(self):
		print "\n"
		print "Total Issues   : ",self.total_issues
		print "Total Blcokers : ",self.total_blockers
		print "Total Critical : ",self.total_critical
		print "Total Majors   : ",self.total_major
		print "Total Minor    : ",self.total_minor
		print "Total Info     : ",self.total_info
		print "\n"

	def writeResults(self):
		print "Writing results to file"
		subprocess.call(["touch", SONAR_RESULTS])
		f = open(SONAR_RESULTS,'w')
		try:
			f.write('[Default]\n')
			f.write('total = '+str(self.total_issues)+'\n')
			f.write('blocker = '+str(self.total_blockers)+'\n')
			f.write('critical = '+str(self.total_critical)+'\n')
			f.write('major = '+str(self.total_major)+'\n')
			f.write('minor = '+str(self.total_minor)+'\n')
			f.write('info = '+str(self.total_info)+'\n')
		except IOError:
			print "Error while writing to file"
		finally:
			f.close()

	def readResults(self):
		print "Reading results from file"
		config = ConfigParser.RawConfigParser()
		config.read(SONAR_RESULTS)
		self.total_issues = int(config.get('Default', 'total'))
		self.total_blockers = int(config.get('Default', 'blocker'))
		self.total_critical = int(config.get('Default', 'critical'))
		self.total_major = int(config.get('Default', 'major'))
		self.total_minor = int(config.get('Default', 'minor'))
		self.total_info = int(config.get('Default', 'info'))


SONAR_RESULTS = "sonarResults.out"

if (len(sys.argv) != 6):
	print "Usage : python SonarBuildBreaker.py <sonar_server_url> <groupId> <artifactId> <branch> <mode>"
	print "Mode (1 or 2)"
	print "\t 1. Pre-Quality Analysis"
	print "\t 2. Post-Quality Analysis"
	exit(1)

print "Sonar URL   : ", sys.argv[1]
print "Group Id    : ", sys.argv[2]
print "Artifact id : ", sys.argv[3]
print "Branch      : ", sys.argv[4]
print "Mode        : ", sys.argv[5]
print "\n"

if (sys.argv[5] == '1'):
	print ("Runnig in PRE Analysis mode")
	pre = Sonar (sys.argv[1])
	pre.findIssues (sys.argv[2], sys.argv[3], sys.argv[4])
	pre.printResults()
	pre.writeResults()

elif (sys.argv[5] == '2'):
	print ("Runnig in POST Analysis mode")
	post = Sonar (sys.argv[1])
	post.findIssues (sys.argv[2], sys.argv[3], sys.argv[4])
	post.printResults()

	pre = Sonar (sys.argv[1])
	pre.readResults()
	pre.printResults()

	print "Running COMPARISON"
	msg = ''
	fail = False

	if (pre.total_issues < post.total_issues):
		msg = "New issues "+ str(post.total_issues - pre.total_issues)+"\n"

	if (pre.total_blockers < post.total_blockers):
		msg = msg + "New BLOCKER issues "+ str(post.total_blockers - pre.total_blockers)+"\n"
		fail = True

	if (pre.total_critical < post.total_critical):
		msg = msg + "New CRITICAL issues "+ str(post.total_critical - pre.total_critical)+"\n"
		fail = True

	if (pre.total_major < post.total_major):
		msg = msg + "New MAJOR issues "+ str(post.total_major - pre.total_major)+"\n"

	if (pre.total_minor < post.total_minor):
		msg = msg + "New MINOR issues "+ str(post.total_minor - pre.total_minor)+"\n"

	if (pre.total_info < post.total_info):
		msg = msg + "New INFO issues "+ str(post.total_info - pre.total_info)+"\n"

	if (fail):
		print "Analysis result : FAILED"
		print msg
		exit (1)
	else:
		print "Analysis result : PASSED"
		print msg
