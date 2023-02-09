import json

import pandas as pd
import plotly
import plotly.express as px
from application import app
from flask import Flask, jsonify, render_template, request
from flaskext.mysql import MySQL


#   host: "seniordesign-db.cxwhjsfccgui.us-east-1.rds.amazonaws.com",
#   port: "3306",
#   user: "admin",
#   password: "password!",

# https://flask-mysqldb.readthedocs.io/en/latest/
app.config['MYSQL_DATABASE_HOST'] = "seniordesign-db.cxwhjsfccgui.us-east-1.rds.amazonaws.com"
app.config['MYSQL_DATABASE_USER'] = "admin"
app.config['MYSQL_DATABASE_PASSWORD'] = "password!"
app.config['MYSQL_DATABASE_DB'] = "SeniorDesign"
app.config['MYSQL_DATABASE_PORT'] = 3306
mysql = MySQL()
mysql.init_app(app)
# cursor = mysql.get_db().cursor()


@app.route('/hello', methods=['GET', 'POST'])
def hello():

    # POST request
    if request.method == 'POST':
        print('Incoming..')
        print(request.get_json())  # parse as JSON
        return 'OK', 200

    # GET request
    else:
        message = {'greeting':'Hello from Flask!'}
        return jsonify(message)  # serialize and use JSON headers

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chart1')
def chart1():

    # Graph One
    df = px.data.medals_wide()
    fig1 = px.bar(df, x="nation", y=["gold", "silver", "bronze"], title="Wide-Form Input")
    graph1JSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

    # Graph two
    df = px.data.iris()
    fig2 = px.scatter_3d(df, x='sepal_length', y='sepal_width', z='petal_width',
              color='species',  title="Iris Dataset")
    graph2JSON = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    # Graph three
    df = px.data.gapminder().query("continent=='Oceania'")
    fig3 = px.line(df, x="year", y="lifeExp", color='country',  title="Life Expectancy")
    graph3JSON = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)


    return render_template('index.html', graph1JSON=graph1JSON,  graph2JSON=graph2JSON, graph3JSON=graph3JSON)



@app.route('/chart2', methods=['GET', 'POST'])
def chart2():
    # POST request
    if request.method == 'POST':
        print('Incoming..')
        print(request.get_json())  # parse as JSON

        
    
    cursor = mysql.get_db().cursor()
    cursor.execute("SELECT City FROM SeniorDesign.CrimeData GROUP BY City")
    cities=cursor.fetchall()
    cursor.execute("SELECT Year(Date) AS Year FROM SeniorDesign.CrimeData GROUP BY Year(Date)"),
    years=cursor.fetchall()
    cursor.execute("SELECT Offense AS Year FROM SeniorDesign.CrimeData GROUP BY Year(Date)"),
    years=cursor.fetchall()
    

    # query = 'SELECT * FROM SeniorDesign.CrimeData WHERE City="' +city +'" AND Date >= ' + minDate + " AND Date < " + maxDate +";"

    cursor.execute("SELECT * FROM CrimeData")
    cityData = cursor.fetchall()
    print(cityData)
    df = pd.DataFrame(cityData, columns=["id", "city", "date", "offense", "latitude", "longitude"])
    print(df)
    # print(df.groupby(['category']).count())
    crimeCount=df.groupby(['city']).count().reset_index()
    # print(uniqueCrimes)
    print(df)
    print(years)
    print(cities)
    # fig = px.pie(df, values=1, names=1, title='Population of European continent')
    # Graph One
    df = px.data.medals_wide()
    fig1 = px.bar(crimeCount, x="city", y="offense", color="offense", title="Amount of Crimes in each City")
    graph1JSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

        # Graph One
    fig2 = px.pie(crimeCount, values="offense", names="city", color="offense", title="Pie Crime")
    graph2JSON = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)


    # yearCount=df.groupby(['city']).count().reset_index()
    # print(yearCount)
    # fig3 = px.bar(yearCount, x="city", y="offense", color="offense", title="Amount of Crimes in each City")
    # graph3JSON = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html', graph1JSON=graph1JSON, graph2JSON=graph2JSON, cities=cities, years=years)

    # # Graph two
    # df = px.data.iris()
    # fig2 = px.scatter_3d(df, x='sepal_length', y='sepal_width', z='Crime Data',
    #           color='species',  title="Iris Dataset")
    # graph2JSON = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    # # Graph three
    # df = px.data.gapminder().query("continent=='Oceania'")
    # fig3 = px.line(df, x="year", y="lifeExp", color='country',  title="Crime Data")
    # graph3JSON = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)


    # return render_template('index.html', graph1JSON=graph1JSON,  graph2JSON=graph2JSON, graph3JSON=graph3JSON)
