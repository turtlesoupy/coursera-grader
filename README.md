# Coursera External Grader
This is an grading library for coursera that I wrote as a TA for Stanford's
CS124: From Languages to Information Class. Essentially, this covers the 
intermediate nonsense required to communicate to coursera servers, leaving
the administrator to write the actual grading logic. Naturally, the audience 
for this may be limited :)

An example grader that reports a fixed score is available in `example_grader.py`.

## Minimal Example
Your grading logic is registered as callback functions that accept the submission
data object as a parameter. So, below, we are giving a score of 3 for part 1,2
and a score of 0 for part 3. The administrator would put their grading
logic in place.

The simplest grader I could think of:
    from coursera_queue import QueueProcessor, SubmissionGrade
    QueueProcessor("queue_name", 
       "http://coursera-course.coursera.org/assignment/api/pending_submisison", 
       "http://coursera-course.coursera.org/assignment/api/score",
       "api_key", {
       ("1", "2"): (lambda s: SubmissionGrade(3.0, feedback="Great!")),
       "3": (lambda s: SubmissionGrade(0.0, feedback="Too bad!"))
    }).pollForever()
