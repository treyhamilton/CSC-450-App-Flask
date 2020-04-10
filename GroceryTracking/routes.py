from flask import render_template
from GroceryTracking import app
from GroceryTracking.testModels import *

@app.route("/")
@app.route("/MainMenu")
def mainMenuRoute():

    return render_template('MainMenu.html')

