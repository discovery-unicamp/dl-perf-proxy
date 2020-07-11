function fail()
{
    echo "FAIL: $@"
    exit 1
}

# Use -> get-log-by-stream-name.sh {Log stream name} > {Output file}

if [[ $(echo "$1") == "match" ]]
then
	if [[ "$2" =~ mnist\-[[:alnum:]]+\-gpu[0-9]+\-b[0-9]+\-e[0-9]+\/ ]] ; then
		var=$(echo "$2" | grep -E -o ".+/")
		p=$(echo "$var" | grep -o -E "mnist-[A-Za-z0-9]+")
		p=${p/mnist-/}
		gpu=$(echo "$var" | grep -E -o "gpu\d+" | grep -o -E "\d+")
		e=$(echo "$var" | grep -E -o "e\d+" | grep -o -E "\d+")
		b=$(echo "$var" | grep -E -o "b\d+" | grep -o -E "\d+")
		aws logs get-log-events --log-group-name /aws/sagemaker/TrainingJobs --log-stream-name $2 | python3 read-log-messages.py > logs/result-$p-$gpu-$b-e$e.txt
	else
		aws logs get-log-events --log-group-name /aws/sagemaker/TrainingJobs --log-stream-name $2 | python3 read-log-messages.py 
		echo ""
	fi
else
	aws logs get-log-events --log-group-name /aws/sagemaker/TrainingJobs --log-stream-name $1 | python3 read-log-messages.py 
	echo ""
fi
