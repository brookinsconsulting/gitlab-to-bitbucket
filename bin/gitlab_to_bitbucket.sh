#!/bin/bash

# Usage
# bin/gitlab_to_bitbucket.sh <parameters>

# Dependencies
# Bash
# Python

# Main Script Execution (Timed)
start_time=`date +%s`;
$HOME"/bin/gitlab-to-bitbucket/bin/gitlab_to_bitbucket.rb" $@;
end_time=`date +%s`

echo "";
# echo "Execution time was: "`expr $end_time - $start_time`" seconds"
runtime=$(python -c "print 'Execution time was: %u minutes and %02u seconds' % ((${end_time} - ${start_time})/60, (${end_time} - ${start_time})%60)")
echo $runtime;

exit;
