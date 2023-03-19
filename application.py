from flask import Flask, jsonify, render_template, request

import json
from unicodedata import decimal
import folium
from folium.plugins import HeatMap
import pandas as pd
import plotly
import plotly.express as px
from flaskext.mysql import MySQL
from unicodedata import decimal
import folium
from folium.plugins import HeatMap
import markupsafe
import numpy as np
import math


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
    cursor = mysql.get_db().cursor()
    cursor.execute("SELECT city FROM SeniorDesign.CityInformation")
    citiesSQL=cursor.fetchall()

    # cursor.execute("SELECT Year FROM SeniorDesign.CrimeTypeTotals GROUP BY Year"),
    # yearsSQL=cursor.fetchall()

    citiesSelect=[]
    # yearsSelect=[]

    for i in citiesSQL:
        citiesSelect.append(i[0])

    # for i in yearsSQL:
        # yearsSelect.append(i[0])

    return render_template("index.html", cities=citiesSelect)

def getSQLString(cityList):
    cityString="("
    for i in cityList:
        cityString=cityString+"'"+i+"', "
    cityString=cityString[:-2]+")"
    return cityString


@application.route('/analysis/')
def crimeLoad(city=None):
    city=request.args.get('city')
    jsonData=graphResults(city)
    cityInfo=getDataDrops(city)
    return render_template("crimeAnalysis.html", graph1JSON=jsonData[0], graph2JSON=jsonData[1], graph3JSON=jsonData[2], years=cityInfo['years'], cities=cityInfo['cities'], tab="data", city=city)


@application.route('/mapUpdate/')
def mapLoad(city=None):
    city=request.args.get('city')
    cityInfo=getHeatMapDrops(city)
    return render_template("crimeAnalysis.html", years=cityInfo['years'], cities=cityInfo['cities'], tab="heatmap", city=city)


@application.route('/analysis/<city>/<tab>', methods=["GET", "POST"])
def crimeAnalysis(city=None, tab=None):
    print(tab)
    if(tab=="data"):
        jsonData=graphResults(city)
        cityInfo=getDataDrops(city)
        return render_template("crimeAnalysis.html", graph1JSON=jsonData[0], graph2JSON=jsonData[1], years=cityInfo['years'], cities=cityInfo['cities'], tab="data", city=city)
    elif(tab=="heatmap"):
        cityInfo=getHeatMapDrops(city)
        return render_template('crimeAnalysis.html', years=cityInfo['years'], cities=cityInfo['cities'], tab="heatmap", city=city)
    elif(tab=="crimelist"):
        df=getCrimeList(city)
        print(df)
        return render_template("crimeAnalysis.html", tab="crimelist", city=city, crimeData=np.array(df))
    elif(tab=="safety"):
        cityInfo = safetyScore()
        return render_template('crimeAnalysis.html', safetyScore=cityInfo["safetyScore"], 
                                address=cityInfo["address"], latitude=cityInfo["latitude"], longitude=cityInfo["longitude"], 
                                state=cityInfo["state"], city=city, tab="safety", radius=cityInfo["radius"], unit=cityInfo["unit"])


    return render_template("crimeAnalysis.html")

@application.route('/analysis/<city>/<tab>/enhanceGraphs/pieYears=<pieYears>')
@application.route('/analysis/<city>/<tab>/enhanceGraphs/compCity=<compCity>')
@application.route('/analysis/<city>/<tab>/enhanceGraphs/pieYears=<pieYears>compCity=<compCity>')
def dataGraphsUpdate(city=None, tab=None, pieYears=None, compCity=None):
    jsonData=graphResults(city)
    cityInfo=getDataDrops(city)
    if(pieYears!=None):
        graph1JSON=sunGraph(city, pieYears)[0]
    else:
        graph1JSON=jsonData[0]
    if(compCity!=None):
        graph2JSON=lineGraph(city, compCity)[0]
    else:
        graph2JSON=jsonData[1]
    graph3JSON=jsonData[2]

    return render_template("crimeAnalysis.html", graph1JSON=graph1JSON, graph2JSON=graph2JSON, graph3JSON=graph3JSON, years=cityInfo['years'], pieYears=pieYears, compCity=compCity, cities=cityInfo['cities'], tab="data", city=city)


