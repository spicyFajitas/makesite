#!/bin/bash
# Author: spicyFajitas
# Date: 2024-02-14
# Script: website_update.sh
# Purpose: Updates web server directory contents based on rebuilding html files from markdown content

# Define paths
LOG_DIR="/home/adam/log"
VENV_DIR="/home/adam/adfulton-venv"
MAKESITE_DIR="/home/adam/makesite"
OUTPUT_DIR="/home/adam/makesite/_site"
PUBLIC_HTML="/home/adam/public_html"

# Function to display error and exit
display_error_and_exit() {
    echo "Error: $1" >&2
    exit 1
}

# Check if log directory exists, if not, create it
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR" || display_error_and_exit "Failed to create log directory"
fi

# Echo current date stamp to log file
echo -e "\n\n\n\n\n$(date +'%Y-%m-%d %H:%M:%S') - Script started" >> "$LOG_DIR/website_update.log"

# Check if venv directory exists, if not, create it
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment" >> "$LOG_DIR/website_update.log"
    python3 -m venv "$VENV_DIR" >> "$LOG_DIR/website_update.log" 2>&1 || display_error_and_exit "Failed to create virtual environment"
fi

# Activate venv
echo "Activating venv" >> "$LOG_DIR/website_update.log"
source "$VENV_DIR/bin/activate" >> "$LOG_DIR/website_update.log" 2>&1 || display_error_and_exit "Failed to activate virtual environment"

# Install commonmark if not installed
if ! python3 -c "import commonmark" &>/dev/null; then
    echo "Installing commonmark" >> "$LOG_DIR/website_update.log"
    pip install commonmark >> "$LOG_DIR/website_update.log" 2>&1 || display_error_and_exit "Failed to install commonmark"
fi

# Check if makesite directory exists, if not, clone it
if [ ! -d "$MAKESITE_DIR" ]; then
    echo "Cloning makesite repository" >> "$LOG_DIR/website_update.log"
    git clone https://github.com/spicyFajitas/makesite.git "$MAKESITE_DIR" >> "$LOG_DIR/website_update.log" 2>&1 || display_error_and_exit "Failed to clone makesite repository"
else
    # Move to makesite directory
    cd "$MAKESITE_DIR" >> "$LOG_DIR/website_update.log" 2>&1 || display_error_and_exit "Failed to move to makesite directory"

    # Git pull any new changes
    echo "Git pulling any new changes that may have been pushed" >> "$LOG_DIR/website_update.log"
    git pull >> "$LOG_DIR/website_update.log" 2>&1 || echo "Failed to git pull updates" >> "$LOG_DIR/website_update.log"
fi

# Compile html files from markdown
echo "Compiling html website files from markdown files" >> "$LOG_DIR/website_update.log"
cd $MAKESITE_DIR; python3 makesite.py >> "$LOG_DIR/website_update.log" 2>&1 || display_error_and_exit "Failed to compile HTML files"

# Deactivate venv
echo "Deactivating venv" >> "$LOG_DIR/website_update.log"
deactivate >> "$LOG_DIR/website_update.log" 2>&1 || display_error_and_exit "Failed to deactivate virtual environment"

echo "Website update completed successfully" >> "$LOG_DIR/website_update.log"

# Check if there are files in the public_html directory
if [ "$(ls -A $PUBLIC_HTML)" ]; then
    # If there are files, remove them
    echo "Removing contents of public_html folder" >> "$LOG_DIR/website_update.log"
    rm -r "$PUBLIC_HTML/"* 2>&1 || display_error_and_exit "Failed to remove files from public_html"
else
    # If there are no files, just log the information
    echo "No files found in public_html folder, skipping removal step" >> "$LOG_DIR/website_update.log"
fi

# Copy output files from _site output to public_html files directory
echo "Copying output files to public_html folder" >> "$LOG_DIR/website_update.log"
cp -r "$OUTPUT_DIR/"* "$PUBLIC_HTML/" 2>&1 || display_error_and_exit "Failed to copy files from _site output to public_html"

# Copy script to home directory root
echo "Copying script to home directory root" >> "$LOG_DIR/website_update.log"
cp "$0" "/home/adam/website_update.sh" 2>&1 || display_error_and_exit "Failed to copy script to home directory root"

# Check if crontab is up to date
if ! crontab -l | grep -q "makesite/website_update.sh"; then
    echo "Updating crontab to run hourly updates" >> "$LOG_DIR/website_update.log"
    (crontab -l 2>/dev/null; echo "0 * * * * /home/adam/makesite/website_update.sh") | crontab - 2>&1 || display_error_and_exit "Failed to update crontab"
else
    echo "Crontab already up to date" >> "$LOG_DIR/website_update.log"
fi

# Check if script is executable
if [ ! -x "/home/adam/website_update.sh" ]; then
    echo "Making script executable" >> "$LOG_DIR/website_update.log"
    chmod +x "/home/adam/website_update.sh" 2>&1 || display_error_and_exit "Failed to make script executable"
else
    echo "Script is already executable" >> "$LOG_DIR/website_update.log"
fi

# Echo current date stamp to log file
echo "$(date +'%Y-%m-%d %H:%M:%S') - Script completed" >> "$LOG_DIR/website_update.log"