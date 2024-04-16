FROM node:18

# Install Python and necessary packages for creating a virtual environment
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    python3-venv

# Create a virtual environment
RUN python3.11 -m venv /venv

# Activate the virtual environment for subsequent commands
ENV PATH="/venv/bin:$PATH"

# Change working directory
WORKDIR /testbedFederation

# Add application files
ADD . /testbedFederation

# Install Node.js dependencies
RUN npm install

# Rebuild ZeroMQ specifically to handle any native bindings
RUN npm rebuild zeromq --build-from-source

# Install Python bindings for WebGME using the virtual environment
RUN pip install pyyaml webgme-bindings

# Command to start the application
CMD ["npm", "start"]
