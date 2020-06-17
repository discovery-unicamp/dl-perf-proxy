function fail()
{
    echo "FAIL: $@"
    exit 1
}

# Use -> get-log-by-stream-name.sh {Log stream name} > {Output file}

aws logs get-log-events --log-group-name /aws/sagemaker/TrainingJobs --log-stream-name $1 | python3 get_log_messages.py
