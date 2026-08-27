variable "okta_org_name" {
  description = "Your Okta org subdomain, e.g. 'dev-12345' for dev-12345.okta.com"
  type        = string
}

variable "okta_base_url" {
  description = "Okta base URL: 'okta.com' for most developer orgs, 'oktapreview.com' for some"
  type        = string
  default     = "okta.com"
}

variable "okta_api_token" {
  description = "API token from Security > API > Tokens"
  type        = string
  sensitive   = true
}
