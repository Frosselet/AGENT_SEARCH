# TATami context, please initialize appropriately
locals {
  context = {
    area      = ... # Fill this with a proper value
    scope     = ... # Fill this with a proper value
    specifier = ... # Fill this with a proper value

    region      = var.tat_body_part
    environment = var.tat_environment

    org       = "francoisrosselet"
    repo      = "tatami-sol-raw"
    tag_major = "0"

    arm_record = "N/A"
    einsight   = "N/A"
    base_tags = merge(var.tat_tags_generator, {
      # You MUST specify a proper 'owner' and 'domain' attribute, like in the following example
      # "tatami.attribute.owner" : "tatami.owners.teams.tat",
      # "tatami.attribute.domain" : "tatami.domains.tda.generic",

      "tatami.attribute.owner" : ...,  # Look for valid values here: https://git.cglcloud.com/TAT/tatami-schemas/blob/main/contracts/v01.json#L10
      "tatami.attribute.domain" : ..., # Look for valid values here: https://git.cglcloud.com/TAT/tatami-schemas/blob/main/contracts/v01.json#L34

      # You MAY need to specify a valid data contract address, in case uncomment the following line and make sure you specify a valid value
      # "tatami.attribute.data-contract" : "sm://tat-tda-data-contracts/data-contract-url-template/sample_open_meteo.json"

      # Additional tags can be added if required
    })
  }
}

# Your local variables
