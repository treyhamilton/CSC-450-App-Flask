from flask import render_template
from GroceryTracking import app


@app.route("/")
@app.route("/MainMenu")
def mainMenuRoute():

    return render_template('MainMenu.html')

