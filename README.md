# Coursera External Grader
This is an grading library for coursera that I wrote as a TA for Stanford's
CS124: From Languages to Information Class. The audience for this may be limited :)

An example grader that reports a fixed score is available in `example_grader.py`

## Minimal Example
The simplest grader I could think of:
    from coursera_queue import QueueProcessor, SubmissionGrade
    QueueProcessor("queue_name", 
       "http://coursera-course.coursera.org/assignment/api/pending_submisison", 
       "http://coursera-course.coursera.org/assignment/api/score",
       "api_key", {
       ("1", "2"): (lambda s: SubmissionGrade(3.0, feedback="Great!")),
       "3": (lambda s: SubmissionGrade(0.0, feedback="Too bad!"))
    }).pollForever()
