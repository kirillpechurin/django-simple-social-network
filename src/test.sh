#!/bin/bash

set -e

echo "----------Start tests script----------"

echo "\nInstall requirements..."
pip install -r requirements.tests.txt

echo "\nRun tests..."

for opts in $(echo $TEST_OPTS | tr ",", "\n")
do
  echo "\nCoverage Run with opts: \`$opts\`"
  coverage run "$opts"
done

echo "\nCoverage Combine data files"
coverage combine --keep test_coverage/data_files

echo "\nCoverage Report in xml"
coverage xml

echo "\nCoverage Report in text"
coverage report

echo "----------End of tests script----------"
