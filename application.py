from tokenize import String
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
from folium.features import DivIcon
from folium.plugins import MarkerCluster
import markupsafe
import numpy as np
import math
from flask_caching import Cache
import random
import plotly.io as pio
import branca.colormap as branca_folium_cm


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
current_template = 'simple_white'
graph_height = 300

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
        cityListInfo=crimeList(city)
        crimeRates=calcCrimeRates(city)
        return render_template("crimeAnalysis.html", graph1JSON=jsonData[0], graph2JSON=jsonData[1], graph3JSON=jsonData[2], years=cityInfo['years'], cities=cityInfo['cities'], graph4JSON=crimeRates[1], crimeRates=crimeRates[0], violentPercent=crimeRates[2], propertyPercent=crimeRates[3], otherPercent=crimeRates[4], crimeData=np.array(cityListInfo['data']), pageNumber=cityListInfo['pageNumber'], pages=cityListInfo['pages'], tab="data", city=city, citiesSelect=citiesSQL)
    elif(tab=="heatmap"):
        cityInfo=getHeatMapDrops(city)
        return render_template('crimeAnalysis.html', years=cityInfo['years'], tab="heatmap", city=city, citiesSelect=citiesSQL)
    elif(tab=="safety"):
        cityInfo = safetyScore(city)

        return render_template('crimeAnalysis.html', safetyScore=cityInfo["safetyScore"], status=cityInfo["status"],
                                address=cityInfo["address"], latitude=cityInfo["latitude"], longitude=cityInfo["longitude"], 
                                state=cityInfo["state"], city=city, tab="safety", radius=cityInfo["radius"], unit=cityInfo["unit"],
                                cityLat=cityInfo["cityLat"], cityLng=cityInfo["cityLng"], scoresByYear=cityInfo["scoresByYear"],
                                graph=cityInfo["graph"], citiesSelect=citiesSQL)


    return render_template("crimeAnalysis.html")

""" @application.route('/analysis/<city>/<tab>/enhanceGraphs/pieYears=<pieYears>')
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
 """
@application.route('/analysis/<city>/<tab>/enhanceGraphs/pieYears=<pieYears>',methods=['GET'])
@application.route('/analysis/<city>/<tab>/enhanceGraphs/compCity=<compCity>',methods=['GET'])
@application.route('/analysis/<city>/<tab>/enhanceGraphs/pieYears=<pieYears>compCity=<compCity>',methods=['GET'])
def dataGraphsUpdate(city=None, tab=None, pieYears=None, compCity=None):
    graph1JSON = None
    if(pieYears!=None and pieYears!="None"):
        graph1JSON=sunGraph(city, pieYears)[0]
    
    if(compCity!=None):
        graph1JSON=lineGraph(city, compCity)[0]

    if(compCity=="Yearly" ):
        graph1JSON=lineGraph(city, None)[0]
    
    return graph1JSON


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
    
# @application.route('/crimeList', methods=['GET', 'POST'])
# @application.route('/crimeListcity=<city>year=<year>', methods=['GET', 'POST'])
# def getCrimeList(city=None, year=None):
#     if request.method == 'POST':
#         print('Incoming..')
#         print(request.get_json()) 
#         return ("Nothing") # parse as JSON
    
#     else:
#         cursor = mysql.get_db().cursor()
#         cityString=getSQLString([city])
#         cursor.execute("SELECT * FROM SeniorDesign.CrimeData WHERE city IN "+cityString+" LIMIT 10")
#         crimeSQL=cursor.fetchall()
#         df = pd.DataFrame(crimeSQL, columns=["id", "city", "state", "offense", "crime_type", "date", "latitude", "longitude"])
#         plotDF=df[['id', 'offense', 'crime_type', 'date']].copy()


#         return plotDF
    
