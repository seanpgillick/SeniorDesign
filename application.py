from tokenize import String
from turtle import circle, color
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
from flask_caching import Cache
import random

application = Flask(__name__,static_folder='html') # This needs to be named `application`


#   host: "seniordesign-db.cxwhjsfccgui.us-east-1.rds.amazonaws.com",
#   port: "3306",
#   user: "admin",
#   password: "password!",

# https://flask-mysqldb.readthedocs.io/en/latest/
application.config['CACHE_TYPE'] = "SimpleCache"
application.config['MYSQL_DATABASE_HOST'] = "seniordesign-db.cxwhjsfccgui.us-east-1.rds.amazonaws.com"
application.config['MYSQL_DATABASE_USER'] = "admin"
application.config['MYSQL_DATABASE_PASSWORD'] = "password!"
application.config['MYSQL_DATABASE_DB'] = "SeniorDesign"
application.config['MYSQL_DATABASE_PORT'] = 3306
mysql = MySQL()
cache = Cache()
mysql.init_app(application)
cache.init_app(application)
# cursor = mysql.get_db().cursor()

primary_color= '#f5b611'
dark_color = '#21252f'

@application.route('/')
@cache.cached(timeout=3600)
def index():
    cursor = mysql.get_db().cursor()
    cursor.execute("SELECT city, state FROM SeniorDesign.CityInformation")
    citiesSQL=cursor.fetchall()
    return render_template("index.html", cities=citiesSQL)

def getSQLString(cityList):
    cityString="("
    for i in cityList:
        cityString=cityString+"'"+i+"', "
    cityString=cityString[:-2]+")"
    return cityString


@application.route('/mapUpdate/')
def mapLoad(city=None):
    city=request.args.get('city')
    cityInfo=getHeatMapDrops(city)
    return render_template("crimeAnalysis.html", years=cityInfo['years'], cities=cityInfo['cities'], tab="heatmap", city=city)


@application.route('/analysis/<city>/<tab>', methods=["GET", "POST"])
def crimeAnalysis(city=None, tab=None):
    cursor = mysql.get_db().cursor()
    cursor.execute("SELECT city, state FROM SeniorDesign.CityInformation;")
    citiesSQL=cursor.fetchall()
    
    if(tab=="data"):
        jsonData=graphResults(city)
        cityInfo=getDataDrops(city)
        return render_template("crimeAnalysis.html", graph1JSON=jsonData[0], graph2JSON=jsonData[1], graph3JSON=jsonData[2], years=cityInfo['years'], cities=cityInfo['cities'], tab="data", city=city, citiesSelect=citiesSQL)
    elif(tab=="heatmap"):
        cityInfo=getHeatMapDrops(city)
        return render_template('crimeAnalysis.html', years=cityInfo['years'], tab="heatmap", city=city, citiesSelect=citiesSQL)
    elif(tab=="crimelist"):
        df=getCrimeList(city)
        return render_template("crimeAnalysis.html", tab="crimelist", city=city, crimeData=np.array(df), citiesSelect=citiesSQL)
    elif(tab=="safety"):
        cityInfo = safetyScore(city)

        return render_template('crimeAnalysis.html', safetyScore=cityInfo["safetyScore"], status=cityInfo["status"],
                                address=cityInfo["address"], latitude=cityInfo["latitude"], longitude=cityInfo["longitude"], 
                                state=cityInfo["state"], city=city, tab="safety", radius=cityInfo["radius"], unit=cityInfo["unit"],
                                cityLat=cityInfo["cityLat"], cityLng=cityInfo["cityLng"], scoresByYear=cityInfo["scoresByYear"],
                                graph=cityInfo["graph"], citiesSelect=citiesSQL)


    return render_template("crimeAnalysis.html")

