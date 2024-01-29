FROM public.ecr.aws/lambda/python:3.8

# Required for lxml
RUN yum install -y gcc libxml2-devel libxslt-devel
COPY . ${LAMBDA_TASK_ROOT}
RUN pip install --upgrade pip
RUN pip3.8 install -r requirements.txt
WORKDIR ${LAMBDA_TASK_ROOT}/newsdata/spiders
CMD [ "lambda_function.handler" ]
