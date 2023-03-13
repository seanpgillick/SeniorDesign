from flask import Flask, jsonify, render_template, request

import json
from unicodedata import decimal
import folium
from folium.plugins import HeatMap
import pandas as pd
import plotly
import plotly.express as px
from flaskext.mysql import MySQL
from decimal import Decimal
from unicodedata import decimal
import folium
from folium.plugins import HeatMap
import markupsafe


application = Flask(__name__) # This needs to be named `application`


#   host: "seniordesign-db.cxwhjsfccgui.us-east-1.rds.amazonaws.com",
#   port: "3306",
#   user: "admin",
#   password: "password!",

# https://flask-mysqldb.readthedocs.io/en/latest/
application.config['MYSQL_DATABASE_HOST'] = "seniordesign-db.cxwhjsfccgui.us-east-1.rds.amazonaws.com"
application.config['MYSQL_DATABASE_USER'] = "admin"
application.config['MYSQL_DATABASE_PASSWORD'] = "password!"
application.config['MYSQL_DATABASE_DB'] = "SeniorDesign"
application.config['MYSQL_DATABASE_PORT'] = 3306
mysql = MySQL()
mysql.init_app(application)
# cursor = mysql.get_db().cursor()

@application.route('/')
def index():
    return render_template('index.html')

@application.route('/graphResults', methods=['GET', 'POST'])
@application.route('/graphResults/<city>', methods=['GET', 'POST'])
def graphResults(city=None):
    # print(request.args.getlist('city'))
    if request.method == 'POST':
        print('Incoming..')
        print(request.get_json()) 
        return ("Nothing") # parse as JSON
    
    else:
        cursor = mysql.get_db().cursor()
        
        yearsSelect=[]
        citiesSelect=[]
        offenses=[]
        print("Here")
        print(city)
        if(city!=None):
            # cityString="("

            # for i in request.args.getlist('city'):
            #     cityString=cityString+"'"+i+"', "
            # cityString=cityString[:-2]+")"
            print(city)
            cityString="('"+city+"')"
            # cursor.execute("SELECT City, Year(Date) as Year, Offense, Latitude, Longitude FROM SeniorDesign.CrimeData WHERE Year(Date) IN "+yearString+" AND City IN "+cityString)
            cursor.execute("SELECT City, Year(Date) as Year, Offense, Latitude, Longitude, crime_type FROM SeniorDesign.CrimeData WHERE City IN "+cityString)


            crimeData = cursor.fetchall()

            cursor.execute("SELECT * FROM SeniorDesign.CrimeTypeTotals WHERE City IN "+cityString)
            cityTypeData = cursor.fetchall()



            df = pd.DataFrame(crimeData, columns=["city", "date", "offense", "latitude", "longitude", "crimeType"])
            dfType = pd.DataFrame(cityTypeData, columns=["id", "city", "homicide", "agg_assault", "rape", "robbery", "violent", "theft", "burglary", "arson", "property", "other", "total", "year", "vehicle_theft"])



            crimeCountTypesType=df.groupby(['city']).count().reset_index()

            #VIOLENT, PROPERTY, OTHER

            

            crimeCountCity=df.groupby(['city']).count().reset_index()
            crimeCountDates=df.groupby(['date']).count().reset_index()
            crimeCountTypes=df.groupby(['crimeType']).count().reset_index()
            agg_functions = {'homicide': 'sum', "agg_assault": 'sum', "rape": 'sum', "robbery": 'sum', "violent": 'sum', "theft": 'sum', "burglary": 'sum', "arson": 'sum', "property": 'sum', "other": 'sum', "total": 'sum', "year": 'first', "vehicle_theft": 'sum'}

            dfType = dfType.groupby(df['city']).aggregate(agg_functions)
            # df = px.data.medals_wide()
            # fig1 = px.bar(crimeCountTypes, x="crimeType", y="offense", color="offense", title="Types of crime in each city")
            # graph1JSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

            # fig1 = px.bar(dfType, x=["homicide", "agg_assault", "rape", "robbery", "violent", "theft", "burglary", "arson", "property", "other", "vehicle_theft"], y=["homicide", "agg_assault", "rape", "robbery", "violent", "theft", "burglary", "arson", "property", "other", "vehicle_theft"], color="offense", title="Types of crime in each city")
            # graph1JSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

            # Graph Two
            # df = px.data.tips()
            print(dfType)
            print(dfType['total'][0])
            dataSun = dict(
                character=["Theft", "Burglary", "Arson", "Vehicle Theft", "homicide", "Aggravated Assault", "Rape", "Robbery"],
                parent=["Property", "Property", "Property", "Property", "Violent", "Violent", "Violent", "Violent"],
                value=[dfType['theft'][0], dfType['burglary'][0], dfType['arson'][0], dfType['vehicle_theft'][0], dfType['homicide'][0], dfType['agg_assault'][0], dfType['rape'][0], dfType['robbery'][0]]
            )
            # fig2 = px.sunburst(dfType, path=['rape', 'robbery', 'violent'])
            fig2 = px.sunburst(
                dataSun,
                names='character',
                parents='parent',
                values='value',
            )
            graph1JSON = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

            fig3 = px.line(crimeCountDates, x=['2019', '2020', '2021'], y='offense', title="count of crimes per year", markers=True)
            graph2JSON = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)

            
            print("we made it here")
            # return fig1.to_html(full_html=False, include_plotlyjs=False)
            return [graph1JSON, graph2JSON]