@application.route('/analysis/<city>/<tab>/enhanceGraphs/pieYears=<pieYears>')
@application.route('/analysis/<city>/<tab>/enhanceGraphs/compCity=<compCity>')
@application.route('/analysis/<city>/<tab>/enhanceGraphs/pieYears=<pieYears>compCity=<compCity>')
def dataGraphsUpdate(city=None, tab=None, pieYears=None, compCity=None):
    jsonData=graphResults(city)
    cityInfo=getDataDrops(city)
    if(pieYears!=None and pieYears!="None"):
        graph1JSON=sunGraph(city, pieYears)[0]
    else:
        print('HERE 5')
        graph1JSON=jsonData[0]
    if(compCity!=None):
        print("ARE YOU HERE")
        graph2JSON=lineGraph(city, compCity)[0]
    else:
        graph2JSON=jsonData[1]
    graph3JSON=jsonData[2]

    return render_template("crimeAnalysis.html", graph1JSON=graph1JSON, graph2JSON=graph2JSON, graph3JSON=graph3JSON, years=cityInfo['years'], pieYears=pieYears, compCity=compCity, cities=cityInfo['cities'], tab="data", city=city)


@application.route('/cityDrops', methods=['GET', 'POST'])
@application.route('/cityDropscity=<city>year=<year>', methods=['GET', 'POST'])
@cache.memoize(timeout=86400)
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
        cursor.execute("SELECT * FROM SeniorDesign.CrimeData WHERE city IN "+cityString+" LIMIT 10")
        crimeSQL=cursor.fetchall()
        df = pd.DataFrame(crimeSQL, columns=["id", "city", "state", "offense", "crime_type", "date", "latitude", "longitude"])
        plotDF=df[['id', 'offense', 'crime_type', 'date']].copy()


        return plotDF
    
@application.route('/cityDrops', methods=['GET', 'POST'])
@application.route('/cityDropscity=<city>year=<year>', methods=['GET', 'POST'])
@cache.memoize(timeout=86400)
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
def safetyScore(city):
    latitude = request.args.get('latitude') 
    longitude = request.args.get('longitude')
    radius = request.args.get('radius')
    city = city
    address = request.args.get('address')
    radiusUnit = request.args.get('unit') or "mi"
    safetyScore = None
    overalSafetyScore = None
    safetyScoresByYear = None
    cityState = ""
    cursor = mysql.get_db().cursor()
    cursor.execute("SELECT latitude, longitude FROM SeniorDesign.CityInformation WHERE city='"+city+"';")
    cityLatLng = cursor.fetchall()
    cityLat = cityLatLng[0][0]
    cityLng = cityLatLng[0][1]
    graphJSON = None
    splitAddress = []
    if(address is not None):
        splitAddress = address.split(',')

    if(address and latitude and longitude and radius):
        if(not (abs(float(latitude)-cityLat)<1 and abs(float(longitude)-cityLng)<1) or not(splitAddress[1].strip() == city)):
            return {"safetyScore": overalSafetyScore, "address": address, "status": "failed",
            "latitude": latitude, "longitude": longitude, "state": cityState, "radius": radius, "unit": radiusUnit,
            "cityLat": cityLat, "cityLng": cityLng, "scoresByYear": safetyScoresByYear, "graph": graphJSON}
        
        # Get crimes withing selected area 
        if(radiusUnit == "km"):
            kmRadius = float(radius) * 0.621371
        else:
            kmRadius = float(radius) 

        areaOfCircle = math.pi*(float(kmRadius) ** 2)

        # Get city total crimes and total number of crimes
        cursor = mysql.get_db().cursor()
        cursor.execute("""SELECT ctt.year, ctt.total, ci.area, ci.state, ci.latitude, ci.longitude
                            FROM SeniorDesign.CrimeTypeTotals ctt
                            INNER JOIN SeniorDesign.CityInformation ci 
                                ON ci.city = ctt.city
                            WHERE ctt.city='{}';""".format(city))
        
        cityInformation = cursor.fetchall()
        cityArea = cityInformation[0][2]
        cityState = cityInformation[0][3]

        totalCrimeCountsByYear=[]
        safetyScoresByYear = {"years": [], "scores": []}
        totalCrimeCount = 0

        sqlQuery = "SELECT COUNT(*) as total"
        for yearInfo in cityInformation:
            currentYear = yearInfo[0]
            totalCrimeCountsByYear += [yearInfo[1]]
            totalCrimeCount += yearInfo[1]
            safetyScoresByYear["years"] += [currentYear]
            sqlQuery += ",COUNT(IF(Year(date)='{}',1,null)) as `{}`".format(currentYear, currentYear)
            
            # cursor.execute("SELECT latitude, longitude FROM SeniorDesign.CrimeData WHERE city='"+city+"' AND YEAR(date)='"+currentYear+"' AND SQRT(POW("+latitude+" - latitude , 2) + POW("+longitude+" - longitude, 2)) * 100 < "+str(kmRadius)+"")

        sqlQuery += "FROM SeniorDesign.CrimeData WHERE city='"+city+"' AND SQRT(POW("+latitude+" - latitude , 2) + POW("+longitude+" - longitude, 2)) * 100 < "+str(kmRadius)
        cursor.execute(sqlQuery)

        crimeCountInfo = cursor.fetchall()
        crimeCountInfo = crimeCountInfo[0]
        for i in range(len(crimeCountInfo)):
            #calculate overall safety score
            # Calculate safety score
            if(i == 0):
                N = areaOfCircle * float(totalCrimeCount) / cityArea
            else:
                N = areaOfCircle * float(totalCrimeCountsByYear[i-1]) / cityArea
            safetyRatio = crimeCountInfo[i] / N
            if(safetyRatio > 2):
                tempSafetyScore = 1
            elif(1 < safetyRatio and safetyRatio < 2):
                tempSafetyScore = 2
            elif(0.5 < safetyRatio and safetyRatio < 1):
                tempSafetyScore = 3
            elif(0.25 < safetyRatio and safetyRatio < 0.5):
                tempSafetyScore = 4
            else:
                tempSafetyScore = 5
            if(i == 0):
                overalSafetyScore =  tempSafetyScore
            else:
                safetyScoresByYear["scores"] += [tempSafetyScore]

        safetyScoreDf = pd.DataFrame.from_dict(safetyScoresByYear)
        fig = px.line(safetyScoreDf, x='years', y='scores', title="Safety score over the years")
        fig.update_layout(yaxis_range=[0,5])

        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return {"safetyScore": overalSafetyScore, "address": address, "status":"passed",
            "latitude": latitude, "longitude": longitude, "state": cityState, "radius": radius, "unit": radiusUnit,
            "cityLat": cityLat, "cityLng": cityLng, "scoresByYear": safetyScoresByYear, "graph": graphJSON}

