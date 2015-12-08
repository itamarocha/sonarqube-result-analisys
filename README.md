# Overview #

The built in Build Breaker Plugin for SonarQube has retired in 5.1 release. This is a workaround to achieve the same using SonarQube REST APIs.

# Usage #
python SonarBuildBreaker.py <sonar_server_url> <groupId> <artifactId> <branch> <mode>

Mode (1 or 2)

*   1 - Pre-Quality Analysis. This has to be execute before Sonar analysis to fetch the existing quality metrics from Sonar server
*   2 - Post-Quality Analysis. This has to be execute after Sonar analysis to fetch the latest quality metrics from Sonar server and compare with the previous metrics

e.g. python SonarBuildBreaker.py 'http://sonar.dev.intsys.atlassian.com:9000' 'com.atlassian.platform' 'ctk-plugin' master 2

By default, the build will fail if any increase in issues of type BLOCKER, CRITICAL or MAJOR. 
But you can control the behaviour by setting these environment variables **skipBlocker, skipCritical, skipMajor, skipMinor, skipInfo**

# Reference Bamboo Plan #
https://ecosystem-bamboo.internal.atlassian.com/browse/NRAM-SQPLUG

# Limitations
* This will fail the build if we run first time (on master or any branch build)because the pre-analyser return ZERO for all issue types.