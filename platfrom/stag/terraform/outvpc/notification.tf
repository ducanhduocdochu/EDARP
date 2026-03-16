resource "aws_s3_bucket_notification" "bucket_notification" {

  bucket = aws_s3_bucket.data_bucket.id

  topic {
    topic_arn = aws_sns_topic.event_topic.arn
    events    = ["s3:ObjectCreated:*"]
  }

  depends_on = [aws_sns_topic.event_topic]
}