@application.route('/graphResults', methods=['GET', 'POST'])
@application.route('/graphResults/<city>', methods=['GET', 'POST'])
@cache.memoize(timeout=86400)
def graphResults(city=None):
    # print(request.args.getlist('city'))
    if request.method == 'POST':
        print('Incoming..')
        print(request.get_json()) 
        return ("Nothing") # parse as JSON
    
    else:
        # cursor = mysql.get_db().cursor()

        # if(city!=None):
            
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
        dfSunburst = pd.DataFrame(
            dict(SpecificCrime=specificCrime, GeneralCrime=generalCrime, CrimeCount=crimeCount)
        )
        fig = px.sunburst(dfSunburst, path=['GeneralCrime', 'SpecificCrime'], values='CrimeCount')
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            
        )
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
        print(city)
        print(compCity)
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


        fig = px.line(plotDF, x='year', y='total', title="Total Numbers of Crimes per Year", color='city')
        fig.update_traces(line_color=primary_color, line_width=2)
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
        yearSearch="('2019', '2020', '2021')"

        cursor.execute("SELECT * FROM SeniorDesign.CrimeTypeTotals WHERE year IN "+yearSearch)
        cityData = cursor.fetchall()

        df = pd.DataFrame(cityData, columns=["id", "city", "homicide", "agg_assault", "rape", "robbery", "violent", "theft", "burglary", "arson", "property", "other", "total", "year", "vehicle_theft"])

        agg_functionsLine = {'homicide': 'sum', "agg_assault": 'sum', "rape": 'sum', "robbery": 'sum', "violent": 'sum', "theft": 'sum', "burglary": 'sum', "arson": 'sum', "property": 'sum', "other": 'sum', "total": 'sum', "vehicle_theft": 'sum'}

        dfLineChart = df.groupby(df['city']).aggregate(agg_functionsLine).reset_index()
        # plotDF=dfLineChart[['city', 'total', 'year']].copy()
        color_discrete_map = {city: primary_color}

        fig = px.bar(dfLineChart, x="city", y="total", color="city", color_discrete_map=color_discrete_map, color_discrete_sequence=[dark_color])
        fig.update_layout(
            xaxis_title="Cities",
            yaxis_title="Num. of Crimes (2019-2021)",
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis={'categoryorder':'total ascending'}
        )
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        # return fig1.to_html(full_html=False, include_plotlyjs=False)
        return [graphJSON]

