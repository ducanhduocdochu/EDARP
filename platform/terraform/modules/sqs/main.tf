# ─── Dead Letter Queue ───────────────────────────────────────────────────────
resource "aws_sqs_queue" "indexing_dlq" {
  name                      = "${var.name_prefix}-indexing-dlq"
  message_retention_seconds = 1209600 # 14 days
  kms_master_key_id         = var.kms_key_arn

  tags = { Name = "${var.name_prefix}-indexing-dlq" }
}

# ─── Main Indexing Queue ─────────────────────────────────────────────────────
resource "aws_sqs_queue" "indexing" {
  name                       = "${var.name_prefix}-indexing"
  visibility_timeout_seconds = var.visibility_timeout_seconds
  message_retention_seconds  = var.message_retention_seconds
  kms_master_key_id          = var.kms_key_arn

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.indexing_dlq.arn
    maxReceiveCount     = var.dlq_max_receive_count
  })

  tags = { Name = "${var.name_prefix}-indexing" }
}

# ─── Queue Policy — allow S3 to send messages ───────────────────────────────
resource "aws_sqs_queue_policy" "allow_s3" {
  queue_url = aws_sqs_queue.indexing.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "AllowS3SendMessage"
      Effect    = "Allow"
      Principal = { Service = "s3.amazonaws.com" }
      Action    = "sqs:SendMessage"
      Resource  = aws_sqs_queue.indexing.arn
      Condition = {
        ArnLike = {
          "aws:SourceArn" = "arn:aws:s3:::${var.name_prefix}-documents"
        }
      }
    }]
  })
}
