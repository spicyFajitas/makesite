<!-- title: Home -->
<!-- subtitle: spicyFajitas -->

# Hello

Welcome to my MTU Shell Website!

If you're looking for my documentation, check out my [documentation website](https://spicyfajitas.github.io/cookbooks/).

Technology/role specific `readme.md` files are located in my GitHub [cookbooks repository](https://github.com/spicyFajitas/cookbooks).

To Do (website_update.sh):

- [ ] Have script be entirely self-contained
  - [ ] Check if venv is installed, if not, `python3 -m venv ./adfulton-venv`
  - [ ] `pip install commonmark`
  - [ ] Check if git repo has been downloaded (run `git pull`, if error, `git clone https://github.com/spicyFajitas/makesite`)`
  - [ ] Copy script to home directory root (/home/adam/website_update.sh)
  - [ ] Check if crontab is up to date (grep for script name) - if not, template crontab to run hourly updates
