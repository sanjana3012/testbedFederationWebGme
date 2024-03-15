# Testbed Federation Tool
## Installation
### Prerequisites
First, you need to install the following to use the testbed federation tool:
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
    - Give a name to your container. I gave it sanjanadb.
      - Set host path as :

        ```
        /Users/<yourname>/DB
        ```



      Where DB is a folder I created to store all the data related to the WebGME model.
     - ​Set the Container path as

      ```
      /data/db
      ```
      

### Dependencies and deployment
Once you have all the prerequisities, we can get to the fun part!
- To use my tool, first clone it using :

```
git clone git@github.com:sanjana3012/testbedFederationWebGme.git

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
- Tada! You are looking at the testbed federation tool now.
#### How to make a new project
- Create new project and give a name to it.
- Use the "fabfed' seed to create the project.
- Follow the instructions from there to run your own experiments and create custom code artifacts.