@application.route('/mapGenSafetyScorecity=<city>lat=<lat>lng=<lng>radius=<radius>unit=<unit>', methods=['GET', 'POST'])
def safetyScoreMapGen(city, lat, lng, radius, unit):
    # Get crimes withing selected area 
    if(unit == "km"):
        kmRadius = float(radius) * 0.621371
    else:
        kmRadius = float(radius) 

    cursor = mysql.get_db().cursor()
    cursor.execute("SELECT latitude, longitude, crime_type FROM SeniorDesign.CrimeData WHERE city='"+city+"' AND SQRT(POW("+lat+" - latitude , 2) + POW("+lng+" - longitude, 2)) * 100 < "+str(kmRadius)+"")

    totalCrimeLatLng = cursor.fetchall()

    colorDict = {
        "VIOLENT": "Red",
        "PROPERTY": "Blue",
        "OTHER": "Yellow"
    }
    #heat map
    lgd_txt = '<span style="color: {col};">{txt}</span>'
    fgR = folium.FeatureGroup(name= lgd_txt.format( txt= 'VIOLENT', col= 'red'))
    fgB = folium.FeatureGroup(name= lgd_txt.format( txt= 'PROPERTY', col= 'blue'))
    fgY = folium.FeatureGroup(name= lgd_txt.format( txt= 'OTHER', col= 'yellow'))
    mapObj = folium.Map([lat, lng], zoom_start=16)
    for point in totalCrimeLatLng:
        if((point[0] is not None) and (point[1] is not None) and (isinstance(point[0], float)) and (isinstance(point[1], float)) and (not np.isnan(point[0])) and (not np.isnan(point[1]))):
            colorpoint = folium.Circle(
                location=[point[0], point[1]],
                popup=point[2],
                radius = 10,
                fill = True,
                fill_opacity = 1, 
                fill_color = colorDict.get(point[2]),
                color = colorDict.get(point[2])
            )
        if (colorDict.get(point[2])=="Red"):
            fgR.add_child(colorpoint)
        elif (colorDict.get(point[2])=="Blue"):
            fgB.add_child(colorpoint)
        else:
            fgY.add_child(colorpoint)

    mapObj.add_child(fgR)
    mapObj.add_child(fgB)
    mapObj.add_child(fgY)

    folium.map.LayerControl('topleft', collapsed= False).add_to(mapObj)

    # HeatMap(data, gradient={.25: 'blue', .50: 'green', .75:'yellow', 1:'red'}, max_zoom=20, min_opacity=.25, max=1.0).add_to(mapObj)
    
    return mapObj._repr_html_()

