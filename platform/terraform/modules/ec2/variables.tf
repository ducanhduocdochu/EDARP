variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "subnet_id" {
  description = "Private subnet ID to launch the instance in"
  type        = string
}

variable "security_group_id" {
  description = "Security group ID for Weaviate EC2"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type (needs enough RAM for vector operations)"
  type        = string
  default     = "r6i.xlarge"
}

variable "root_volume_size" {
  description = "Root EBS volume size in GB"
  type        = number
  default     = 50
}

variable "data_volume_size" {
  description = "Data EBS volume size in GB for Weaviate persistent storage"
  type        = number
  default     = 100
}

variable "data_volume_type" {
  description = "EBS volume type for data volume"
  type        = string
  default     = "gp3"
}

variable "data_volume_iops" {
  description = "Provisioned IOPS for gp3 data volume"
  type        = number
  default     = 3000
}

variable "data_volume_throughput" {
  description = "Provisioned throughput (MB/s) for gp3 data volume"
  type        = number
  default     = 125
}

variable "kms_key_arn" {
  description = "KMS key ARN for EBS encryption"
  type        = string
}

variable "key_name" {
  description = "SSH key pair name (optional, for debugging)"
  type        = string
  default     = ""
}

variable "weaviate_version" {
  description = "Weaviate Docker image version"
  type        = string
  default     = "1.28.4"
}

variable "weaviate_port" {
  description = "Weaviate HTTP API port"
  type        = number
  default     = 8080
}

variable "weaviate_grpc_port" {
  description = "Weaviate gRPC port"
  type        = number
  default     = 50051
}
