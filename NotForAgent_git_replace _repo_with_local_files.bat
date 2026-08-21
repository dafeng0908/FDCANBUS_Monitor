[Git repo address]
https://github.com/dafeng0908/FDCANBUS_Monitor

[Flow replace repo with local files]
git init
git branch -M main

git remote remove origin 2>nul
git remote add origin https://github.com/dafeng0908/FDCANBUS_Monitor


git add -A
git commit -m "Replace repo with local files"


git fetch origin
git push --force-with-lease -u origin main


[close repo]
git close https://github.com/dafeng0908/FDCANBUS_Monitor


[Update file and then update repo/project]
git status
git add -A
git commit -m "Update project"

git pull --rebase origin main
git push origin main