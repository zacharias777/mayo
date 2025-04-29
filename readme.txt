
1. Change congig.sample.py to config.py
2. Add the real username and password
3. Make a virual env to run this code in by going:
--python3 -m venv env  
--source env/bin/activate
--pip install -r requirements.txt
--python3 yf-hist.py

Note - here's how I run pip commands, because I'm globally on the kraken default
pip install mysql-connector-python --index-url https://pypi.org/simple

##To make updates:
##Check out the repo, make a branch for changes, and then commit that branch
---------------
cd repos
cd mayo
git clone https://github.com/username/repository.git
git checkout -b my-feature-branch
--make some edits
--do git branch to check that your on the right branch
--do git status to see what you've changed
git add .  # Add all changes
git commit -m "build: Adding all the files from mustard"
git push origin my-feature-branch  # If using a branch

##Then merge those features into the main branch
git checkout main
git pull origin main
git merge my-feature-branch
git push origin main