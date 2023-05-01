# API using fastAPI + Pydantic & Athena datastore
## Intro

In this article, we will look at creating an API and datastore using the Docker on AWS with API gateway and creating it all using the modern python framework FastAPI with pydantic.
After we have stood up the API we will store the results in AWS Athena. Amazon Athena is a query service for analyzing data in S3 with SQL under the hood. Athena uses a distributed SQL engine called [Presto](https://prestodb.io/), which is used to run the SQL queries against your data in S3.

## Objectives

By the end of this article, you should be able to:
1. Ingest and validate data using pydantic and more in-depth validators for clean data.
2. Create tests with code coverage for your API.
3. Store the validated data in the AWS Athena datastore.
4. Docker file and installation.
```
fastapi-api
    ├── venv
    ├── requirements.txt
    └── app
        ├── __init__.py
        │   └── main.py
        |   └── models.py
        └── tests
            ├── __init__.py
            └── conftest.py
            └── test_main.py
```

We will be using `Python 3.10.6`, but let's create the directory structure and setup the virtual env for development.
```
$ mkdir fastapi-api && cd fastapi-api
$ mkdir app && cd app
$ mkdir test
$ cd ..
$ python3.10.6 -m venv venv
$ source venv/bin/activate
(env)$ pip install flask==1.1.2
```

For the `requirements.txt` file just add the following.
```txt
fastapi==0.65.1
pydantic
# local development & testing
pytest==6.2.1
uvicorn==0.14.0
```
Run `pip install -r requirements.txt` .

Personally, I use [poetry](https://python-poetry.org/) for most of my dependencie management these days but for this article 
 
Now let's setup the basic app in the `main.py` with routes for sending data and testing.

```python
#/app/main.py
from fastapi import FastAPI

app = FastAPI(title="Unicorn API")


@app.get("/")
def hello():
    return {"Hello": "World"}


@app.post("/unicorn")
def post_unicorn():
    return {}

```
Let's start the server and make sure everything is up and running locally.
Run this in your terminal at the root of the project. `uvicorn app.main:app --reload`  this will the auto-reload after ever change you make and you could keep it running in the background as you make code changes.

Navigate in your browser to `http://127.0.0.1:8000 ` you should see your docs for your new API.
[PLACE IMAGE HERE]

Swagger Page \[](http://127.0.0.1:8000/docs)

## Section 2
Lets start writing tests for the endpoints and create our first data model so we can validate that our unicorn endpoint accepts only valid unicorns.

```python
#app/tests/test_main.py
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World!"}
```

Time to create our first model for our unicorn with its basic data model.

```python
#/app/main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Unicorn API")


class Unicorn(BaseModel):
    name: str
    rainbow: bool

@app.get("/")
def hello():
    return {"Hello": "World"}


@app.post("/unicorn")
def post_unicorn(unicorn: Unicorn):
    return {unicorn}

```
Lets' go ahead and check out the API `http://127.0.0.1:8000 ` and we can see that the model has been introduced.
[PLACE IMAGE HERE]

Now, let's go ahead and create a proper testing harness that we will want to use later. let's put the TestClient into a `conftest.py` as we will be using it a lot and having the fixture autoload makes sense.

```python
#app/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def test_app():
    with TestClient(app) as test_client:
        yield test_client
```

Here, we imported Starlette's TestClient which is wrapped by FastAPI, which uses the requests library to make requests against the FastAPI app.
when the route is hit with a POST request, FastAPI will read the body of the request and validate the data:
When valid, the data will be available in the payload parameter. FastAPI also generates JSON Schema definitions that are then used to generate the OpenAPI schema and API documentation.
If the payload is incorrect per the pydantic model, an error is returned.


 `http --json POST http://localhost:8004/unicorn/ data={ "name": "honey", "rainbow": True }`

## Section 3
Since AWS Athena, just queries S3 data and we have validated it we can safely put the data into S3.
We will also create a service that 
In this section we will setup AWS athena and send our validated unicorn data into S3
we will also use the moto mocking library so that we can test everything locally without deploying our code to AWS.
This will allow for quicker development, and create a sense of ease before we start creating objects in s3.

```python
import boto3

def query_results(session, params, wait=True):
	client = session.client('athena')

	## This function executes the query and returns the query execution ID
	response_query_execution_id = client.start_query_execution(
		QueryString=params['query'],
		QueryExecutionContext={
			'Database': "default"
		},
		ResultConfiguration={
			'OutputLocation': 's3://' + params['bucket'] + '/' + params['path']
		}
	)

	if not wait:
		return response_query_execution_id['QueryExecutionId']
	else:
		response_get_query_details = client.get_query_execution(
			QueryExecutionId=response_query_execution_id['QueryExecutionId']
		)
		status = 'RUNNING'
		iterations = 360  # 30 mins

		while (iterations > 0):
			iterations = iterations - 1
			response_get_query_details = client.get_query_execution(
				QueryExecutionId=response_query_execution_id['QueryExecutionId']
			)
			status = response_get_query_details['QueryExecution']['Status']['State']

			if (status == 'FAILED') or (status == 'CANCELLED'):
				return False, False

			elif status == 'SUCCEEDED':
				location = response_get_query_details['QueryExecution']['ResultConfiguration']['OutputLocation']

				## Function to get output results
				response_query_result = client.get_query_results(
					QueryExecutionId=response_query_execution_id['QueryExecutionId']
				)
				result_data = response_query_result['ResultSet']

				if len(response_query_result['ResultSet']['Rows']) > 1:
					header = response_query_result['ResultSet']['Rows'][0]
					rows = response_query_result['ResultSet']['Rows'][1:]

					header = [obj['VarCharValue'] for obj in header['Data']]
					result = [dict(zip(header, get_var_char_values(row))) for row in rows]

					return location, result
				else:
					return location, None
		else:
			time.sleep(5)

		return False
 ```
## Section 4
Since AWS Athena, just queries S3 data and we have validated it we can safely put the data into S3.
We will also create a service that 
In this section we will setup AWS athena and send our validated unicorn data into S3
we will also use the moto mocking library so that we can test everything locally without deploying our code to AWS.
This will allow for quicker development, and create a sense of ease before we start creating objects in s3.

```
FROM python:latest

EXPOSE 5000

ADD requirements.txt .

RUN python3 -m pip3 install -r requirements.txt

WORKDIR /app

ADD . /app

# In order to launch our python code, we must import it into our image.
# We use the keyword 'COPY' to do that.
# The first parameter 'main.py' is the name of the file on the host.
# The second parameter '/' is the path where to put the file on the image.
# Here we put the file at the image root folder.
COPY main.py /

# We need to define the command to launch when we are going to run the image.
# We use the keyword 'CMD' to do that.
# The following command will execute "python ./main.py".
CMD [ "uvicorn", "main:app"]
```

#### Pushing docker image. Amazon ECR.

You can push your container images to an Amazon ECR repository with the docker push command. Amazon ECR also supports creating and pushing Docker manifest lists, which are used for multi-architecture images. Each image referenced in a manifest list must already be pushed to your repository. For more information, see Pushing a multi-architecture image.

To push a Docker image to an Amazon ECR repository

The Amazon ECR repository must exist before you push the image. For more information, see Creating a private repository.

### Create a private repository

Your container images are stored in Amazon ECR repositories. Use the following steps to create a private repository using the AWS Management Console. For steps to create a repository using the AWS CLI, see Step 3: Create a repository.

To create a repository (AWS Management Console)

1. Open the Amazon ECR console at https://console.aws.amazon.com/ecr/repositories.

2. From the navigation bar, choose the Region to create your repository in.

3. In the navigation pane, choose Repositories.

4. On the Repositories page, choose the Private tab, and then choose Create repository.

5. For Visibility settings, verify that Private is selected.

6. For Repository name, enter a unique name for your repository. The repository name can be specified on its own (for example nginx-web-app). Alternatively, it can be prepended with a namespace to group the repository into a category (for example project-a/nginx-web-app). The repository name must start with a letter and can only contain lowercase letters, numbers, hyphens, underscores, and forward slashes. Using a double hyphen, underscore, or forward slash isn't supported.

7. For Tag immutability, choose the tag mutability setting for the repository. Repositories configured with immutable tags prevent image tags from being overwritten. For more information, see Image tag mutability.

8. For Scan on push, while you can specify the scan settings at the repository level for basic scanning, it is best practice to specify the scan configuration at the private registry level. Specify the scanning settings at the private registry allow you to enable either enhanced scanning or basic scanning as well as define filters to specify which repositories are scanned. For more information, see Image scanning.

9. For KMS encryption, choose whether to enable encryption of the images in the repository using AWS Key Management Service. By default, when KMS encryption is enabled, Amazon ECR uses an AWS managed key (KMS key) with the alias aws/ecr. This key is created in your account the first time that you create a repository with KMS encryption enabled. For more information, see Encryption at rest.

10. When KMS encryption is enabled, select Customer encryption settings (advanced) to choose your own KMS key. The KMS key must be in the same Region as the cluster. Choose Create an AWS KMS key to navigate to the AWS KMS console to create your own key.

11. Choose Create repository.

12. (Optional) Select the repository that you created and choose View push commands to view the steps to push an image to your new repository. For more information about pushing an image to your repository, see Pushing an image.

### Pushing image (after create repository)

1. Authenticate your Docker client to the Amazon ECR registry to which you intend to push your image. Authentication tokens must be obtained for each registry used, and the tokens are valid for 12 hours. For more information, see Private registry authentication. To authenticate Docker to an Amazon ECR registry, run the aws ecr get-login-password command. When passing the authentication token to the docker login command, use the value AWS for the username and specify the Amazon ECR registry URI you want to authenticate to. If authenticating to multiple registries, you must repeat the command for each registry.

***Important
If you receive an error, install or upgrade to the latest version of the AWS CLI. For more information, see Installing the AWS Command Line Interface in the AWS Command Line Interface User Guide.***

```
aws ecr get-login-password --region region | docker login --username AWS --password-stdin aws_account_id.dkr.ecr.region.amazonaws.com
```

2. If your image repository doesn't exist in the registry you intend to push to yet, create it. For more information, see Creating a private repository.

3. Identify the local image to push. Run the ***docker*** images command to list the container images on your system.

```
docker images
```
You can identify an image with the ```repository:tag``` value or the image ID in the resulting command output.

4. Tag your image with the Amazon ECR registry, repository, and optional image tag name combination to use. The registry format is ```aws_account_id```.dkr.ecr.```region```.amazonaws.com. The repository name should match the repository that you created for your image. If you omit the image tag, we assume that the tag is latest.

The following example tags a local image with the ID ```e9ae3c220b23``` as ```aws_account_id```.dkr.ecr.```region```.amazonaws.com/```my-repository:tag```.

docker tag ```e9ae3c220b23``` ```aws_account_id```.dkr.ecr.```region```.amazonaws.com/```my-repository:tag```
Push the image using the ***docker push*** command:

docker push ```aws_account_id```.dkr.ecr.```region```.amazonaws.com/```my-repository:tag```
5. (Optional) Apply any additional tags to your image and push those tags to Amazon ECR by repeating Step 4 and Step 

## Conclusion
We covered a lot in this article. We created and tested an API with FastAPI, pytest
FastAPI is a powerful framework that makes it easy and a joy to develop RESTful APIs. With the power of pydantic you can  check the inbound data coming from other sources and even coerce the data when needed or do deeper type validation creating a more reliable data pipeline. Also, we stood up our datastore so that our analysts and datascience team could use our validated data.