@application.route('/mapGenSafetyLabelcity=<city>lat=<lat>lng=<lng>radius=<radius>unit=<unit>', methods=['GET', 'POST'])
def safetyScoreLabel(city, lat, lng, radius, unit):
    # Get crimes withing selected area 
    if(unit == "km"):
        kmRadius = float(radius) * 0.621371
    else:
        kmRadius = float(radius) 

    cursor = mysql.get_db().cursor()
    cursor.execute("SELECT latitude, longitude FROM SeniorDesign.CrimeData WHERE city='"+city+"' AND SQRT(POW("+lat+" - latitude , 2) + POW("+lng+" - longitude, 2)) * 100 < "+str(kmRadius)+"")

    totalCrimeLatLng = cursor.fetchall()

    cursor.execute("SELECT crime_type FROM SeniorDesign.CrimeData WHERE city='"+city+"' AND SQRT(POW("+lat+" - latitude , 2) + POW("+lng+" - longitude, 2)) * 100 < "+str(kmRadius)+"")
    crimeTypes = cursor.fetchall()

    #heat map
    mapObj = folium.Map([lat, lng], zoom_start=16)
    circleRad = kmRadius * 1010

    violent = 0
    property = 0
    other = 0

    # data = []
    # for point in totalCrimeLatLng:
    #     if((point[0] is not None) and (point[1] is not None) and (isinstance(point[0], float)) and (isinstance(point[1], float)) and (not np.isnan(point[0])) and (not np.isnan(point[1]))):
    #         data.append([point[0], point[1], 3])

    for crime in crimeTypes:
        if(crime[0] == "PROPERTY"):
            property+=1
        elif(crime[0] == "VIOLENT"):
            violent+=1
        else:
            other+=1

    circleObj = folium.Circle(
        radius = circleRad,
        location = [lat, lng],
        color='blue',
        fill=False,)

    latChange = (kmRadius/3)/110.574
    longChange = (kmRadius/1.3)/111.320*math.cos(float(lat))

    folium.Circle(location=[float(lat)+latChange,float(lng)+longChange], radius = float(circleRad)/3, popup=("Property: " + str(property)), color='Blue', fill_opacity=.50, fill_color='Blue').add_to(mapObj)
    folium.Circle(location=[float(lat)+latChange,float(lng)-longChange], radius = float(circleRad)/3, popup=("Violent: " + str(violent)), color='Red', fill_opacity=.50, fill_color='Red').add_to(mapObj)
    folium.Circle(location=[float(lat)-latChange,float(lng)], radius = float(circleRad)/3, popup=("Other: " + str(other)), color='Yellow', fill_opacity=.50, fill_color='Yellow').add_to(mapObj)
    circleObj.add_to(mapObj)

    # HeatMap(data, gradient={.25: 'blue', .50: 'green', .75:'yellow', 1:'red'}, max_zoom=20, min_opacity=.25, max=1.0).add_to(mapObj)
    
    return mapObj._repr_html_()



@application.route('/mapGencity=<city>year=<year>crime=<crime>', methods=['GET', 'POST'])
@cache.memoize(timeout=86400)
def heatmapGen(city, year, crime):
    cursor = mysql.get_db().cursor()
    cityList = []
    cityList.append(city)
    yearList = []
    yearList.append(year)
    crimeList = []
    crimeList.append(crime)
    if(cityList!=[] and yearList!=[]):
        queryString=""
        yearString="("
        cityString="("
        crimeString="("
        for i in yearList:
            yearString=yearString+"'"+i+"', "
        for i in cityList:
            cityString=cityString+"'"+i+"', "
        for i in crimeList:
            crimeString=crimeString+"'"+i+"', "
        cityString=cityString[:-2]+")"
        yearString=yearString[:-2]+")"
        crimeString=crimeString[:-2]+")"

        if(yearString=="('All')"):
            queryString += "SELECT City, Year(Date) as Year, Latitude, Longitude FROM SeniorDesign.CrimeData WHERE City = "+cityString
        else:
            queryString += "SELECT City, Year(Date) as Year, Latitude, Longitude FROM SeniorDesign.CrimeData WHERE Year(Date) IN "+yearString+" AND City IN "+cityString
        
        if(not crimeString=="('All')"):
            queryString += "AND crime_type IN" +crimeString
        

        cursor.execute(queryString)
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

        if(len(data)<1):
            htmlCode = '<html><br><h3 style="text-align: center">Failed to retrieve location data for ' + cityString + '</h3></html>'
            return htmlCode

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
        cursor.execute("SELECT Year(Date) AS Year FROM SeniorDesign.CrimeData GROUP BY Year(Date)"),
        yearsSQL=cursor.fetchall()
        cursor.execute("SELECT Offense FROM SeniorDesign.CrimeData GROUP BY Offense"),
        offensesSQL=cursor.fetchall()
        yearsSelect=[]
        citiesSelect=[]
        offenses=[]
        for i in yearsSQL:
            yearsSelect.append(i[0])

        for i in offensesSQL:
            offenses.append(i[0])

        return render_template('crimeAnalysis.html', years=yearsSelect, crimes=offenses)


if __name__ == "__main__":
    application.run(port=2000, debug=True)