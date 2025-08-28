# current user (POSIX)
u=$(id -u -n)

# go up 3 levels, get folder name (base folder of the module)
f="$(basename $(dirname $(dirname $(dirname $(dirname $PWD)))))"

# SHA1 of $f
h=$(echo -n $f | sha1sum | awk '{print $1}')

# First 7 characters
k=${h:0:7}

echo "Repo folder is: $f ($k)"

# When using 'latest' on a module, '.terraform' folder needs to be cleaned
rm -Rf .terraform

terraform init -reconfigure -backend-config="key=tat_ghs_sandbox_${u::7}-$k.tfstate" -backend-config="profile=tat_ghs_sandbox_${u::7}" -backend-config="bucket=s3usamea-tat-terraform-tfstate"
