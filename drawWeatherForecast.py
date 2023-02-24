#--------------------------------------------------------------
#Import
#--------------------------------------------------------------
import sys
import os
from datetime import datetime
import logging
import requests

fontDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fonts')
libDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
picDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')

if os.path.exists(libDir):
  sys.path.append(libDir)

from waveshare_epd import epd7in5bc #bc = 3 colours
from PIL import Image,ImageDraw,ImageFont

#--------------------------------------------------------------
#OpenWeatherMap icon map for Meteocons.ttf
#--------------------------------------------------------------
def getWeatherIcon(iconCode):
  switcher = {
    '01d': 'B', #01 clear sky
    '01n': 'C', #01 clear sky
    '02d': 'H', #02 few clouds
    '02n': 'I', #02 few clouds
    '03d': 'N', #03 scattered clouds
    '03n': 'N', #03 scattered clouds
    '04d': 'Y', #04 broken clouds
    '04n': 'Y', #04 broken clouds
    '09d': 'Q', #09 shower rain
    '09n': 'Q', #09 shower rain
    '10d': 'R', #10 rain
    '10n': 'R', #10 rain
    '11d': 'O', #11 thunderstorm
    '11n': 'O', #11 thunderstorm
    '13d': 'W', #13 snow
    '13n': 'W', #13 snow
    '50d': 'E', #50 mist
    '50n': 'E', #50 mist
  }

  return switcher.get(iconCode,'B')

#--------------------------------------------------------------
#OpenWeatherMap setup
#--------------------------------------------------------------
#OpenWeatherMap API key
apiKey = "PutYourKeyHere"
#Base URL
baseUrl = "http://api.openweathermap.org/data/2.5/"
#City
cityName = "London,GB"
#Complete URL
currentWeatherUrl = baseUrl + "weather?appid=" + apiKey + "&q=" + cityName
forecastWeatherUrl = baseUrl + "forecast?appid=" + apiKey + "&q=" + cityName

