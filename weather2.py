from flask import Flask, request, jsonify
from cityData import CITY # this is the city list with (Country code)
import pprint, requests

app = Flask('app')
weather_api1='f4ae90e2d9ebd6134141f4509741c3d8'
weather_api='c7e7de2a0b76378c7558a68031ba2c3b'
aqi_key="308bb7a40f0d41e443a3fdc378155a5d86099e4b"

activities={"air_quality":["breathing","picnic"],
"wind":["kite flying","flight","surfing","fishing","skating"],
"UV":["swimming","swim"]}
weather_color={"clouds":"gray",
"clear":"blue",
"rain":"navy"}

aqi_color={
  0:{"condition":"Good",
  "color":"green",
  "cs":"None"},
  50:{"condition":"Moderate",
  "color":"yellow",
  "cs":"<ul><li>Active children</li><li>adults and people with respiratory disease, such as asthma</li></ul> should limit prolonged outdoor exertion."},
  100:{"condition":"Unhealthy for Sensitive Groups",
  "color":"orange",
   "cs":"<ul><li>Active children and adults</li><li>people with respiratory disease, such as asthma,</li></ul>should avoid prolonged outdoor exertion; <ul><li>everyone else, especially children</li></ul> should limit prolonged outdoor exertion"},
  150:{"condition":"Unhealthy",
  "color":"red"},
  200:{"condition":"Very Unhealthy",
    "color":"purple"},
  300:{"condition":"Hazardrous",
    "color":"dark-red"}}


@app.route('/')
def home_page():
  return 'Hello - Weather Bot!'

def get_url(bot):
  return f'http://store.ncss.cloud/melb/{bot}'

def get_weather():
  response_weather = request.get(get_url(weather))

  if response_weather.ok:
    return response_weather.json()
  else:
    return []


@app.route('/weather', methods=['POST'])
def weather():
  data = request.get_json()
  pprint.pprint(data)
  textCont = [city.lower() for city in data['text'].split()]

  country = ''
  for word in textCont:
    if word in CITY:
      city = word
      country = CITY.get(city)
  if country=='':  
    return jsonify({"text":'Incorrect place entered, please re-enter'})

  weatherResponse = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city},{country}&APPID={weather_api}&units=metric')
  aqiResponse=requests.get(f"https://api.waqi.info/feed/{city}/?token={aqi_key}")
  response=weatherResponse.json()
  weatherQuery = response["weather"][0]["main"].lower()
  weatherResp = response["weather"]
 
  print(weatherQuery)
  

  temp = response["main"]["temp"]
  feel_like = response["main"]["feels_like"]
  temp_min = response["main"]["temp_min"]
  temp_max = response["main"]["temp_max"]
  humidity = response['main']['humidity']
  condition = weatherResp[0]['description']
  # print(textCont, weatherQuery)
  

  if weatherQuery == 'clouds':
    weatherCondition = f'it looks like there are {condition}.'
    
  elif weatherQuery == 'clear':
    weatherCondition = f'the sky is looking clear.' 
    
  elif weatherQuery == 'rain':
    weatherCondition = f'Currently its look like {condition}.'
    
  elif weatherQuery == 'thunderstorm':
    weatherCondition = f'Looking at the sky it is sure that there is {condition}.'

  elif weatherQuery == 'drizzle':
   weatherCondition = f"Its lookin' like {condition}, you should bring a raincoat."

  elif weatherQuery == 'snow':
    weatherCondition = f'It looks like {condition}.'
  
  elif weatherQuery == 'atmosphere':
    weatherCondition = f"It looks like there's {condition} in the air."
  
  return jsonify ({
     'text': f'In {city.title()}, {country}, <font color="{weather_color[weatherQuery]}"><strong>{weatherCondition}</strong></font> Current temperature of {temp}°C but it feels like {feel_like}°C. The max will be {temp_max}°C and the min will be {temp_min}°C.'
  })
  # if weatherQuery=="rain":
  #   tip="Remember to bring an umbrella!"
  # return jsonify({
  # 'text': returntext+tip
  #   })
  
@app.route('/aqi', methods=['POST'])
def air_qua():
  data = request.get_json()
  pprint.pprint(data)
  city=data["params"]["place"].lower()
  
  if city not in CITY:
    return jsonify({"text":'Incorrect place entered, please re-enter'})

  aqiResponse=requests.get(f"https://api.waqi.info/feed/{city}/?token={aqi_key}").json()
  aqi_index=aqiResponse["data"]["aqi"]
  color="green"
  condition="Good"
  cs="None"
  for k in aqi_color:
    if aqi_index>k:
      color=aqi_color[k]["color"]
      condition=aqi_color[k]["condition"]
      cs=aqi_color[k]["cs"]
  aqi_html="""<div class="loading loading-2 wave wave-2">
  <div class="ff"></div>
  <div class="loading-2-text"></div>
</div>"""+f"""<div style="background-color:{color};max-width:180px;text-align:center;"><small>{city[0].upper()+city[1:]} AQI</small> <div style='font-size:65px;height:60px;padding-top:0px'>{aqi_index}</div>{condition}</div><br>{cs}"""
  return jsonify({"text":aqi_html})





app.run(debug = True, host='0.0.0.0', port=8080)