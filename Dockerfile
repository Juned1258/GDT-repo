from public.ecr.aws/lambda/python:3.9
copy requirements.txt ${LAMBDA_TASK_ROOT}
copy code.py ${LAMBDA_TASK_ROOT}
run pip install -r requirements.txt
cmd ["code.lambda_handler"]