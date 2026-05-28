#!/bin/bash
# Author: spicyFajitas
# Script: website_update.sh
# Purpose: Pulls the latest pre-built site from the 'built' branch and serves it.
#          GitHub Actions builds the site on every push to master and pushes the
#          output to the 'built' branch. This script only needs to pull that output.
#
# First-time setup:
#   chmod +x ~/makesite/build/website_update.sh
#   ~/makesite/build/website_update.sh
#   (The script will clone public_html and register itself in cron automatically.)

REPO_URL="https://github.com/spicyFajitas/makesite.git"
LOG_DIR="/home/adam/log"
PUBLIC_HTML="/home/adam/public_html"
SCRIPT_PATH="/home/adam/makesite/build/website_update.sh"

display_error_and_exit() {
    echo "Error: $1" >&2
    exit 1
}

# Ensure log directory exists
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR" || display_error_and_exit "Failed to create log directory"
fi

log() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_DIR/website_update.log"
}

echo -e "\n\n\n" >> "$LOG_DIR/website_update.log"
log "Script started"

# Pull or clone the built branch into public_html
if [ -d "$PUBLIC_HTML/.git" ]; then
    log "Fetching latest built site into public_html"
    git -C "$PUBLIC_HTML" fetch origin built >> "$LOG_DIR/website_update.log" 2>&1 \
        || display_error_and_exit "Failed to fetch latest site"
    git -C "$PUBLIC_HTML" reset --hard origin/built >> "$LOG_DIR/website_update.log" 2>&1 \
        || display_error_and_exit "Failed to reset public_html to latest site"
else
    if [ -d "$PUBLIC_HTML" ]; then
        log "public_html exists but is not a git repo - clearing it for fresh clone"
        rm -rf "$PUBLIC_HTML" >> "$LOG_DIR/website_update.log" 2>&1 \
            || display_error_and_exit "Failed to clear public_html"
    fi
    log "Cloning built branch into public_html"
    git clone --branch built --single-branch "$REPO_URL" "$PUBLIC_HTML" >> "$LOG_DIR/website_update.log" 2>&1 \
        || display_error_and_exit "Failed to clone built branch"
fi

log "Website update completed successfully"

# Register cron job if not already present
if ! crontab -l 2>/dev/null | grep -q "makesite/build/website_update.sh"; then
    log "Registering hourly cron job"
    (crontab -l 2>/dev/null; echo "0 * * * * $SCRIPT_PATH") | crontab - \
        || display_error_and_exit "Failed to register cron job"
else
    log "Cron job already registered"
fi

# Ensure this script remains executable
if [ ! -x "$SCRIPT_PATH" ]; then
    log "Making script executable"
    chmod +x "$SCRIPT_PATH" || display_error_and_exit "Failed to make script executable"
fi

log "Script completed"
