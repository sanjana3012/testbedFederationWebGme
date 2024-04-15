FROM node:18


ADD . /testbedFederation
# If the following line fails, run `npm run prepare-docker` to remove test dependencies
WORKDIR /testbedFederation
RUN npm i

CMD ["npm", "start"]