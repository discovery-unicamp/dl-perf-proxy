LOGS_DIR="./logs/"
# p3 instances
for batch in 256 512 1024 2048;
	do for g in 1; 
		do aws s3 sync s3://fcncloudml/resnet50-p3-gpu$g-b$batch-e0/ .; 
		a="$(tar -ztf output/model.tar.gz '*.txt')";
		tar -xf output/model.tar.gz $a;
	       	mv $a $LOGS_DIR/result-p3-$g-$batch-e0.txt;
		echo $LOGS_DIR/result-p3-$g-$batch-e0.txt;
	done; 
done;
# p2 instances 
for batch in 256 512 1024 2048;
	do for g in 1; 
		do aws s3 sync s3://fcncloudml/resnet50-p2-gpu$g-b$batch-e0/ .; 
		a="$(tar -ztf output/model.tar.gz '*.txt')";
		tar -xf output/model.tar.gz $a;
	       	mv $a $LOGS_DIR/result-p2-$g-$batch-e0.txt;
		echo $LOGS_DIR/result-p2-$g-$batch-e0.txt;
	done; 
done;

# g4 instances with 1 gpu
for instance in g4dnxlarge g4dn2xlarge g4dn4xlarge g4dn8xlarge g4dn16xlarge;
	do for batch in 256 512 1024 2048;
		do for g in 1; 
			do aws s3 sync s3://fcncloudml/resnet50-${instance}-gpu$g-b$batch-e0/ .; 
			a="$(tar -ztf output/model.tar.gz '*.txt')";
			tar -xf output/model.tar.gz $a;
			mv $a $LOGS_DIR/result-${instance}-$g-$batch-e0.txt;
			echo $LOGS_DIR/result-${instance}-$g-$batch-e0.txt;
		done; 
	done;
done;
aws s3 sync s3://fcncloudml/resnet50-g4dn4xlarge-gpu1-b2048-e0-real/ .; 
a="$(tar -ztf output/model.tar.gz '*.txt')";
tar -xf output/model.tar.gz $a;
mv $a $LOGS_DIR/result-g4dn4xlarge-1-2048-e0.txt;
echo $LOGS_DIR/result-g4dn4xlarge-1-2048-e0.txt;
