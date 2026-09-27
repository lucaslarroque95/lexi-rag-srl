locals {
  foundation = data.terraform_remote_state.foundation.outputs
}

resource "aws_lambda_function" "rag" {
  function_name = "${var.project}-rag-ingest-document"
  role          = local.foundation.rag_lambda_role_arn
  runtime       = "python3.13"
  architectures = ["x86_64"] # matches whatever machine ran build.sh — see build.sh's PYTHON_BIN comment
  handler       = "main.handler"
  timeout       = 900 # same ceiling the KEDA ScaledJob's activeDeadlineSeconds had — Lambda's own max
  memory_size   = 512 # epub parsing + embedding calls need more headroom than the HTTP services

  filename         = "${path.module}/../dist/function.zip"
  source_code_hash = filebase64sha256("${path.module}/../dist/function.zip")

  vpc_config {
    subnet_ids         = local.foundation.private_subnet_ids
    security_group_ids = [local.foundation.lambda_security_group_id]
  }

  environment {
    variables = {
      POSTGRES_SERVER     = local.foundation.rds_address
      POSTGRES_PORT       = tostring(local.foundation.rds_port)
      POSTGRES_USER       = local.foundation.db_master_username
      POSTGRES_PASSWORD   = local.foundation.rds_master_password
      POSTGRES_DB         = local.foundation.db_name
      OPENAI_API_KEY      = local.foundation.openai_api_key
      S3_BUCKET           = local.foundation.books_bucket
      EMBEDDING_MODEL     = var.embedding_model
      EMBEDDING_DIMENSION = tostring(var.embedding_dimension)
      CHUNK_SIZE          = tostring(var.chunk_size)
      CHUNK_OVERLAP       = tostring(var.chunk_overlap)
    }
  }
}

# batch_size=1 matches the "one book per run" semantics the KEDA ScaledJob
# had (queueLengthTarget: "1") — one message, one invocation.
# ReportBatchItemFailures makes AWS actually honor the batchItemFailures
# the handler returns, instead of treating any non-exception return as a
# full success.
resource "aws_lambda_event_source_mapping" "book_ingestion" {
  event_source_arn = local.foundation.book_ingestion_queue_arn
  function_name    = aws_lambda_function.rag.function_name
  batch_size       = 1

  function_response_types = ["ReportBatchItemFailures"]
}
