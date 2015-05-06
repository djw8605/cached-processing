#!/bin/sh

job_dir=$1

tmp_file=`mktemp`

# First, get the jobid from the directory
output_filename=`ls $job_dir/output.* | head -1`
num_jobs=`ls $job_dir/output.*  |  wc -l` 
jobid=`expr match \"$output_filename\" '.*output.\([0-9]*\)\..*'`
echo "Jobid=$jobid"

for line in `condor_history -backwards -match $num_jobs $jobid  -format "%i" JobCurrentStartExecutingDate -format "-%i\n" JobStartDate`; do echo $line | bc >> $tmp_file;  done; 

echo "Num Jobs: $num_jobs"

awk '{s+=$1} END {print s}' $tmp_file

rm $tmp_file

