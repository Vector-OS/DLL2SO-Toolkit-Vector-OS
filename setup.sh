#!/bin/bash

# Check if the script is running on Linux
if [[ "$(uname)" != "Linux" ]]; then
    echo "This script can only run on Linux!"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."

# Update package lists
sudo apt update

# Install Mono, Wine, and other dependencies
sudo apt install -y mono-complete wine python3-pip

# Install Python dependencies from requirements.txt
pip3 install -r requirements.txt

echo "Setup complete!"
