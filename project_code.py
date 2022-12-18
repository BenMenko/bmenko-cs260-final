# !pip install geopandas
# !pip install folium
# !pip install mapclassify
# !pip install aspose-words
# !pip install statsmodels
# !pip install chart_studio
from google.colab import drive
drive.mount('/content/drive')
# system
import os, glob, sys
 # math
import numpy as np
import matplotlib.pyplot as plt
 # data
import pandas as pd
# mapping
import geopandas as gp
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio

# geopandas tools:
import folium 
import mapclassify
# convert html
import aspose.words as aw
from bs4 import BeautifulSoup as bs

# plotly api info for creating interactive map
import chart_studio
import chart_studio.plotly as py
import chart_studio.tools as tls

username = 'Bmenko' 
api_key = 'kKOloGiBdjiDuMpwi0kQ' 
chart_studio.tools.set_credentials_file(username=username, api_key=api_key)

# creating list of key locations and dict
list_of_countries = ['AUS', 'GRC', 'AUT', 
                     'BEL', 'CAN', 'CZE', 
                     'DNK', 'FIN', 'FRA', 
                     'DEU', 'HUN', 'ISL', 
                     'IRL', 'ITA', 'JPN', 
                     'KOR', 'LUX', 'MEX', 
                     'NLD', 'NZL', 'NOR', 
                     'POL', 'PRT', 'SVK', 
                     'ESP', 'SWE', 'CHE', 
                     'TUR', 'GBR', 'USA', 
                     'EST', 'ISR', 'SVN', 
                     'LVA', 'LTU']
# creating dict of location
coords =            {'AUS':[-30, 135], 'GRC':[38, 22], 'AUT':[47.5, 15], 
                     'BEL':[50, 5], 'CAN':[60,-100 ], 'CZE':[49.5, 15], 
                     'DNK':[55.75, 9], 'FIN':[62, 26], 'FRA':[46, 2], 
                     'DEU':[52, 10], 'HUN':[46.75, 19], 'ISL':[65, -20], 
                     'IRL':[53, -8.2], 'ITA':[43, 12], 'JPN':[35, 137], 
                     'KOR':[37, 128], 'LUX':[49.8,6], 'MEX':[20,-100], 
                     'NLD':[52, 5], 'NZL':[-38, 175], 'NOR':[62, 10], 
                     'POL':[52, 18], 'PRT':[38.25, -8.2], 'SVK':[48.5, 19], 
                     'ESP':[39.25, -3.5], 'SWE':[62, 15], 'CHE':[47, 8], 
                     'TUR':[38, 33], 'GBR':[52, -2], 'USA':[40,-110 ], 
                     'EST':[58, 26.5], 'ISR':[30.5, 34.69], 'SVN':[46, 15], 
                     'LVA':[56.5, 25], 'LTU':[55, 23.5]}
# creating dict just in case
cdict = {'AUS':"Australia", 'GRC':"Greece", 'AUT':"Austria", 
                     'BEL':"Belgium", 'CAN':"Canada", 'CZE':"Czech Republic", 
                     'DNK':"Denmark", 'FIN':"Finland", 'FRA':"France", 
                     'DEU':"Germany", 'HUN':"Hungary", 'ISL':"Iceland", 
                     'IRL':"Ireland", 'ITA':"Italy", 'JPN':"Japan", 
                     'KOR':"South Korea", 'LUX':"Luxembourg", 'MEX':"Mexico", 
                     'NLD':"Netherlands", 'NZL':"New Zealand", 'NOR':"Norway", 
                     'POL':"Poland", 'PRT':"Portugal", 'SVK':"Slovakia", 
                     'ESP':"Spain", 'SWE':"Sweden", 'CHE':"Switzerland", 
                     'TUR':"Turkey", 'GBR':"England", 'USA':"United States", 
                     'EST':"Estonia", 'ISR':"Israel", 'SVN':"Slovenia", 
                     'LVA':"Latvia", 'LTU':"Lithuania"}

dirt ="drive/MyDrive/final/" # path to the data folder referenced below