#--------------------------------------------------------------
#Setup and main loop
#--------------------------------------------------------------
def main():
  try:
    logging.info("Notification start")

    #Initialise display
    #==========================
    epd = epd7in5bc.EPD()
    logging.info("Initialise and clear")
    epd.init()
    epd.Clear()

    #Setup fonts
    #==========================
    tahomaBig = ImageFont.truetype(os.path.join(fontDir, 'tahoma.ttf'), 155)
    tohoma20 = ImageFont.truetype(os.path.join(fontDir, 'tahoma.ttf'), 20)
    tohoma24 = ImageFont.truetype(os.path.join(fontDir, 'tahoma.ttf'), 24)
    tohoma24bd = ImageFont.truetype(os.path.join(fontDir, 'tahomabd.ttf'), 24)
    tohoma40 = ImageFont.truetype(os.path.join(fontDir, 'tahoma.ttf'), 40)
    weatherIconsBig = ImageFont.truetype(os.path.join(fontDir, 'Meteocons.ttf'), 230)
    weatherIconsSmall = ImageFont.truetype(os.path.join(fontDir, 'Meteocons.ttf'), 75)

    #Get start time#Get time of update
    #==========================
    nowTime = datetime.now()
    startTime = nowTime.strftime("%H:%M")
    startDate = nowTime.strftime("%d/%m/%Y")

    #Get weather data
    #==========================
    currentWeatherResponse = requests.get(currentWeatherUrl)
    forecastWeatherResponse = requests.get(forecastWeatherUrl)
    #Convert json format data into python format data
    currentData = currentWeatherResponse.json()
    forecastData = forecastWeatherResponse.json()

    #Check if city exist and print data
    if currentData["cod"] != "404":
      #Store value of main
      currentWeatherData = currentData["main"]
      #Current temperature
      currentTemperature = currentWeatherData["temp"]
      currentTempMin = currentWeatherData["temp_min"]
      currentTempMax = currentWeatherData["temp_max"]
      #Current temperature feels like
      currentTempFeel = currentWeatherData["feels_like"]
      #Current pressure
      currentPressure = currentWeatherData["pressure"]
      #Current humidity
      currentHumidity = currentWeatherData["humidity"]
      #Weather
      weatherDescription = currentData["weather"]
      #Description
      weatherText = weatherDescription[0]["description"]
      weatherIcon = weatherDescription[0]["icon"]
      # print following values 
    else:
      print("City not found")

    #Forecast -- Check if city exist and print data
    forecastList = []
    if forecastData["cod"] != "404":
      #Store value of main
      forecastWeatherDataMain = forecastData["list"]
      #Extract forecast data
      for i in forecastWeatherDataMain:
        forecastItemList = [i["dt_txt"]] #Timestamp
        forecastItemList.append(i["main"]["temp"]) #Weather at timestamp
        forecastItemList.append(i["weather"][0]["icon"]) #Weather icon at timestamp
        forecastList.append(forecastItemList) 
    else:
      print("Forecast city not found") 

    #Get time of update
    #==========================
    nowTime = datetime.now()
    currentTime = nowTime.strftime("%H:%M")
    currentDate = nowTime.strftime("%d/%m/%Y")
    print("Current time = ", currentTime)
    print("Current date = ", currentDate)

    #Write to E-Ink
    #==========================
    imageBlack = Image.new('1', (epd7in5bc.EPD_WIDTH, epd7in5bc.EPD_HEIGHT), 255) # 255: clear frame
    imageRed = Image.new('1', (epd7in5bc.EPD_WIDTH, epd7in5bc.EPD_HEIGHT), 255) # 255: clear frame
    draw = ImageDraw.Draw(imageBlack)
    #Last update stamp
    draw.text((330,350),'Last update: ' + currentDate + ' - ' + currentTime, font = tohoma20, fill = 0)
    #Black frame
    #Forecast +3h
    draw.text((20,245),str(round(forecastList[0][1]-273.15,1)) + '°C', font = tohoma20, fill = 0)
    draw.text((14,270),getWeatherIcon(forecastList[0][2]), font = weatherIconsSmall, fill = 0)
    #Forecast +6h
    draw.text((155,245),str(round(forecastList[1][1]-273.15,1)) + '°C', font = tohoma20, fill = 0)
    draw.text((149,270),getWeatherIcon(forecastList[1][2]), font = weatherIconsSmall, fill = 0)
    #Forecast +9h
    draw.text((290,245),str(round(forecastList[2][1]-273.15,1)) + '°C', font = tohoma20, fill = 0)
    draw.text((284,270),getWeatherIcon(forecastList[2][2]), font = weatherIconsSmall, fill = 0)
    #Forecast +12h
    draw.text((425,245),str(round(forecastList[3][1]-273.15,1)) + '°C', font = tohoma20, fill = 0)
    draw.text((419,270),getWeatherIcon(forecastList[3][2]), font = weatherIconsSmall, fill = 0)
    #Forecast +15h
    draw.text((560,245),str(round(forecastList[4][1]-273.15,1)) + '°C', font = tohoma20, fill = 0)
    draw.text((554,270),getWeatherIcon(forecastList[4][2]), font = weatherIconsSmall, fill = 0)
    #CurrentWeather
    draw.text((7,7),getWeatherIcon(weatherIcon), font = weatherIconsBig, fill = 0)
    draw.text((295,170),'Feels like ' + str(round(currentTempFeel-273.15)) + '°C' + ' Humidity ' + str(currentHumidity) + '%', font = tohoma20, fill = 0)
    currentTempString = str(round(currentTemperature-273.15,1))
    currentTempCharLen = len(currentTempString)-1
    dotLength = 55
    bigFontWidth = 80
    draw.text((280+(currentTempCharLen*bigFontWidth)+dotLength,30),'°C', font = tohoma40, fill = 0)

    #Red frame
    #CurrentWeather
    draw = ImageDraw.Draw(imageRed)
    draw.text((280,1),currentTempString, font = tahomaBig, fill = 0)
    #Forecast +3h
    draw.text((20,220),forecastList[0][0][11:16], font = tohoma24bd, fill = 0)
    #Forecast +6h
    draw.text((155,220),forecastList[1][0][11:16], font = tohoma24bd, fill = 0)
    #Forecast +9h
    draw.text((290,220),forecastList[2][0][11:16], font = tohoma24bd, fill = 0)
    #Forecast +12h
    draw.text((425,220),forecastList[3][0][11:16], font = tohoma24bd, fill = 0)
    #Forecast +15h
    draw.text((550,220),forecastList[4][0][11:16], font = tohoma24bd, fill = 0)

    #Display image
    epd.display(epd.getbuffer(imageBlack),epd.getbuffer(imageRed))

  except IOError as e:
    logging.info(e)

  except KeyBoardInterrupt:
    logging.info("ctrl + c:")
    exit()

  if __name__ == "__main__":
    main()