from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

import string
import re
import math

# if chromedriver is outdated, chrome browser has updated, but chromedriver is only compatible with older version.
# run 'choco upgrade chromedriver' in admin powershell

import string


class Flight:

    def __init__(self, origin, destination, departDate, returnDate):
        self.origin = origin.upper()
        self.destination = destination.upper()
        self.departDate = departDate
        self.returnDate = returnDate

    def __str__(self):
        return f'Flight from {origin} to {destination} on {departDate} returning {returnDate}'


def scrape(firstFlight):
    driver = webdriver.Chrome()
    datum = {}
    driver.get('https://www.kayak.com/flights/' + firstFlight.origin + '-' +
               firstFlight.destination + '/' + firstFlight.departDate + '/' + firstFlight.returnDate + '?sort=bestflight_a')

    driver.refresh()

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    results_flights = soup.find_all(
        'div', {'class': "inner-grid keel-grid"})

    print(f'count = {len(results_flights)}')

    for res in results_flights:

        times = res.find('div', {'class': 'section times'}
                         ).get_text()
        numStops = res.find('div', {'class': 'section stops'}
                            ).get_text()
        duration = res.find(
            'div', {'class': 'section duration allow-multi-modal-icons'}).get_text()
        price = res.find('span', {'class': 'price-text'}
                         ).get_text()

        def clean_string(var):
            var = str(var)
            var = var.rstrip()  # remove white space at both ends
            var = var.replace('\n', '')
            return var

        def clean_price(var):
            var = str(var)
            var = var.rstrip()
            var = var.replace('$', '')
            return float(var)

        datum['times'] = datum.get('times', []) + [clean_string(times)]
        datum['numStops'] = datum.get(
            'numStops', []) + [clean_string(numStops)]
        datum['duration'] = datum.get(
            'duration', []) + [clean_string(duration)]
        datum['price'] = datum.get('price', []) + [clean_price(price)]
    calculate(datum)
    return 1


def calculate(datum):
    sumTime = 0
    sumTimeOneStop = 0
    sumTimeTwoStop = 0

    sumNonstopPrice = 0
    sumOnestopPrice = 0
    sumTwostopPrice = 0

    countNonstop = 0
    countOnestop = 0
    countTwostop = 0

    for j in range(len(datum['numStops'])):
        l = list(map(str, datum['numStops'][j].split()))
        datum['numStops'][j] = l[0]

    for p in range(len(datum['price'])):
        if datum['numStops'][p] == 'nonstop':
            sumNonstopPrice += datum['price'][p]
            time, space, travel = datum['duration'][p].rpartition(' ')
            hrAndMmin = list(map(int, re.findall(r'\d+', time)))

            totalTime = (hrAndMmin[0] * 60) + hrAndMmin[1]
            totalTime = float(totalTime/60)
            sumTime += totalTime
            countNonstop += 1
        if datum['numStops'][p] == '1':
            sumOnestopPrice += datum['price'][p]
            time, space, travel = datum['duration'][p].rpartition(' ')
            hrAndMmin = list(map(int, re.findall(r'\d+', time)))
            totalTime = (hrAndMmin[0] * 60) + hrAndMmin[1]
            totalTime = float(totalTime/60)
            sumTimeOneStop += totalTime
            countOnestop += 1
        if datum['numStops'][p] == '2':
            sumTwostopPrice += datum['price'][p]
            time, space, travel = datum['duration'][p].rpartition(
                ' ')  # 5h4m icn-ord
            hrAndMmin = list(map(int, re.findall(r'\d+', time)))  # [5, 4]

            totalTime = (hrAndMmin[0] * 60) + hrAndMmin[1]
            totalTime = float(totalTime/60)
            sumTimeTwoStop += totalTime
            countTwostop += 1

    avgPriceNonstop = 0
    avgPriceOneStop = 0
    avgPriceTwoStop = 0

    if countNonstop > 0:
        avgPriceNonstop = float(sumNonstopPrice / countNonstop)
        print('Average Price for nonstop: $' + str(avgPriceNonstop))
        avgDuration = str(sumTime/float(countNonstop))

        hour, dec, minutes = avgDuration.rpartition('.')

        minutes = math.ceil(float(str(f'{dec}{minutes}')) * 60)
        print('Average Flight Time: ' + str(hour) +
              ' hours ' + str(minutes) + ' minutes')
    else:
        print('No nonstop flights available')
    if countOnestop > 0:
        avgPriceOneStop = float(sumOnestopPrice / countOnestop)
        print('Average Price for 1 stop: $' + str(avgPriceOneStop))
        avgDurationOneStop = str(sumTimeOneStop / float(countOnestop))
        hour1, dec, minutes1 = avgDurationOneStop.rpartition('.')
        minutes1 = math.ceil(float(str(f'{dec}{minutes1}')) * 60)
        print('Average Flight Time with 1 stops: ' +
              str(hour1) + ' hours ' + str(minutes1) + ' minutes')
    else:
        print('No 1 stop flights available')
    if countTwostop > 0:
        avgPriceTwoStop = float(sumTwostopPrice / countTwostop)
        print('Average Price for 2 stop: $' + str(avgPriceTwoStop))
        avgDurationTwoStop = str(sumTimeTwoStop/float(countTwostop))
        hour2, dec, minutes2 = avgDurationTwoStop.rpartition('.')
        minutes2 = math.ceil(float(str(f'{dec}{minutes2}')) * 60)

        print('Average Flight Time with 2 stops: ' +
              str(hour2) + ' hours ' + str(minutes2) + ' minutes')
    else:
        print('No 2 stop flights available')


if __name__ == "__main__":
    print('Enter Origin, Destination, Depart Date(YYYY-MM-DD), and Return date(YYYY-MM-DD)')

    loc, dest, go, back = map(str, input().split())
    firstChoice = Flight(loc, dest, go, back)

    print('Enter Second destination. Will assume same dates and origin as first')
    loc2, dest2, go2, back2 = map(str, input().split())
    secondChoice = Flight(loc2, dest2, go2, back2)
    destinations = [firstChoice, secondChoice]
    for destination in destinations:
        scrape(destination)
        print(f'Destination {destination.destination}')
