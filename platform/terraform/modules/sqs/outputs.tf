output "queue_url" {
  description = "SQS indexing queue URL"
  value       = aws_sqs_queue.indexing.url
}

output "queue_arn" {
  description = "SQS indexing queue ARN"
  value       = aws_sqs_queue.indexing.arn
}

output "queue_name" {
  description = "SQS indexing queue name"
  value       = aws_sqs_queue.indexing.name
}

output "dlq_url" {
  description = "Dead letter queue URL"
  value       = aws_sqs_queue.indexing_dlq.url
}

output "dlq_arn" {
  description = "Dead letter queue ARN"
  value       = aws_sqs_queue.indexing_dlq.arn
}