@application.route('/crimeList', methods=['GET', 'POST'])
@application.route('/crimeList/city=<city>year=<year>', methods=['GET', 'POST'])
@application.route('/crimeList/city=<city>pageNumber=<pageNumber>', methods=['GET', 'POST'])
@application.route('/crimeList/city=<city>year=<year>pageNumber=<pageNumber>', methods=['GET', 'POST'])
def crimeList(city=None, year=None, pageNumber=0):
    if request.method == 'POST':
        print('Incoming..')
        print(request.get_json()) 
        return ("Nothing") # parse as JSON
    
    else:
        # pageNumber=0
        if(request.args.get('pageNumber')):
            pageNumber = request.args.get('pageNumber')
        cursor = mysql.get_db().cursor()
        cityString=getSQLString([city])
        offsetNum=int(pageNumber)*25
        cursor.execute("SELECT * FROM SeniorDesign.CrimeData WHERE city IN "+cityString+" LIMIT 25 OFFSET "+str(offsetNum))
        crimeSQL=cursor.fetchall()
        cursor.execute("SELECT COUNT(*) as count_pet FROM SeniorDesign.CrimeData WHERE city IN "+cityString)
        crimeCount=cursor.fetchall()
        df = pd.DataFrame(crimeSQL, columns=["id", "city", "state", "offense", "crime_type", "date", "latitude", "longitude"])
        df.insert(0, 'row_no', range(offsetNum+1, offsetNum+1 + len(df)))
        plotDF=df[['row_no', 'offense', 'crime_type', 'date']].copy()
        plotDF['date']=plotDF['date'].astype(str)

        numOfPages=int(crimeCount[0][0]/25)

        print("Pages"+str(pageNumber))

        return {"data": plotDF, "pageNumber":int(pageNumber), "pages":numOfPages}
    
@application.route('/crimeListSpec', methods=['GET', 'POST'])
@application.route('/crimeListSpec/city=<city>pageNumber=<pageNumber>', methods=['GET', 'POST'])
def crimeListSpec(city=None, pageNumber=0):
    if request.method == 'POST':
        print('Incoming..')
        print(request.get_json()) 
        return ("Nothing") # parse as JSON
    
    else:
        # pageNumber=0
        print("HIIIII")
        if(request.args.get('pageNumber')):
            pageNumber = request.args.get('pageNumber')
        cursor = mysql.get_db().cursor()
        cityString=getSQLString([city])
        offsetNum=int(pageNumber)*25
        cursor.execute("SELECT * FROM SeniorDesign.CrimeData WHERE city IN "+cityString+" LIMIT 25 OFFSET "+str(offsetNum))
        crimeSQL=cursor.fetchall()
        cursor.execute("SELECT COUNT(*) as count_pet FROM SeniorDesign.CrimeData WHERE city IN "+cityString)
        crimeCount=cursor.fetchall()
        df = pd.DataFrame(crimeSQL, columns=["id", "city", "state", "offense", "crime_type", "date", "latitude", "longitude"])
        df.insert(0, 'row_no', range(offsetNum+1, offsetNum+1 + len(df)))
        plotDF=df[['row_no', 'offense', 'crime_type', 'date']].copy()
        plotDF['date']=plotDF['date'].astype(str)

        numOfPages=int(crimeCount[0][0]/25)
        print(plotDF.to_json())

        return {"data": plotDF.to_json(), "pageNumber":int(pageNumber), "pages":numOfPages}
    
