from flask import render_template
from main import app

@app.route("/")
@app.route("/MainMenu")
def mainMenu():
    return render_template('MainMenu.html')