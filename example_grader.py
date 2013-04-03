import coursera_queue
from coursera_queue import SubmissionGrade, QueueProcessor

def gradeOneTwo(submissionData):
  score = 3.0
  data = submissionData.submissionData #Get the data that was submitted
  solution = submissionDecoded.solutionData #Get the solution you specified in coursera
  return SubmissionGrade(score, feedback="Great job! Your feedback will appear soon", hardDeadlineFeedback="Points: %f / 10" % score)

def gradeThree(submissionData):
  score = 0.0
  data = submissionData.submissionData
  solution = submissionDecoded.solutionData
  return SubmissionGrade(score, feedback="Interesting!", hardDeadlineFeedback="Points: %f / 10" % score)

if __name__ == "__main__":
  coursera_queue.setupLogging()
  #Your queue name goes here
  queueName = "YOUR_COURSE_QUEUE"
  #Your URLs would go here
  pollUrl='https://stanford.coursera.org/cs124-001/assignment/api/pending_submission'
  scoreUrl='https://stanford.coursera.org/cs124-001/assignment/api/score'
  #Your api key goes here
  apiKey='YOUR_API_KEY'

  QueueProcessor(queueName, pollUrl, scoreUrl, apiKey, {
    ("1", "2"): gradeOneTwo,
    "3": gradeThree
  }).pollForever()
