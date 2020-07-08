# construct the ECR name.
account=$(aws sts get-caller-identity --query Account --output text)
region=$(aws configure get region)
fullname="${account}.dkr.ecr.${region}.amazonaws.com/fcn/sagemaker:latest"

# create the repository in ECR.
aws ecr create-repository --repository-name "fcn/sagemaker" > /dev/null

# Get the login command from ECR and execute it directly
$(aws ecr get-login --region ${region} --no-include-email)

# Build the docker image, tag it with the full name, and push it to ECR
docker build  -t "fcn/sagemaker" fcn-sagemaker/
docker tag "fcn/sagemaker" ${fullname}

docker push ${fullname}