@application.route('/cityDrops', methods=['GET', 'POST'])
@application.route('/cityDropscity=<city>year=<year>', methods=['GET', 'POST'])
def getDataDrops(city=None, year=None):
    if request.method == 'POST':
        print('Incoming..')
        print(request.get_json()) 
        return ("Nothing") # parse as JSON
    
    else:
        cursor = mysql.get_db().cursor()
        cityString=getSQLString([city])
        cursor.execute("SELECT Year FROM SeniorDesign.CrimeTypeTotals WHERE city IN "+cityString),
        yearsSQL=cursor.fetchall()
        cursor.execute("SELECT city FROM SeniorDesign.CityInformation WHERE city NOT IN "+cityString)
        citiesSQL=cursor.fetchall()

        citiesSelect=[]
        yearsSelect=[]

        for i in citiesSQL:
            citiesSelect.append(i[0])

        for i in yearsSQL:
            yearsSelect.append(i[0])
        return {"years":yearsSelect, "cities":citiesSelect}
    
@application.route('/crimeList', methods=['GET', 'POST'])
@application.route('/crimeListcity=<city>year=<year>', methods=['GET', 'POST'])
def getCrimeList(city=None, year=None):
    if request.method == 'POST':
        print('Incoming..')
        print(request.get_json()) 
        return ("Nothing") # parse as JSON
    
    else:
        cursor = mysql.get_db().cursor()
        cityString=getSQLString([city])
        cursor.execute("SELECT * FROM SeniorDesign.CrimeData WHERE city IN "+cityString)
        crimeSQL=cursor.fetchall()
        df = pd.DataFrame(crimeSQL, columns=["id", "city", "state", "offense", "crime_type", "date", "latitude", "longitude"])
        plotDF=df[['id', 'offense', 'crime_type', 'date']].copy()


        return plotDF
    
@application.route('/cityDrops', methods=['GET', 'POST'])
@application.route('/cityDropscity=<city>year=<year>', methods=['GET', 'POST'])
def getHeatMapDrops(city=None, year=None):
    if request.method == 'POST':
        print('Incoming..')
        print(request.get_json()) 
        return ("Nothing") # parse as JSON
    
    else:
        cursor = mysql.get_db().cursor()
        cityString=getSQLString([city])
        cursor.execute("SELECT Year FROM SeniorDesign.CrimeTypeTotals WHERE city IN "+cityString),
        yearsSQL=cursor.fetchall()
        cursor.execute("SELECT city FROM SeniorDesign.CityInformation")
        citiesSQL=cursor.fetchall()

        citiesSelect=[]
        yearsSelect=[]

        for i in citiesSQL:
            citiesSelect.append(i[0])

        for i in yearsSQL:
            yearsSelect.append(i[0])
        return {"years":yearsSelect, "cities":citiesSelect}

@application.route('/safetyScore', methods=['GET', 'POST'])
def safetyScore():
    latitude = request.args.get('latitude') 
    longitude = request.args.get('longitude')
    radius = request.args.get('radius')
    city = request.args.get('city')
    address = request.args.get('address')
    radiusUnit = request.args.get('unit') or "mi"
    safetyScore = None
    cityState = ""
    if(city and latitude and longitude and radius):
        # Get crimes withing selected area 
        if(radiusUnit == "km"):
            print("km")
            kmRadius = float(radius) * 0.621371
            print(kmRadius)
        else:
            kmRadius = float(radius) 
        cursor = mysql.get_db().cursor()
        
        # cursor.execute("set @px="+str(longitude)+";")
        # cursor.execute("set @py="+str(latitude)+";")
        # cursor.execute("set @rangeKm="+str(kmRadius)+";")
        # cursor.execute("""set @search_area = st_makeEnvelope (
        #     point((@px + @rangeKm / 111), (@py + @rangeKm / 111)),
        #     point((@px - @rangeKm / 111), (@py - @rangeKm / 111)));""")
        


        # cursor.execute("SELECT latitude, longitude, st_distance_sphere(point(@px, @py), point(longitude, latitude)) as distanc FROM SeniorDesign.CrimeData WHERE city='"+city+"' AND st_contains(@search_area, point("+longitude+","+latitude+"))")
        
        cursor.execute("SELECT latitude, longitude FROM SeniorDesign.CrimeData WHERE city='"+city+"' AND SQRT(POW("+latitude+" - latitude , 2) + POW("+longitude+" - longitude, 2)) * 100 < "+str(kmRadius)+"")

        crimeLatLng = cursor.fetchall()
        crimeCountInRadius = cursor.rowcount
        print(radiusUnit)
        print(crimeCountInRadius)       
        # crimeCountInRadius = crimeCountInRadius[0][0]

        # Get city total crimes and total number of crimes
        cursor = mysql.get_db().cursor()
        cursor.execute("""SELECT SUM(ctt.total) as total_crime, ci.area, ci.state
                            FROM SeniorDesign.CrimeTypeTotals ctt
                            INNER JOIN SeniorDesign.CityInformation ci 
                                ON ci.city = ctt.city
                            WHERE ctt.city='{}'
                            GROUP BY ci.area 
                            LIMIT 1;""".format(city))
        
        cityInformation = cursor.fetchone()
        totalCrimeInCity = cityInformation[0]
        cityArea = cityInformation[1]
        cityState = cityInformation[2]
        
        # Calculate safety score
        areaOfCircle = math.pi*(float(kmRadius) ** 2)
        N = areaOfCircle * float(totalCrimeInCity) / cityArea
        safetyRatio = crimeCountInRadius / N
        
        if(safetyRatio > 2):
            safetyScore = 1
        elif(1 < safetyRatio and safetyRatio < 2):
            safetyScore = 2
        elif(0.5 < safetyRatio and safetyRatio < 1):
            safetyScore = 3
        elif(0.25 < safetyRatio and safetyRatio < 0.5):
            safetyScore = 4
        else:
            safetyScore = 5
    return {"safetyScore": safetyScore, "address": address, 
            "latitude": latitude, "longitude": longitude, "state": cityState, "radius": radius, "unit": radiusUnit}

