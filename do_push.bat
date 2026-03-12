@echo off
cd /d "d:\nlp2mysql"
git init
git add .
git commit -m "Initial commit: nlp2mysql" 2>nul || git commit -m "Update nlp2mysql" --allow-empty
git branch -M main
git remote remove origin 2>nul
git remote add origin https://github.com/weidada051006/mcp_Mysql.git
git push -u origin main