@application.route('/calcCrimeRates/<city>', methods=['GET', 'POST'])
def calcCrimeRates(city):
    # print(request.args.getlist('city'))
    if request.method == 'POST':
        print('Incoming..')
        print(request.get_json()) 
        return ("Nothing") # parse as JSON
    
    else:
        cursor = mysql.get_db().cursor()
        cityString="('"+city+"')"
        cursor.execute("SELECT * FROM SeniorDesign.CityPopulations WHERE city IN "+cityString)
        cityPopData = cursor.fetchall()
        df_pop = pd.DataFrame(cityPopData, columns=["id", "city", "state", "population", "year"])

        cursor.execute("SELECT * FROM SeniorDesign.CrimeTypeTotals WHERE city IN "+cityString)
        cityCrimeData = cursor.fetchall()
        df_crime = pd.DataFrame(cityCrimeData, columns=["id", "city", "homicide", "agg_assault", "rape", "robbery", "violent", "theft", "burglary", "arson", "property", "other", "total", "year", "vehicle_theft"])
        crimeRates=[]
        total=0
        violentPercent=0
        propertyPercent=0
        otherPercent=0
        counter=0
        for index, row in df_pop.iterrows():
            counter+=1
            crimecount=(df_crime.loc[df_crime['year'] == row['year']])['total'].values[0]
            crimeRates.append({"year":row['year'], "rate":round((crimecount/row['population'])*100, 2)})

            total+=crimecount/row['population']
            

        for index, row in df_crime.iterrows():
            violentPercent+=row['violent']/row['total']
            propertyPercent+=row['property']/row['total']
            otherPercent+=row['other']/row['total']
        violentPercent=round((violentPercent/counter)*100, 2)
        propertyPercent=round((propertyPercent/counter)*100, 2)
        otherPercent=round((otherPercent/counter)*100, 2)

        crimeRates.append({"year": 'total', "rate": round(total/len(crimeRates)*100, 1)})

        df=pd.DataFrame(crimeRates[:3], columns=["year", "rate"])
        plotDF=df.sort_values(by='year')
        print(plotDF)

        fig = px.line(plotDF, x='year', y='rate')
        fig.update_traces(line_color=primary_color, line_width=2)
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        return [crimeRates, graphJSON, violentPercent, propertyPercent, otherPercent]
        
    
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
        fig = px.line(safetyScoreDf, x='years', y='scores', title="Safety score over the years",template=current_template,height=graph_height)
        fig.update_layout(yaxis_range=[0,5], xaxis={'showgrid' :True},
            yaxis={ 'showgrid' :True},margin=dict(l=20, r=20, t=30, b=20))

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

        # fig = px.sunburst(dfSunburst, path=['GeneralCrime', 'SpecificCrime'], values='CrimeCount', color="GeneralCrime", color_discrete_map={"Other":'gold', 'Violent':'red', 'Property':'blue'})
                #Shades of blue
            #Aqua - #00FFFF
            #Baby Blue - #89CFF0
            #Azure - #F0FFFF
            #Electric Blue - #7DF9FF
            #Royal Blue - #4169E1
        #Shades of Red
            #Blood Red - #880808
            #Brick red - #AA4A44
            #Bright Red - #EE4B2B
            #Burnt Orange - #CC5500
        
        # fig = px.sunburst(dfSunburst, path=['GeneralCrime', 'SpecificCrime'], values='CrimeCount', color="SpecificCrime", color_discrete_map={"":"gold", "Theft":"#00FFFF", "Burglary":"#89CFF0", "Arson":"#F0FFFF", "Vehicle Theft":"#7DF9FF", "Homicide": "#880808", "Aggravated Assault": "#AA4A44", "Rape": "#EE4B2B", "Robbery": "#CC5500"})
        fig = px.sunburst(dfSunburst, path=['GeneralCrime', 'SpecificCrime'], values='CrimeCount')
        color_mapping = {"Other":"gold", "Violent": "Red", "Property": "Blue", "":"gold", "Arson":"#3939FF", "Burglary":"#2B2BFF", "Vehicle Theft":"#1F1FFF", "Theft":"#1111FF",  "Homicide": "#FF4B4B", "Rape": "#FF3C3C", "Robbery": "#FF2828", "Aggravated Assault": "#FF1111", }

        fig.update_traces(marker_colors=[color_mapping[cat] for cat in fig.data[-1].labels])

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=25, b=20),
            
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


        fig = px.line(plotDF, x='year', y='total', color='city',template=current_template,height=graph_height)
        fig.update_layout( xaxis={'showgrid' :True},
            yaxis={ 'showgrid' :True}, margin=dict(l=20, r=20, t=30, b=20))
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

        fig = px.bar(dfLineChart, x="city", y="total", color="city", color_discrete_map=color_discrete_map, color_discrete_sequence=[dark_color],template=current_template,height=graph_height)
        fig.update_layout(
            xaxis_title="Cities",
            yaxis_title="Num. of Crimes (2019-2021)",
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis={'categoryorder':'total ascending',  'showgrid' :True},
            yaxis={ 'showgrid' :True},
            margin=dict(l=20, r=20, t=25, b=20),
           
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
    cursor.execute("SELECT crime_type, latitude, longitude FROM SeniorDesign.CrimeData WHERE city='"+city+"' AND SQRT(POW("+lat+" - latitude , 2) + POW("+lng+" - longitude, 2)) * 100 < "+str(kmRadius)+"")

    totalCrimeLatLng = cursor.fetchall()

    # cursor.execute("SELECT crime_type FROM SeniorDesign.CrimeData WHERE city='"+city+"' AND SQRT(POW("+lat+" - latitude , 2) + POW("+lng+" - longitude, 2)) * 100 < "+str(kmRadius)+"")
    # crimeTypes = cursor.fetchall()

    #heat map
    mapObj = folium.Map([lat, lng], zoom_start=14)
    circleRad = kmRadius * 1010

    violent = 0
    property = 0
    other = 0

    markerCluster = MarkerCluster(bame="Crimes").add_to(mapObj)

    for crime in totalCrimeLatLng:
        if(crime[0] == "PROPERTY"):
            folium.Marker(location=[crime[1], crime[2]], popup="Property", icon=folium.Icon(color="blue", icon="home")).add_to(markerCluster)
        elif(crime[0] == "VIOLENT"):
            folium.Marker(location=[crime[1], crime[2]], popup="Violent", icon=folium.Icon(color="red", icon="warning-sign")).add_to(markerCluster)
        else:
            folium.Marker(location=[crime[1], crime[2]], popup="Other", icon=folium.Icon(color="orange")).add_to(markerCluster)

    # Old display map

    # data = []
    # for point in totalCrimeLatLng:
    #     if((point[0] is not None) and (point[1] is not None) and (isinstance(point[0], float)) and (isinstance(point[1], float)) and (not np.isnan(point[0])) and (not np.isnan(point[1]))):
    #         data.append([point[0], point[1], 3])

    # circleObj = folium.Circle(
    #     radius = circleRad,
    #     location = [lat, lng],
    #     color='blue',
    #     fill=False,)

    # latChange = (kmRadius/3)/110.574
    # longChange = (kmRadius/1.3)/111.320*math.cos(float(lat))

    # folium.Circle(location=[float(lat)+latChange,float(lng)+longChange], radius = float(circleRad)/3, popup=("Property: " + str(property)), color='Blue', fill_opacity=.50, fill_color='Blue').add_to(mapObj)
    # folium.map.Marker(location=[float(lat)+latChange,float(lng)+longChange+((kmRadius/1.3)/111.320*math.cos(float(lat))*.25)], icon=DivIcon(icon_size=(40,40), icon_anchor=(4,14), html=f'<div style="font-size: 20pt;">%s</div>' % str(property))).add_to(mapObj)
    # folium.Circle(location=[float(lat)+latChange,float(lng)-longChange], radius = float(circleRad)/3, popup=("Violent: " + str(violent)), color='Red', fill_opacity=.50, fill_color='Red').add_to(mapObj)
    # folium.map.Marker(location=[float(lat)+latChange,float(lng)-longChange+((kmRadius/1.3)/111.320*math.cos(float(lat))*.25)], icon=DivIcon(icon_size=(40,40), icon_anchor=(4,14), html=f'<div style="font-size: 20pt;">%s</div>' % str(violent))).add_to(mapObj)
    # folium.Circle(location=[float(lat)-latChange,float(lng)], radius = float(circleRad)/3, popup=("Other: " + str(other)), color='Yellow', fill_opacity=.50, fill_color='Yellow').add_to(mapObj)
    # folium.map.Marker(location=[float(lat)-latChange,float(lng)+((kmRadius/1.3)/111.320*math.cos(float(lat))*.25)], icon=DivIcon(icon_size=(40,40), icon_anchor=(4,14), html=f'<div style="font-size: 20pt;">%s</div>' % str(other))).add_to(mapObj)
    # circleObj.add_to(mapObj)

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
        z_min = 0.25
        z_max = 1
        if(len(startingPoint) > 0):
            mapObj = folium.Map([startingPoint[0][0], startingPoint[0][1]], zoom_start=11)
            ## Add BRANCA colormap ##
            
            #colormap = branca_folium_cm.linear.Reds_05.scale(z_min, z_max)
            #colormap.caption = "Bla bla"  # how do I change fontsize and color here?
            colormap = branca_folium_cm.LinearColormap(colors=['blue','green', 'yellow','red'], 
                                                       caption = "Criminal Activity Legend",
                                                       vmin=0, vmax=100)
            mapObj.add_child(colormap)
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

#if __name__ == '__main__':
    #application.run(host='0.0.0.0', port=8080, debug=True)