@application.route('/graphResults', methods=['GET', 'POST'])
@application.route('/graphResults/<city>', methods=['GET', 'POST'])
def graphResults(city=None):
    # print(request.args.getlist('city'))
    if request.method == 'POST':
        print('Incoming..')
        print(request.get_json()) 
        return ("Nothing") # parse as JSON
    
    else:
        # cursor = mysql.get_db().cursor()

        # if(city!=None):

            
        print(city)
        print(city)
            
            # return fig1.to_html(full_html=False, include_plotlyjs=False)
        return [sunGraph(city)[0], lineGraph(city)[0], barGraph(city)[0]]
        

@application.route('/sunGraph', methods=['GET', 'POST'])
@application.route('/sunGraph/city=<city>year=<year>', methods=['GET', 'POST'])
def sunGraph(city=None, year=None):
    if request.method == 'POST':
        print('Incoming..')
        print(request.get_json()) 
        return ("Nothing") # parse as JSON
    
    else:
        cursor = mysql.get_db().cursor()



        cityString="('"+city+"')"
        if(year==None or year is None):
            cursor.execute("SELECT * FROM SeniorDesign.CrimeTypeTotals WHERE city IN "+cityString)
        else:
            year=year.split(",")
            yearString=getSQLString(year)
            cursor.execute("SELECT * FROM SeniorDesign.CrimeTypeTotals WHERE city IN "+cityString+" AND year IN "+yearString)
        cityTypeData = cursor.fetchall()

        df = pd.DataFrame(cityTypeData, columns=["id", "city", "homicide", "agg_assault", "rape", "robbery", "violent", "theft", "burglary", "arson", "property", "other", "total", "year", "vehicle_theft"])
        agg_functionsSun = {'homicide': 'sum', "agg_assault": 'sum', "rape": 'sum', "robbery": 'sum', "violent": 'sum', "theft": 'sum', "burglary": 'sum', "arson": 'sum', "property": 'sum', "other": 'sum', "total": 'sum', "year": 'first', "vehicle_theft": 'sum'}

        dfSunTotal = df.groupby(df['city']).aggregate(agg_functionsSun)
        specificCrime = ["", "Theft", "Burglary", "Arson", "Vehicle Theft",
                "Homicide", "Aggravated Assault", "Rape", "Robbery"]
        generalCrime = ["Other", "Property", "Property", "Property", "Property",
                "Violent", "Violent", "Violent", "Violent"]
        crimeCount = [dfSunTotal['other'][0], dfSunTotal['theft'][0], dfSunTotal['burglary'][0], dfSunTotal['arson'][0], dfSunTotal['vehicle_theft'][0], dfSunTotal['homicide'][0], dfSunTotal['agg_assault'][0], dfSunTotal['rape'][0], dfSunTotal['robbery'][0]]
        print(crimeCount)
        dfSunburst = pd.DataFrame(
            dict(SpecificCrime=specificCrime, GeneralCrime=generalCrime, CrimeCount=crimeCount)
        )
        fig = px.sunburst(dfSunburst, path=['GeneralCrime', 'SpecificCrime'], values='CrimeCount')
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        return [graphJSON]
    
