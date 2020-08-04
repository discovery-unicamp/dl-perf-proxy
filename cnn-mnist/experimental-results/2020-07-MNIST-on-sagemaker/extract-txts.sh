LOGS_DIR="./logs/"
# p2 instances
for batch in 256 512;
	do for g in 1 8 16; 
		do aws s3 sync s3://fcncloudml/mnist-p2-gpu$g-b$batch-e2/ .; 
		a="$(tar -ztf output/model.tar.gz '*.txt')";
		tar -xf output/model.tar.gz $a;
	       	mv $a $LOGS_DIR/result-p2-$g-$batch-e2.txt;
		echo $LOGS_DIR/result-p2-$g-$batch-e2.txt;
	done; 
done;
# p3 instances
for batch in 256 512;
	do for g in 1 4 8; 
		do aws s3 sync s3://fcncloudml/mnist-p3-gpu$g-b$batch-e2/ .; 
		a="$(tar -ztf output/model.tar.gz '*.txt')";
		tar -xf output/model.tar.gz $a;
	       	mv $a $LOGS_DIR/result-p3-$g-$batch-e2.txt;
	       	echo $LOGS_DIR/result-p3-$g-$batch-e2.txt;
	done; 
done;
# g4.xlarge instances
for batch in 256 512 1024 2048;
	do aws s3 sync s3://fcncloudml/mnist-g4dnxlarge-gpu1-b$batch-e2/ .; 
	a="$(tar -ztf output/model.tar.gz '*.txt')";
	tar -xf output/model.tar.gz $a;
	mv $a $LOGS_DIR/result-g4dn-1-$batch-e2.txt;
	echo $LOGS_DIR/result-g4dn-1-$batch-e2.txt;
done;
# g4dn.Nxlarge instances with 1 GPU 
for batch in 256 512 1024 2048;
	do for N in 2 4 8 16;
	do aws s3 sync s3://fcncloudml/mnist-g4dn${N}xlarge-gpu1-b$batch-e2/ .; 
		a="$(tar -ztf output/model.tar.gz '*.txt')";
		tar -xf output/model.tar.gz $a;
		mv $a $LOGS_DIR/result-g4dn${N}xlarge-1-$batch-e2.txt;
		echo $LOGS_DIR/result-g4dn${N}xlarge-1-$batch-e2.txt;
	done;
done;
# g4dn.12xlarge instances
for batch in 256 512 1024 2048;
	do aws s3 sync s3://fcncloudml/mnist-g4dn12xlarge-gpu4-b$batch-e2/ .; 
	a="$(tar -ztf output/model.tar.gz '*.txt')";
	tar -xf output/model.tar.gz $a;
	mv $a $LOGS_DIR/result-g4dn12xlarge-4-$batch-e2.txt;
	echo $LOGS_DIR/result-g4dn12xlarge-4-$batch-e2.txt;
done;
# g4dn.xlarge - 2048 - fix
aws s3 sync s3://fcncloudml/mnist-g4dnxlarge-gpu1-b2048-e2-fix/ .; 
a="$(tar -ztf output/model.tar.gz '*.txt')";
tar -xf output/model.tar.gz $a;
mv $a $LOGS_DIR/result-g4dn-1-2048-e1.txt;
echo $LOGS_DIR/result-g4dn-1-2048-e1.txt;
# g4dn.12xlarge - 256 - fix
aws s3 sync s3://fcncloudml/mnist-g4dn12xlarge-gpu4-b256-e2-fix/ .;
a="$(tar -ztf output/model.tar.gz '*.txt')";
tar -xf output/model.tar.gz $a;
mv $a $LOGS_DIR/result-g4dn12xlarge-4-256-e1.txt;
echo $LOGS_DIR/result-g4dn12xlarge-4-256-e1.txt;

## END

rm -r output/
