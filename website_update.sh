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
PUBLIC_HTML="home/adam/public_html"

# Function to display error and exit
display_error_and_exit() {
    echo "Error: $1" >&2
    exit 1
}

# Echo current date stamp to log file
echo "$(date +'%Y-%m-%d %H:%M:%S') - Script started" >> "$LOG_DIR/website_update.log"

# Check if log directory exists, if not, create it
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR" || display_error_and_exit "Failed to create log directory"
fi

# Check if venv directory exists
if [ ! -d "$VENV_DIR" ]; then
    display_error_and_exit "Virtual environment directory $VENV_DIR not found"
fi

# Activate venv that has commonmark installed
echo "Activating venv" >> "$LOG_DIR/website_update.log"
source "$VENV_DIR/bin/activate" >> "$LOG_DIR/website_update.log" 2>&1 || display_error_and_exit "Failed to activate virtual environment"

# Move to makesite directory
cd "$MAKESITE_DIR" >> "$LOG_DIR/website_update.log" 2>&1 || display_error_and_exit "Failed to move to makesite directory"

# Git pull any new changes
echo "Git pulling any new changes that may have been pushed" >> "$LOG_DIR/website_update.log" 
git pull >> "$LOG_DIR/website_update.log" 2>&1 || display_error_and_exit "Failed to git pull updates" 

# Compile html files from markdown
echo "Compiling html website files from markdown files" >> "$LOG_DIR/website_update.log"
python3 makesite.py >> "$LOG_DIR/website_update.log" 2>&1 || display_error_and_exit "Failed to compile HTML files"

# Deactivate venv
echo "Deactivating venv" >> "$LOG_DIR/website_update.log"
deactivate >> "$LOG_DIR/website_update.log" 2>&1 || display_error_and_exit "Failed to deactivate virtual environment"

echo "Website update completed successfully" >> "$LOG_DIR/website_update.log"


# Copy output files from _site output to public_html files directory
echo "Copying output files to public_html folder"
cp -r "$OUTPUT_DIR/*" "public_html" 2>&1 || display_error_and_exit "Failed to copy files from _site output to public_html"

# Echo current date stamp to log file
echo "$(date +'%Y-%m-%d %H:%M:%S') - Script completed" >> "$LOG_DIR/website_update.log"
