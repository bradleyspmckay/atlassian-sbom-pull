!#/bin/bash
echo "Running sbom-puller against atlassian/jira-core:9.13-jdk11"
python3 sbom-puller.py -i atlassian/jira-core:9.13-jdk11
echo "Check these docker images to ensure atlassian/jira-core:9.13-jdk11 was removed:"
docker images