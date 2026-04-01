variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "force_destroy" {
  description = "Allow destroying the bucket even if it contains objects"
  type        = bool
  default     = false
}

variable "kms_key_arn" {
  description = "KMS key ARN for server-side encryption"
  type        = string
}

variable "sqs_queue_arn" {
  description = "SQS queue ARN for S3 event notifications"
  type        = string
}
