#!/bin/bash
echo "Running sbom-puller against atlassian/jira-core:9.13-jdk11"
echo "----------------------------------------------------------"
python3 sbom-puller.py -i atlassian/jira-core:9.13-jdk11
echo "----------------------------------------------------------"
echo "Images not removed:"
echo ""
docker images | grep 9.13-jdk11