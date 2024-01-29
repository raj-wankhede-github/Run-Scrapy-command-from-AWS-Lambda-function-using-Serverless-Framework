# Run Scrapy command from AWS Lambda function using Serverless Framework
This repository provides a guide on running Scrapy commands from an AWS Lambda function using the Serverless Framework.

## Pre-requisite mandatory steps to use this repository

(Skip if you already have AWS CLI, Nodejs, npm, Serverless and Docker installed)
### 1.	Create Access and Secret Access Keys
- 	For new IAM user:
    -	Login to your AWS account and search for IAM service on the service search filter.
    -	Go to the Users page and click on “Create user”
    -	Now give a user name and click Next.
    -	Now we need to set up permissions for this user. Select on “Attach policies directly”, and provide “AdministratorAccess” to the user. This is going to provide this user full access to your AWS account, you can change if you want. And click Next.
    -	Then on the next page it will ask you to add tags (if required) and click “Create user”. 
    -	Once the user is created, follow below steps.

-	Already have IAM user:
    -	Go to User -> Security Credentials -> Under “Access Keys” click on “Create access key”.
    -	Select “Command Line Interface (CLI)” and tick the Confirmation box and click Next.
    -	Type description if required and click “Create access key”. 
    -	Click on “Download .csv file” and then click Done. Make sure not to share this file with anyone.

### 2.	Installing AWS CLI on your system
-	Install [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html#getting-started-install-instructions) on your system. 
-	After installation go to the command prompt to review your installation type “aws help”
-	Type `aws configure` and use the Access and Secret Access Keys from above step. 

### 3.	Setup NodeJS
-	To install NodeJs go to [nodeJs website](https://nodejs.org/en) and download/install. 
-	To review your installation use `node --version` from CLI to check the version.

### 4.	Installing and configuring AWS Serverless framework
-	Serverless is provided as npm package. To install serverless open CMD prompt and type `npm install -g serverless`
-	To review your installation use `serverless -v` from CLI to check the version

### 5.	Install Docker
-	Install docker from [Docker website](https://docs.docker.com/engine/install/)
-	Create account on [docker hub](https://hub.docker.com/) if you do not already have.
-	Run the docker on local machine and login to Docker hub using above credentials.

## Steps to deploy new application on AWS Lambda using Docker and Serverless Framework:
### 1.  Create new folder in your local machine 
- Name the folder `MyLambdaFunction` (or any other name that you feel suitable for this project).

### 2.  Move into the created folder
- cd into above created folder from CLI of your local machine.

### 3.  Copy all the application data 
- Clone this Repo and then copy all the contents into `MyLambdaFunction` folder.

### 4.  Create ECR Repository on AWS: 
- Use [AWS Console](https://us-east-1.console.aws.amazon.com/ecr/) or [AWS CLI](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/ecr/create-repository.html)
- Name the repo “my-repo-custom” (or any other name that you feel suitable for this project).
- Copy the URI that was generated for this ECR repo, we will need it later.

### 5.  NOTE
- You need to have [docker (up and running)](https://docs.docker.com/engine/install/), [AWS Serverless](https://www.serverless.com/framework/docs/getting-started) and [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) installed and configured. 
- Please follow the pre-requisite section (above) that has 5 steps at the [start of this documentation](https://github.com/raj-wankhede-github/Run-Scrapy-command-from-AWS-Lambda-function-using-Serverless-Framework#pre-requisite-mandatory-steps-to-use-this-repository). 
- Proceed only if pre-requisite is fulfilled.

### 7.  Edit serverless.yml
- Locate the file `serverless.yml` in `MyLambdaFunction` folder
- Edit the file and replace `region` and `image`. 
- The value for `image` was copied from point 4 above. Make sure to add “:latest” at the end of image URI.
- For `region`, use the region where you would like to deploy the Lambda function.

### 8.  Move into the created folder
- cd into `MyLambdaFunction` folder from CLI (if you are not already in it).

### 9.  From the CLI
- Kindly make sure you have AWS CLI logged in using `aws configure` command and use below command.
- Go to AWS Console for ECR and select the repository and click “View push commands”.
- The commands here contains ->  `docker build`, `docker tag` and `docker push`.
- Select the OS that you are using on your local machine.
- Start from step 2 (building the image) under the commands as step 1 was performed in previous step. 
- Please build image (Step 2) using command shared below in case of MacOs with M1 chip.

- In case of MACOS, build the image using below command
    ```
    docker buildx build --platform linux/amd64 -f ./Dockerfile -t <repo-Name> .
    ```
    
    - Replace the <repo-Name> with name used in [step 4 above](https://github.com/raj-wankhede-github/Run-Scrapy-command-from-AWS-Lambda-function-using-Serverless-Framework#4--create-ecr-repository-on-aws), for example in this case, it is “my-repo-custom”. Do not miss the “.” at the end of above command.

- NOTE: Make sure not to change the name from any of these commands unless you know what you are doing.

### 10.  Move into the created folder
- cd into `MyLambdaFunction` folder from CLI (if you are not already in it) and run below command
`serverless deploy --region <region>`
- Replace the <region> above where you want to deploy Lambda function.

### 13.  Patience!
- Wait for the stack to deploy and navigate to AWS Lambda console and test the same.

## Steps to Update Lambda function.
- Update the files as per your requirement in your local machine (Dockerfile/Serverless.yml/Code etc.) under `MyLambdaFunction` directory.
- Follow steps 8 till 13 from above.

