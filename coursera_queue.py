import sys
import time
import json
import socket
import urllib
import urllib2
import logging
import traceback
import collections

def setupLogging(fileName="grader.log"):
  """Sets up logging to go to a file and stdout. This is not necessary to call"""
  logger = logging.getLogger('')
  logger.setLevel(logging.DEBUG)

  formatter = logging.Formatter('%(asctime)s %(name)-12s: %(levelname)-8s %(message)s')

  console = logging.StreamHandler()
  console.setLevel(logging.DEBUG)
  console.setFormatter(formatter)

  fh = logging.FileHandler(fileName)
  fh.setLevel(logging.WARNING)
  fh.setFormatter(formatter)

  logger.addHandler(console)
  logger.addHandler(fh)

  logging.warning("Logging set up!")

class SubmissionGrade(object):
  """Contains the grade data and feedback."""

  @classmethod
  def errorGrade(cls, errorMessage="Error while grading!"):
    """Returns an grade suitable for an error"""
    return SubmissionGrade(0.0, feedback=errorMessage)

  def __init__(self, score, feedback="Default feedback.", softDeadlineFeedback=None, hardDeadlineFeedback=None):
    self.score = score
    self.feedback = feedback
    self.softDeadlineFeedback = softDeadlineFeedback or feedback
    self.hardDeadlineFeedback = hardDeadlineFeedback or softDeadlineFeedback or feedback

  def __str__(self):
    return "(SubmissionGrade score=%s, feedback=%s)" % (self.score, self.feedback)

class QueueSubmission(object):
  """Contains the data for a single submission."""
  def __init__(self, submissionDict):
    self.submissionData = submissionDict['submission']
    self.solutionData  = submissionDict['solutions']
    self.apiState = submissionDict['api_state']

    md = submissionDict['submission_metadata']
    self.partId  = md['assignment_part_sid'].replace("-dev", "")
    self.userId  = md['user_id']
    self.isDraft = "-dev" in md['assignment_part_sid'] 

  def __str__(self):
    return "(QueueSubmission userId=%s, partId=%s, draft=%s)" % (self.userId, self.partId, self.isDraft)

class QueueProcessor(object):
  """Polls coursera for solutions, posts the grades."""

  def __init__(self, queueName, pollUrl, scoreUrl, apiKey,
      graders={}, pollTime=10, pollTimeout=30):

    #For notational convinience, allow graders to be specified as tuples {('abc', 'bbq'): g} as well as {'2-1': g}
    self.graders = {}
    for (partNames, grader) in graders.iteritems():
      if isinstance(partNames, basestring):
        self.graders[partNames] = grader
      else:
        for partName in partNames:
          self.graders[partName] = grader

    self.pollUrl = pollUrl
    self.scoreUrl = scoreUrl
    self.queueName = queueName
    self.apiKey = apiKey
    self.pollTime = pollTime
    self.pollTimeout = pollTimeout
    self.requestHeaders = {
      'x-api-key': self.apiKey
    }

  def pollForever(self):
    """Polls the coursera queue in an infinite loop. Calls __handleSubmission with every submission."""

    socket.setdefaulttimeout(self.pollTimeout)
    logging.info("Starting queue processor loop for %s" % (sorted(self.graders.keys())))
    while(1):
      logging.info("Polling %s" % self.pollUrl)
      data = self.__poll()
      if not data: # check for connection error
        logging.error("Http error, sleeping")
        time.sleep(self.pollTime)
        continue

      data = json.load(data) 

      if 'submission' in data and data['submission']:
        logging.info("Found a submission!")
        self.__handleSubmission(QueueSubmission(data['submission']))
      else:
        logging.info("No submissions found...")
        time.sleep(self.pollTime)

  def __poll(self):
    """Polls the queue for a submission, returning the data."""
    values = {'queue' : self.queueName}
    data = urllib.urlencode(values)
    req = urllib2.Request(self.pollUrl, data, self.requestHeaders)
    try:
      response = urllib2.urlopen(req)
      return response
    except:
      logging.exception("Exception during poll!")
      return None

  def __handleSubmission(self, submission):
    """Handles a queue submission by calling out to the appropriate grader."""

    if submission.partId in self.graders:
      logging.info("Grading Submission %s" % submission)
      try:
        submissionGrade = self.graders[submission.partId](submission)
      except:
        logging.exception("Unhandled exception while grading!")
        submissionGrade = SubmissionGrade.errorGrade("Unhandled exception while grading...")
    else:
      logging.error("No grader for submission %s" % submission)
      submissionGrade = SubmissionGrade.errorGrade("No graders for part %s" % submission.partId)

    self.__submitGrade(submission, submissionGrade)

  def __submitGrade(self, submission, submissionGrade):
    """Submits a grade to coursera."""

    logging.info("Submitting %s to %s" % (submissionGrade, self.scoreUrl))
    values = {
      'api_state': submission.apiState, 'score': str(submissionGrade.score), 
      'feedback': submissionGrade.feedback, 
      'feedback-after-hard-deadline': submissionGrade.hardDeadlineFeedback,
      'feedback_after_soft_close_time': submissionGrade.softDeadlineFeedback
    }

    try:
      data = urllib.urlencode(values)
      req = urllib2.Request(self.scoreUrl, data, self.requestHeaders)
      response = urllib2.urlopen(req)
      return response.read()
    except:
      logging.exception("Unhandled exception while submitting grade!")
      return None