@application.route('/lineGraph', methods=['GET', 'POST'])
@application.route('/lineGraph/city=<city>compcity=<cityComp>', methods=['GET', 'POST'])
def lineGraph(city=None, compCity=None):
    if request.method == 'POST':
        print('Incoming..')
        print(request.get_json()) 
        return ("Nothing") # parse as JSON
    
    else:
        cursor = mysql.get_db().cursor()
        if(compCity==None or compCity is None):
            cityString="('"+city+"')"
        else:
            cityList=[city, compCity]
            cityString=getSQLString(cityList)
        

        cursor.execute("SELECT * FROM SeniorDesign.CrimeTypeTotals WHERE city IN "+cityString)
        cityData = cursor.fetchall()

        df = pd.DataFrame(cityData, columns=["id", "city", "homicide", "agg_assault", "rape", "robbery", "violent", "theft", "burglary", "arson", "property", "other", "total", "year", "vehicle_theft"])


        # agg_functionsLine = {'homicide': 'sum', "agg_assault": 'sum', "rape": 'sum', "robbery": 'sum', "violent": 'sum', "theft": 'sum', "burglary": 'sum', "arson": 'sum', "property": 'sum', "other": 'sum', "total": 'sum', "vehicle_theft": 'sum'}

        # dfLineChart = df.groupby(df['year']).aggregate(agg_functionsLine)
        # print(dfLineChart)
        plotDF=df[['city', 'total', 'year']].copy()
        plotDF=plotDF.sort_values(by='year')


        fig = px.line(plotDF, x='year', y='total', title="count of crimes per year", color='city')

        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        # return fig1.to_html(full_html=False, include_plotlyjs=False)
        return [graphJSON]
    

@application.route('/barGraph', methods=['GET', 'POST'])
@application.route('/barGraph/city=<city>compcity=<cityComp>', methods=['GET', 'POST'])
def barGraph(city=None):
    if request.method == 'POST':
        print('Incoming..')
        print(request.get_json()) 
        return ("Nothing") # parse as JSON
    
    else:
        cursor = mysql.get_db().cursor()
        
        cursor.execute("SELECT * FROM SeniorDesign.CrimeTypeTotals")
        cityData = cursor.fetchall()

        df = pd.DataFrame(cityData, columns=["id", "city", "homicide", "agg_assault", "rape", "robbery", "violent", "theft", "burglary", "arson", "property", "other", "total", "year", "vehicle_theft"])


        agg_functionsLine = {'homicide': 'sum', "agg_assault": 'sum', "rape": 'sum', "robbery": 'sum', "violent": 'sum', "theft": 'sum', "burglary": 'sum', "arson": 'sum', "property": 'sum', "other": 'sum', "total": 'sum', "vehicle_theft": 'sum'}

        dfLineChart = df.groupby(df['city']).aggregate(agg_functionsLine).reset_index()
        # plotDF=dfLineChart[['city', 'total', 'year']].copy()
        print(dfLineChart)
        color_discrete_map = {city: 'rgb(0,255,0)'}

        fig = px.bar(dfLineChart, x="city", y="total", title="Amount of Crimes in each City", color="city", color_discrete_map=color_discrete_map, color_discrete_sequence=['blue'])
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        # return fig1.to_html(full_html=False, include_plotlyjs=False)
        return [graphJSON]

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
        cursor.execute("SELECT City, Year(Date) as Year, Latitude, Longitude FROM SeniorDesign.CrimeData WHERE Year(Date) IN "+yearString+" AND City IN "+cityString)
        # cursor.execute("SELECT * FROM CrimeData WHERE Year(Date) IN "+yearString+" AND City IN "+cityString+" LIMIT 10000")
        cityData = cursor.fetchall()

        cursor.execute("SELECT latitude, longitude FROM SeniorDesign.CityInformation WHERE city="+cityString+";")
        startingPoint = cursor.fetchall()

        df = pd.DataFrame(cityData, columns=["city", "year", "latitude", "longitude"])
        if(len(startingPoint) > 0):
            mapObj = folium.Map([startingPoint[0][0], startingPoint[0][1]], zoom_start=11)
        else:
            mapObj = folium.Map([39.9526, -75.1652], zoom_start=9)
        data = []
        temp = df.to_numpy()
        for x in temp:
            if((x[2] is not None) and (x[3] is not None) and (isinstance(x[2], float)) and (isinstance(x[3], float)) and (not np.isnan(x[2])) and (not np.isnan(x[3]))):
                if(abs(startingPoint[0][0]-x[2])<1 and abs(startingPoint[0][1]-x[3])<1):
                    data.append([x[2], x[3], 3])
        # for x in data:
        #     print(x)

        HeatMap(data, gradient={.25: 'blue', .50: 'green', .75:'yellow', 1:'red'}, max_zoom=10, min_opacity=.25, max=1.0).add_to(mapObj)
        return mapObj._repr_html_()

    else:
        mapObj = folium.Map([39.9526, -75.1652], zoom_start=9)
        data = []
        return mapObj._repr_html_()

@application.route('/crime/heatmap', methods=['GET', 'POST'])
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

        return render_template('crimeAnalysis.html', cities=citiesSelect, years=yearsSelect)


if __name__ == "__main__":
    application.run(port=2000, debug=True)