@application.route('/statistics', methods=['GET', 'POST'])
@application.route('/statisticscity=<city>year=<year>', methods=['GET', 'POST'])
def statistics(city=None, year=None):
    if request.method == 'POST':
        print('Incoming..')
        print(request.get_json()) 
        return ("Nothing") # parse as JSON
    
    else:
        cursor = mysql.get_db().cursor()
        cursor.execute("SELECT City FROM SeniorDesign.CrimeData GROUP BY City")
        citiesSQL=cursor.fetchall()
        cursor.execute("SELECT Year(Date) AS Year FROM SeniorDesign.CrimeData GROUP BY Year(Date)"),
        yearsSQL=cursor.fetchall()

        citiesSelect=[]
        yearsSelect=[]

        for i in citiesSQL:
            citiesSelect.append(i[0])

        for i in yearsSQL:
            yearsSelect.append(i[0])

        return render_template("statistics.html", cities=citiesSelect, years=yearsSelect)


@application.route('/mapGencity=<city>year=<year>', methods=['GET', 'POST'])
def heatmapGen(city, year):
    cursor = mysql.get_db().cursor()
    cityList = []
    cityList.append(city)
    yearList = []
    yearList.append(year)
    if(cityList!=[] and yearList!=[]):
        yearString="("
        cityString="("
        for i in yearList:
            yearString=yearString+"'"+i+"', "
        for i in cityList:
            cityString=cityString+"'"+i+"', "
        cityString=cityString[:-2]+")"
        yearString=yearString[:-2]+")"
        print(yearString)
        print(cityString)
        cursor.execute("SELECT City, Year(Date) as Year, Latitude, Longitude FROM SeniorDesign.CrimeData WHERE Year(Date) IN "+yearString+" AND City IN "+cityString)
        # cursor.execute("SELECT * FROM CrimeData WHERE Year(Date) IN "+yearString+" AND City IN "+cityString+" LIMIT 10000")
        cityData = cursor.fetchall()

        df = pd.DataFrame(cityData, columns=["city", "year", "latitude", "longitude"])
        print(df)
        mapObj = folium.Map([39.9526, -75.1652], zoom_start=12)
        data = []
        temp = df.to_numpy()
        for x in temp:
            if((x[2] is not None) and (x[3] is not None) and (isinstance(x[2], Decimal)) and (isinstance(x[3], Decimal))):
                data.append([x[2], x[3], .2])
        # for x in data:
        #     print(x)

        HeatMap(data).add_to(mapObj)
        return mapObj._repr_html_()

    else:
        mapObj = folium.Map([39.9526, -75.1652], zoom_start=12)
        data = []
        return mapObj._repr_html_()

