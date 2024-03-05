# Makesite

This repo assumes an architecture in which shell users each have their own home directories located at `/home/{{username}}`

Within each home directory is a `public_html` folder. The shell server servers the html contents of each user's home/{{user}}/public_html directory.

Root index.md file is located in the `content` folder.

## First time instructions

To start this script for the first time, ensure it is located in the home directory of the user it will be updating the shell page for. Also ensure the script is executable (`chmod +x website_update.sh`). Then run the script with `./website_update.sh` and it will create the necessary automation.
