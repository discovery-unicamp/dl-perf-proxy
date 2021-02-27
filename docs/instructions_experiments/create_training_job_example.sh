aws sagemaker create-training-job \
	--training-job-name resnet50-p3-gpu4-b512-e2 \
	--hyper-parameters batch-size=512,epochs=5 \
	--role-arn arn:aws:iam::245983579475:role/service-role/AmazonSageMaker-ExecutionRole-20180829T145526 \
	--algorithm-specification TrainingImage=245983579475.dkr.ecr.us-east-1.amazonaws.com/resnet50-cifar:latest,TrainingInputMode=File \
	--output-data-config S3OutputPath=s3://fcncloudml/ \
	--resource-config InstanceType=ml.p3.8xlarge,InstanceCount=1,VolumeSizeInGB=16 \
	--stopping-condition MaxRuntimeInSeconds=3600
