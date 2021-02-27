function fail()
{
    echo "FAIL: $@"
    exit 1
}

# WARNING: Log stream name =!= Training job name, for the Log stream name go to the TrainingJob page and open CloudWatch registers
# Use -> get-log.sh {Log stream name} > {Output file}
# To salve the log automatically use get-log.sh match {log stream name}

if [[ $(echo "$1") == "match" ]]
then
	if [[ "$2" =~ fcn\-train\-p[0-9]+\-gpu[0-9]+\-b[0-9]+\-e[0-9]+\/ ]] ; then
		var=$(echo "$2" | grep -E -o ".+/")
		p=$(echo "$var" | grep -E -o "p\d+" | grep -o -E "\d+")
		gpu=$(echo "$var" | grep -E -o "gpu\d+" | grep -o -E "\d+")
		e=$(echo "$var" | grep -E -o "e\d+" | grep -o -E "\d+")
		b=$(echo "$var" | grep -E -o "b\d+" | grep -o -E "\d+")
		aws logs get-log-events --log-group-name /aws/sagemaker/TrainingJobs --log-stream-name $2 | python3 read-log-messages.py > logs/result-p$p-$gpu-$b-e$e.txt
	else
		aws logs get-log-events --log-group-name /aws/sagemaker/TrainingJobs --log-stream-name $2 | python3 read-log-messages.py 
	fi
else
	aws logs get-log-events --log-group-name /aws/sagemaker/TrainingJobs --log-stream-name $1 | python3 read-log-messages.py 
fi
