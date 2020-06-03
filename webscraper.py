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


def scrape(flight):
    driver = webdriver.Chrome()
    datum = {}
    driver.get('https://www.kayak.com/flights/' + flight.origin + '-' +
               flight.destination + '/' + flight.departDate + '/' + flight.returnDate + '?sort=bestflight_a')

    driver.refresh()

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    global results
    deptimes = soup.find_all('span', attrs={'class': 'depart-time base-time'})
    arrtimes = soup.find_all('span', attrs={'class': 'arrival-time base-time'})
    meridies = soup.find_all('span', attrs={'class': 'time-meridiem meridiem'})

    deptime = []
    for div in deptimes:
        deptime.append(div.getText()[:-1])

    arrtime = []
    for div in arrtimes:
        arrtime.append(div.getText()[:-1])

    meridiem = []
    for div in meridies:
        meridiem.append(div.getText())

    deptime = np.asarray(deptime)
    deptime = deptime.reshape(int(len(deptime)/2), 2)

    arrtime = np.asarray(arrtime)
    arrtime = arrtime.reshape(int(len(arrtime)/2), 2)

    meridiem = np.asarray(meridiem)
    meridiem = meridiem.reshape(int(len(meridiem)/4), 4)

    # Get the price
    regex = re.compile(
        'Common-Booking-MultiBookProvider (.*)multi-row Theme-featured-large(.*)')
    price_list = soup.find_all('div', attrs={'class': regex})

    price = []
    for div in price_list:
        price.append(int(div.getText().split('\n')[3][1:-1]))

    df = pd.DataFrame({"origin": flight.origin,
                       "destination": flight.destination,
                       "startdate": flight.departDate,
                       "enddate": flight.returnDate,
                       "price": price,
                       "currency": "USD",
                       "deptime_o": [m+str(n) for m, n in zip(deptime[:, 0], meridiem[:, 0])],
                       "arrtime_d": [m+str(n) for m, n in zip(arrtime[:, 0], meridiem[:, 1])],
                       "deptime_d": [m+str(n) for m, n in zip(deptime[:, 1], meridiem[:, 2])],
                       "arrtime_o": [m+str(n) for m, n in zip(arrtime[:, 1], meridiem[:, 3])]
                       })

    results = pd.concat([results, df], sort=False)

    results_flights = soup.find_all(
        'div', {'class': "inner-grid keel-grid"})
    count = len(results_flights)
    print(f'{count} flights to {flight.destination}')

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
    return count


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


class Flight:

    def __init__(self, origin, destination, departDate, returnDate):
        self.origin = origin.upper()
        self.destination = destination.upper()
        self.departDate = departDate
        self.returnDate = returnDate

    def __str__(self):
        return f'Flight from {self.origin} to {self.destination} on {self.departDate} returning {self.returnDate}'


if __name__ == "__main__":
    flights = []

    print(
        'Enter Origin, Destination, Depart Date(YYYY-MM-DD), and Return date(YYYY-MM-DD)')
    try:
        loc, dest, go, back = map(str, input().split())
    except ValueError:
        print('Please Enter all Inputs')
    flights.append(Flight(loc, dest, go, back))

    print(
        'Would you like to keep Origin, Depart Date and Return identical to first flight?(y or n)')
    s = str(input())
    if(s == 'y'):
        print('Please input Destination for Flight 2')
        flights.append(
            Flight(flights[0].origin, str(input()), flights[0].departDate, flights[0].returnDate))
    else:
        print(
            'Enter Origin, Destination, Depart Date(YYYY-MM-DD), and Return date(YYYY-MM-DD)')

    flights.append(Flight(loc, dest, go, back))

    results = pd.DataFrame(columns=['origin', 'destination', 'startdate', 'enddate',
                                    'deptime_o', 'arrtime_d', 'deptime_d', 'arrtime_o', 'currency', 'price'])

    for flight in flights:

        if scrape(flight) > 10:
            print(results)
            print(flight)
        else:
            scrape(flight)
