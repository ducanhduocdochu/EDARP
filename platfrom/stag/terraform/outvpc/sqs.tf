resource "aws_sqs_queue" "queue1" {
  name = "queue-processor-1"
}

resource "aws_sqs_queue" "queue2" {
  name = "queue-processor-2"
}

resource "aws_sqs_queue" "queue3" {
  name = "queue-processor-3"
}

resource "aws_sns_topic_subscription" "sub1" {
  topic_arn = aws_sns_topic.event_topic.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.queue1.arn
}

resource "aws_sns_topic_subscription" "sub2" {
  topic_arn = aws_sns_topic.event_topic.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.queue2.arn
}

resource "aws_sns_topic_subscription" "sub3" {
  topic_arn = aws_sns_topic.event_topic.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.queue3.arn
}