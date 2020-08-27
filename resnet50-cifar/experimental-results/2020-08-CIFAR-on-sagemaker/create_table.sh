for batch in 256 512 1024 2048; 
	do (echo "2nd iteration, Avg(2-6), Avg(2-11), Total Time, Step time (without first step)";
		for i in execution-times/*/$batch/e0.summary; 
		do 
		name=$(echo ${i//\//-} | grep -E -o "[[:alnum:]]+-\d+"); 
		printf "$name,"
		cat $i |  grep -E -o "Estimated time: \d+[.]\d+" | grep -E -o "\d+[.]\d+" | while read -r line; 
			do printf "$line,";
		done;
		ntmi=$(cat $i | grep -E "delta" | grep -E -o "\d+[.]\d+"); 
		tmi=$(cat $i | grep -E "without first step" | grep -E -o "\d+[.]\d+") ;
		printf "$ntmi,$tmi"; 
		echo "";
	done) > table_${batch}_e0.csv; 
done;
