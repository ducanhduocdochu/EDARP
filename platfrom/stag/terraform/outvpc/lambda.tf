resource "aws_lambda_function" "processor1" {

  function_name = "processor1"

  filename      = "lambda.zip"
  handler       = "index.handler"
  runtime       = "nodejs18.x"

  role = aws_iam_role.lambda_role.arn
}

resource "aws_lambda_event_source_mapping" "sqs_trigger1" {

  event_source_arn = aws_sqs_queue.queue1.arn
  function_name    = aws_lambda_function.processor1.arn

  batch_size = 10
}