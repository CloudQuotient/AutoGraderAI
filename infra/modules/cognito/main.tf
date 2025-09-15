resource "aws_cognito_user_pool" "main" {
  name = var.user_pool_name
}

resource "aws_cognito_user_pool_client" "app" {
  name         = "app-client"
  user_pool_id = aws_cognito_user_pool.main.id
}
