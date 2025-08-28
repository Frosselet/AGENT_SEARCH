set -e
RESULT=$(git config --get remote.origin.url | awk -F/ '{ print $(NF-1) }')
echo '{"Result": "'${RESULT}'"}'
