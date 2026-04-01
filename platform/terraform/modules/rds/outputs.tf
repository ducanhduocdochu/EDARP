output "auth_db_endpoint" {
  description = "Auth DB connection endpoint"
  value       = aws_db_instance.auth.endpoint
}

output "auth_db_address" {
  description = "Auth DB hostname"
  value       = aws_db_instance.auth.address
}

output "auth_db_port" {
  description = "Auth DB port"
  value       = aws_db_instance.auth.port
}

output "project_db_endpoint" {
  description = "Project DB connection endpoint"
  value       = aws_db_instance.project.endpoint
}

output "project_db_address" {
  description = "Project DB hostname"
  value       = aws_db_instance.project.address
}

output "project_db_port" {
  description = "Project DB port"
  value       = aws_db_instance.project.port
}

output "auth_db_name" {
  description = "Auth database name"
  value       = aws_db_instance.auth.db_name
}

output "project_db_name" {
  description = "Project database name"
  value       = aws_db_instance.project.db_name
}
