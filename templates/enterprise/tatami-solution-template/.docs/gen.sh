docker build --platform linux/amd64 -t local/terraform-docs-lf -f .docs/dockerfile .
docker run --platform linux/amd64 --rm -v=/$(pwd):/gen -u $(id -u) -it local/terraform-docs-lf markdown gen --config gen/.docs/terraform-docs.yml > README.md