@application.route('/heatmap', methods=['GET', 'POST'])
def heatmapInputs(city=None, year=None):
    if request.method == 'POST':
        print('Incoming..')
        print(request.get_json()) 
        return ("Nothing") # parse as JSON
    else:

        cursor = mysql.get_db().cursor()
        cursor.execute("SELECT City FROM SeniorDesign.CrimeData GROUP BY City")
        citiesSQL=cursor.fetchall()
        cursor.execute("SELECT Year(Date) AS Year FROM SeniorDesign.CrimeData GROUP BY Year(Date)"),
        yearsSQL=cursor.fetchall()
        cursor.execute("SELECT Offense FROM SeniorDesign.CrimeData GROUP BY Offense"),
        offensesSQL=cursor.fetchall()
        yearsSelect=[]
        citiesSelect=[]
        offenses=[]
        for i in yearsSQL:
            yearsSelect.append(i[0])

        for i in citiesSQL:
            citiesSelect.append(i[0])

        for i in offensesSQL:
            offenses.append(i[0])

        return render_template('heatmap.html', cities=citiesSelect, years=yearsSelect)

@application.route('/graphs', methods=['GET', 'POST'])
@application.route('/graphscity=<city>year=<year>', methods=['GET', 'POST'])
def graphs(city=None, year=None):
    # POST request
    print(request.args.getlist('city'))
    print(request.args.getlist('year'))
    print(city)
    print(year)
    if request.method == 'POST':
        print('Incoming..')
        print(request.get_json()) 
        return ("Nothing") # parse as JSON

    else:
    
        cursor = mysql.get_db().cursor()
        cursor.execute("SELECT City FROM SeniorDesign.CrimeData GROUP BY City")
        citiesSQL=cursor.fetchall()
        cursor.execute("SELECT Year(Date) AS Year FROM SeniorDesign.CrimeData GROUP BY Year(Date)"),
        yearsSQL=cursor.fetchall()
        cursor.execute("SELECT Offense FROM SeniorDesign.CrimeData GROUP BY Offense"),
        offensesSQL=cursor.fetchall()
        yearsSelect=[]
        citiesSelect=[]
        offenses=[]
        for i in yearsSQL:
            yearsSelect.append(i[0])
        
        for i in citiesSQL:
            citiesSelect.append(i[0])

        for i in offensesSQL:
            offenses.append(i[0])

        if(request.args.getlist('city')!=[] and request.args.getlist('city')!=[]):
            yearString="("
            cityString="("
            for i in request.args.getlist('year'):
                yearString=yearString+"'"+i+"', "
            for i in request.args.getlist('city'):
                cityString=cityString+"'"+i+"', "
            cityString=cityString[:-2]+")"
            yearString=yearString[:-2]+")"
            print(yearString)
            print(cityString)
            cursor.execute("SELECT City, Year(Date) as Year, Offense, Latitude, Longitude FROM SeniorDesign.CrimeData WHERE Year(Date) IN "+yearString+" AND City IN "+cityString)
            # cursor.execute("SELECT * FROM CrimeData WHERE Year(Date) IN "+yearString+" AND City IN "+cityString+" LIMIT 10000")
            cityData = cursor.fetchall()

            df = pd.DataFrame(cityData, columns=["city", "date", "offense", "latitude", "longitude"])

            crimeCount=df.groupby(['city']).count().reset_index()

            df = px.data.medals_wide()
            fig1 = px.bar(crimeCount, x="city", y="offense", color="offense", title="Amount of Crimes in each City")
            graph1JSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

            # Graph Two
            fig2 = px.pie(crimeCount, values="offense", names="city", color="offense", title="Pie Crime")
            graph2JSON = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

            return render_template('index.html', graph1JSON=graph1JSON, graph2JSON=graph2JSON, cities=citiesSelect, years=yearsSelect)
        # else:
        else:
            cursor.execute("SELECT * FROM CrimeData LIMIT 1000")
            cityData = cursor.fetchall()
        
        
        # query = 'SELECT * FROM SeniorDesign.CrimeData WHERE City="' +city +'" AND Date >= ' + minDate + " AND Date < " + maxDate +";"


            df = pd.DataFrame(cityData, columns=["id", "city", "date", "offense", "latitude", "longitude"])

            crimeCount=df.groupby(['city']).count().reset_index()

            df = px.data.medals_wide()
            fig1 = px.bar(crimeCount, x="city", y="offense", color="offense", title="Amount of Crimes in each City")
            graph1JSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

            # Graph Two
            fig2 = px.pie(crimeCount, values="offense", names="city", color="offense", title="Pie Crime")
            graph2JSON = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

            return render_template('graphs.html', graph1JSON=graph1JSON, graph2JSON=graph2JSON, cities=citiesSelect, years=yearsSelect)
 

if __name__ == "__main__":
    application.run(port=2000, debug=True)