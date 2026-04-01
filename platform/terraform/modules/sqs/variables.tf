variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "kms_key_arn" {
  description = "KMS key ARN for server-side encryption"
  type        = string
}

variable "message_retention_seconds" {
  description = "SQS message retention period in seconds"
  type        = number
  default     = 345600 # 4 days
}

variable "visibility_timeout_seconds" {
  description = "Visibility timeout in seconds"
  type        = number
  default     = 300 # 5 minutes — enough for indexing pipeline
}

variable "dlq_max_receive_count" {
  description = "Max receives before moving to DLQ"
  type        = number
  default     = 3
}
