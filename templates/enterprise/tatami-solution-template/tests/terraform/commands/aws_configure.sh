# get current user id
u=$(id -u -n)

p=tat_ghs_sandbox_${u::7}

echo "Use the *direct deployment* credentials (https://iam-vault.tgrc.cargill.com/ui/vault/secrets/tat/show/AWS/GHS/sandbox/usremea-tat-sandbox-direct-deployment) to fill the requred arguments."

aws configure --profile $p

echo "Access configured, you can now add '--profile $p' to your AWS commands to operate accordingly."
