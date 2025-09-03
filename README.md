# Automatic Grading

This is a web application develeoped using Flask to prove the ability of AI (in this, *Open AI' GPT*) to **solve and grade exams**. It provides an interface that allows uploading PDF and DOCX
files to first solve them, and then grade them using a file with the correct answers. The results are stored on MongoDB Atlas, which lets you manage MongoDB clusters in the cloud.

## 1 Prerrequisites & Installation

### 1.1 MongoDB Atlas

Is it important to have an account configured with a cluster. This cluster will provide us with a **key** that will allow connection between the application and the cluster. The process to
set this up is the following:
1. On Main Page: Project -> New Project -> Create (Set up name and use default settings)
2. Inside new project: Create Cluster (there is a Free Tier) -> Create Deployment
3. Set up connection to cluster, including account and pw
   * Set up IP Addresses you will be using to connect
   * Connection Method: driver -> python -> retrieve `URI` and update with previously set pw

**IMPORTANT**: When retrieving your URI, you may need to include your db name: `mongodb+srv://<username>:<password>@<cluster-name>.mongodb.net/<dbname>?retryWrites=true&w=majority`

> In case you need new IP addresses to connect from: go to Security -> Network Access -> Add IP Adress

### 1.2 OpenAI

Create an account for the OpenAI Platform (not the same as ChatGPT). Create an API Key with all permissions and save it. 

> Make sure you check the pricing of calls and account balance.

### 1.3 Code Repository

Create a `.env` file at the same level as Requirements.txt. The last value should be chosen by you and it adds security to your Flask application. It should include the following (be aware of the single quotes):

```.env
AISERVICE_KEY=<key_retrieved_on_1.2>
MONGO_URI='<uri_retrieved_on_1.1>'
SECRET_KEY='<own_choice>'
```

Install python and all the required packages. The recommended way is to use a virtual environment:

```shell
conda create –name <envName>
conda activate <envName>
pip install -r requirements.txt
```
  
> Make sure your IDE is using the correct python interpreter in case you are seeing package errors