# collecting economic markers data
ppp_data = pd.read_csv(dirt+"data/economic/ppp_data.csv")
ppp_data = ppp_data[["LOCATION","TIME","Value"]]
ppp_data.rename(columns = {'Value':"PPP"}, inplace = True)
average_wage_data = pd.read_csv(dirt+"data/economic/average_wage_data.csv")
average_wage_data = average_wage_data[["LOCATION","TIME","Value"]]
average_wage_data.rename(columns = {'Value':"AVGWAGE"}, inplace = True)

# collecting climate markers data
def get_name(filename):
    output = ""
    for letter in filename:
        if letter.isupper():
            output = output + letter
    return output
temp_data = pd.DataFrame(columns = ["LOCATION","TIME","TEMPERATURE"])
precip_data = pd.DataFrame(columns = ["LOCATION","TIME","PRECIPITATION"])
for file in os.listdir(dirt+"data/climate"):
    country_name = get_name(file)
    data = pd.read_csv(dirt+"data/climate/"+file,usecols = [0,1])
    if file[0] == "p":
        newframe = pd.DataFrame(columns = ["LOCATION","TIME","PRECIPITATION"])
        newframe["TIME"] = data["Variable:"]
        newframe["LOCATION"] = country_name
        newframe["PRECIPITATION"] = data["pr"]
        newframe = newframe.iloc[1: , :]
        precip_data = pd.concat([precip_data,newframe])
    elif file[0] == "t":
        newframe = pd.DataFrame(columns = ["LOCATION","TIME","TEMPERATURE"])
        newframe["TIME"] = data["Variable:"]
        newframe["LOCATION"] = country_name
        newframe["TEMPERATURE"] = data["tas"]
        newframe = newframe.iloc[1: , :]
        temp_data = pd.concat([temp_data,newframe])
    else:
        print("ERROR IN CREATION OF DATAFRAMES")

# finalizing combined data frame
temp_data = temp_data.reset_index()
precip_data = precip_data.reset_index()
ppp_data = ppp_data.reset_index()
average_wage_data = average_wage_data.reset_index()
combined_data = temp_data.merge(right = precip_data, on = ["LOCATION", "TIME"])
combined_data = combined_data.merge(right = ppp_data, on = ["LOCATION", "TIME"])
combined_data = combined_data.join(other = average_wage_data, how = "outer", rsuffix="r")
combined_data = combined_data[["LOCATION","TIME","TEMPERATURE","PRECIPITATION", "PPP", "AVGWAGE"]]

# function to return dataframe for each country
def get_data(country):
    return combined_data.loc[combined_data["LOCATION"]==country]

# function to produce a geodataframe for each country
def get_geodata(country):
  base = world[world.iso_a3 == country]
  return base

# functions to create models
def get_model_info(country):
  data = get_data(country)
  # getting change in ppp
  d_data = []
  ppp = data["PPP"]
  itert = data["PPP"][:-1]
  count = 0
  for index, value in itert.items():
    dif = float(ppp.iloc[count+1])-float(value)
    d_data.append(dif)
    count = count + 1
  d_ppp = pd.Series(name = "d_ppp", data = d_data)
  # getting change in wage
  d_data = []
  wage = data["AVGWAGE"]
  itert = data["AVGWAGE"][:-1]
  count = 0
  for index, value in itert.items():
    dif = float(wage.iloc[count+1])-float(value)
    d_data.append(dif)
    count = count + 1
  d_wage = pd.Series(name = "d_wage", data = d_data)
  # getting change in temp
  d_data = []
  temp = data["TEMPERATURE"]
  itert = data["TEMPERATURE"][:-1]
  count = 0
  for index, value in itert.items():
    dif = float(temp.iloc[count+1])-float(value)
    d_data.append(abs(dif))
    count = count + 1
  d_temp = pd.Series(name = "d_temp", data = d_data)
  # getting change in precip
  d_data = []
  pcip = data["PRECIPITATION"]
  itert = data["PRECIPITATION"][:-1]
  count = 0
  for index, value in itert.items():
    dif = float(pcip.iloc[count+1])-float(value)
    d_data.append(abs(dif))
    count = count + 1
  d_precip = pd.Series(name = "d_precip", data = d_data)
  return [d_temp, d_precip, d_ppp, d_wage]

