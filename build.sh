#!/usr/bin/env bash
# Builds this service's single deployable zip under dist/, for infra/lambda.tf
# to pick up. Just one function (SQS-triggered, no HTTP routes), so unlike
# card-srl there's no shared layer — everything (deps + the adapters/config/
# db/models/ports/repositories/use_cases packages + bootstrap.py + the
# handler) goes into one self-contained zip.
set -euo pipefail
cd "$(dirname "$0")"

DIST=dist
PYTHON_BIN="${PYTHON_BIN:-python3}"

rm -rf "$DIST"
mkdir -p "$DIST/build"

echo "installing dependencies"
"$PYTHON_BIN" -m pip install --quiet --no-cache-dir \
  -r requirements.txt -t "$DIST/build"

# Direct zip upload caps out around 50MB, so drop what the function never
# needs: boto3/botocore/s3transfer already ship with the Lambda Python
# runtime, and bin/ is just console-script entry points.
echo "pruning runtime-provided packages"
rm -rf "$DIST"/build/{boto3,botocore,s3transfer,bin}
rm -rf "$DIST"/build/{boto3,botocore,s3transfer}-*.dist-info

echo "copying shared packages"
cp -r ./{adapters,config.py,db,models,ports,repositories,use_cases} "$DIST/build/"
cp bootstrap.py "$DIST/build/"
cp ingest-document/main.py "$DIST/build/"
find "$DIST/build" -name '__pycache__' -type d -prune -exec rm -rf {} +

python3 ./zip_dir.py "$DIST/build" "$DIST/function.zip"

echo "built $DIST/function.zip"
