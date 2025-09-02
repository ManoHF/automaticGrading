# Automatic Grading

This is a web application develeoped using Flask to prove the ability of AI (in this, *Open AI' GPT*) to **solve and grade exams**. It provides an interface that allows uploading PDF and DOCX
files to first solve them, and then grade them using a file with the correct answers. The results are stored on MongoDB Atlas, which lets you manage MongoDB clusters in the cloud.

## Prerrequisites

### MongoDB Atlas

Is it important to have an account configured with a cluster. This cluster will provide us with a **key** that will allow connection between the application and the cluster. The process to
set this up is the following:
1. On Main Page: Project -> New Project -> Create (Set up name and use default settings)
2. Inside new project: Create Cluster (there is a Free Tier) -> Create Deployment
3. Set up connection to cluster, including account and pw
   * Set up IP Addresses you will be using to connect
   * Connection Method: driver -> python -> retrieve `URI` and update with previously set pw
  