# gets the specified plot
def get_plot(country,which):
  info = get_model_info(country)
  temp = info[0]
  precip = info[1]
  ppp = info[2]
  wage = info[3]
  temp_string = 'Absolute Change in Avg. Temperature\n (Degrees Celsius)'
  wg_string = 'Change in Average Wage\n (US dollar)'
  ppp_string = 'Change in PPP\n (National currency units/US dollar)'
  pc_string = 'Absolute Change in Precipitation\n (mm)'
  if which == 1:
    out = px.scatter(x=temp, y = ppp, trendline = "lowess", labels={"x":temp_string, "y":ppp_string}, title=cdict[country])

  elif which == 2:
    out = px.scatter(x=temp, y = wage, trendline = "lowess",labels={"x":temp_string,
                                                                    "y":wg_string},
                     title=cdict[country] )
  elif which == 3:
    out = px.scatter(x=precip, y = ppp, trendline = "lowess",labels={"x":pc_string,
                                                                    "y":ppp_string},
                     title=cdict[country])
  elif which == 4:
    out = px.scatter(x=precip, y = wage, trendline = "lowess",labels={"x":pc_string,
                                                                    "y":wg_string},
                     title=cdict[country])
  else:
    raise("wrong choice")

  return out

# generate all graphs (which were manually added to github)
for country in list_of_countries:
  for n in range(1,5):
    fig = get_plot(country, n)
    pio.write_html(fig, file=dirt +"plots/html/"+country+"_"+str(n)+"_"+".html", auto_open=False)

# creating base interactive map
world = gp.read_file(gp.datasets.get_path('naturalearth_lowres'))
base = world.explore()
gdf = gp.GeoDataFrame(columns = [ "name", "geometry"])
for country in list_of_countries:
  country_spot = get_geodata(country)
  gdf = pd.concat([country_spot ,gdf])
mmap = gdf.explore(
    popup = ["name", 'pop_est', 'gdp_md_est' ],
    tooltip = "name",
    tiles="CartoDB positron",
    cmap = "Set1",
    name = "World Map")

# creating layers to add
layer1 = folium.FeatureGroup(name="Temperature vs. PPP")
layer2 = folium.FeatureGroup(name="Temperature vs. Wage")
layer3 = folium.FeatureGroup(name="Precipitation vs. PPP")
layer4 = folium.FeatureGroup(name="Precipitation vs. Wage")


# creating popups
for country in list_of_countries:
  flagp = False if get_model_info(country)[2].isnull().values.any() else True
  flagw =  False if get_model_info(country)[3].isnull().values.any() else True
  flagprec =  False if get_model_info(country)[1].isnull().values.any() else True
  flagtemp =  False if get_model_info(country)[0].isnull().values.any() else True
  for n in range(1,5):
    html ="<iframe id=\"igraph\" scrolling=\"no\" style=\"border:none;\" seamless=\"seamless\" src=\"https://benmenko.github.io/bmenko-cs260-final/"+country+"_"+str(n)+"_.html\" height=\"525\" width=\"100%\"></iframe>"
    iframe = folium.IFrame(html,width=800,height=500)
    popup = folium.Popup(iframe, max_width=1000)
    if n==1 and flagp and flagtemp:
      marker = folium.Marker(coords[country], popup=popup).add_to(layer1)
    if n==2 and flagw and flagtemp:
      marker = folium.Marker(coords[country], popup=popup).add_to(layer2)
    if n==3 and flagp and flagprec:
      marker = folium.Marker(coords[country], popup=popup).add_to(layer3)
    if n==4 and flagw and flagprec:
      marker = folium.Marker(coords[country], popup=popup).add_to(layer4)

layer1.add_to(mmap)
layer2.add_to(mmap)
layer3.add_to(mmap)
layer4.add_to(mmap)

folium.LayerControl().add_to(mmap) 
mmap.save(dirt+"final_map.html")
mmap