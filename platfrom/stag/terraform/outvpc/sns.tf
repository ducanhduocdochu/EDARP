resource "aws_sns_topic" "event_topic" {
  name = "s3-event-topic"
}