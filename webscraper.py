from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
import string
import re
import math

# if chromedriver is outdated, chrome browser has updated, but chromedriver is only compatible with older version.
# run 'choco upgrade chromedriver' in admin powershell


def start(loc, dest, go, back):
    driver = webdriver.Chrome()

    driver.get('https://www.kayak.com/flights/' + loc + '-' +
               dest + '/' + go + '/' + back + '?sort=bestflight_a')
    # time.sleep(100)
    driver.refresh()
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    results_flights = soup.find_all(
        'div', {'class': 'resultWrapper'})
    # more10 = driver.find_element_by_id(
    #     'UHxc-loadMore').click()
    print('count = ' + str(len(results_flights)))
    #print(results_flights[2].find('div', {'class': 'name'}).get_text())
    #fd = open("scraped.txt", 'w')
    # for res in results_flights:
    #     # print(res.find(''))
    #     print(res.find('div', {'class': 'section times'}
    #                    ).get_text(), end=' ')
    #     print(res.find('div', {'class': 'section stops'}
    #                    ).get_text(), end=' ')
    #     print(res.find(
    #         'div', {'class': 'section duration allow-multi-modal-icons'}).get_text(), end=' ')
    #     print(res.find('span', {'class': 'price-text'}
    #                    ).get_text())
    #     # print(res.find('span', {
    #     #       'class': 'label'}).get_text())
    #     print('-'*50)
    #     # print(res.get_text())

    datum = {}
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
            print(hrAndMmin)
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

    # for _ in range(len(datum['duration'])):
    #     if datum['numStops'][_] == 'nonstop':

    #         time, space, travel = datum['duration'][_].rpartition(' ')
    #         hrAndMmin = list(map(int, re.findall(r'\d+', time)))
    #         # print(hrAndMmin)
    #         totalTime = (hrAndMmin[0] * 60) + hrAndMmin[1]
    #         totalTime = float(totalTime/60)
    #         sumTime += totalTime
    #     if datum['numStops'][_] == '1':

    #         time, space, travel = datum['duration'][_].rpartition(' ')
    #         hrAndMmin = list(map(int, re.findall(r'\d+', time)))
    #         totalTime = (hrAndMmin[0] * 60) + hrAndMmin[1]
    #         totalTime = float(totalTime/60)
    #         sumTimeOneStop += totalTime
    #     if datum['numStops'][_] == '2':
    #         time, space, travel = datum['duration'][_].rpartition(
    #             ' ')  # 5h4m icn-ord
    #         hrAndMmin = list(map(int, re.findall(r'\d+', time)))  # [5, 4]
    #         print(hrAndMmin)

    #         totalTime = (hrAndMmin[0] * 60) + hrAndMmin[1]
    #         totalTime = float(totalTime/60)
    #         sumTimeTwoStop += totalTime

    # minutes = minutes * 60
    # minutes1 = minutes1 * 60
    # # print(minutes2)
    # minutes2 = minutes2 * 60

    if countNonstop > 0:
        avgPriceNonstop = float(sumNonstopPrice / countNonstop)
        print('Average Price for nonstop: $' + str(avgPriceNonstop))
        avgDuration = str(sumTime/float(countNonstop))

        hour, dec, minutes = avgDuration.rpartition('.')
        print(f'S{sumTime} A{avgDuration} H{hour} M{minutes}')
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

    # print(datum['duration'])
    # print(datum['numStops'])


if __name__ == "__main__":
    print('Enter Current Location, Destination, Depart, and Return date(YYYY-MM-DD)')
    loc, dest, go, back = map(str, input().split())
    loc = loc.upper()
    dest = dest.upper()
    # print(loc)
    start(loc, dest, go, back)

# WORKING WAIT UNTIL it shows/PRESENT!!!!!!!
    # download_button_path = "//html/body/div[1]/div[1]/main/div/div[2]/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div/a"
    # wait = WebDriverWait(driver, 10).until(
    #     EC.element_to_be_clickable((By.XPATH, download_button_path)))
    # more_button = driver.find_element_by_xpath(
    #     '//html/body/div[1]/div[1]/main/div/div[2]/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div/a')

    # for item in more_button:
    #     ActionChains(d).move_to_element(item).click().perform()  # item.click()

    # closePopup = driver.find_element_by_xpath(
    #     '/html/body/div[45]/div[3]/div/button').click()

    #closePopup = driver.find_element_by_id('c8QT1-dialog-close').click
    # try:
    #     closePopup = driver.find_element_by_xpath(
    #         '/html/body/div[45]/div[3]/div/button/svg').click()
    # except:
    #     closePopup2 = driver.find_element_by_xpath(
    #         '/html/body/div[45]/div[3]/div/button').click()

    # try:
    #     wait = WebDriverWait(driver, 5).until(
    #         EC.element_to_be_clickable((By.XPATH, closePopup))).click()
    # except:
    #     wait = WebDriverWait(driver, 5).until(
    #         EC.element_to_be_clickable((By.XPATH, closePopup2))).click()
    # html = driver.find_element_by_tag_name('html')
    # for i in range(6):
    #     html.send_keys(Keys.PAGE_DOWN)
    # more1 = driver.find_element_by_xpath(
    #     '/html/body/div[1]/div[1]/main/div/div[2]/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/div/a').click()
    # time.sleep(5)
