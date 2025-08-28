# Variables matching external environment configuration
variable "tat_body_part" {
  type = string
}
variable "tat_tags_generator" {
  type = map(string)
}
variable "tat_environment" {
  type = string
}

# Introduce necessary argument variables for your module here, for example:

# variable "some_variable" {
#   description = "A description"
#   type        = string
#   default     = ""
# }
