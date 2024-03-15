# Testbed Federation Tool
## Installation
### Prerequisites
First, you need to install the following for the Webgme project to work:
- git using homebrew
  ```
  brew install git

  ```
- [NodeJS](https://nodejs.org/en/) (Version 18 strongly recommended)
- [Python](https://www.python.org/)
- [Docker desktop](https://www.docker.com/products/docker-desktop/)
- MongoDB. Pull the mongodb image in docker desktop and make a new container fro.
  - Steps to create a new container from the image:
    - Click the run button beside the mongo image and set the optional settings

Give a name to your container. I gave it sanjanadb.
Set host path as :

```
/Users/yourname/DB
```
Where DB is a folder I created to store all the database contents.
​Set the Container path as

```
/data/db
```
### Dependencies and deployment
Once you have all the preqreuisities, we can get to the fun part!
- To run my project, first clone it using :

```
git clone https://github.com/sanjana3012/mic_mini_project.git

```
- Install webgme and webgme cli:
  ###### Note: You may have to run these with --force at the end of the command. 

```
npm install webgme
npm install -g webgme-cli
    
```
- Navigate to the project using cd and install the following dependencies:
```
npm i
npm i webgme-bindings

```
- Start mongodb container in the docker desktop
- Start the webgme server using:
```
node app.js
```
or
```
webgme start
```
- copy http://127.0.0.1:8888 to your browser
- Tada! You are looking at the testbed federation tool now. Follow the instructions from there to run your own experiments and create custom code artifacts.
  
<img width="899" alt="Screenshot 2023-12-08 at 2 13 20 PM" src="https://github.com/sanjana3012/mic_mini_project/assets/143513691/04c7f004-8bf3-43d8-926a-5142c9719b85">
