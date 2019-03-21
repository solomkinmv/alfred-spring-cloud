#!/usr/bin/env bash

# exit when any command fails
set -e

python3 update-version.py
python3 workflow-build.py ..

cd ..
version=$(<version)
git add .
git commit -m "Update version to ${version}"

git tag -a v${version} -m "Version: v${version}"
git push origin v${version}