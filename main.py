import requests
import re
from bs4 import BeautifulSoup
import pandas as pd

def main(url):
    URL = url
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    #bothCP returns an array of just courses and professors
    bothCP = soup.find_all(["h2", "h3"])
    prevCourse = False
    courseProfMap = {}
    lastCName = "temp"

    #loop through array and match up the course with the correct professor
    #returns a dictionary that maps every course with a professor
    for cp in bothCP:
        if (cp.string == "2021 Fall" or cp.string == "Search form" or cp.string == "Subscribe to the CICS eNewsletter"):
            continue
        if (cp.string.split()[0] != "Instructor(s):"):
            lastCName = cp.string
        if (prevCourse == True and cp.string.split()[0] == "Instructor(s):"):
            courseProfMap[lastCName] = cp.string
            prevCourse = False
        if (prevCourse == True and cp.string.split()[0] != "Instructor(s):"):
            courseProfMap[lastCName] = "TBD"
            prevCourse = False
        if (prevCourse == False):
            prevCourse = True
    return courseProfMap


#filter function to filter out characters
def sort(variable):
    letters = ['', ' ', '"', '>']
    if (variable in letters):
        return False
    return True
#return the values of the array by elminating unneeded characters
def findValues(arr):
    resultArr = []
    for x in arr:
        if (len(x) > 1 and x[0] == '>'):
            resultArr.append(x.replace('>',""))
    return resultArr


def lookUpProf(prof_name):
    #id for school
    id = '1513'
    name = prof_name
    URL = 'https://www.ratemyprofessors.com/search/teachers?query=' + name + '&sid=' + id
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    #Main data to be scraped
    rating_numR = soup.findAll("div", {"class": "CardNumRating__StyledCardNumRating-sc-17t4b9u-0 eWZmyX"})
    profName = soup.find("div", {"CardName__StyledCardName-sc-1gyrgim-0 cJdVEK"})
    uni_depart = soup.find("div", {"CardSchool__StyledCardSchool-sc-19lmz2k-2 gSTNdb"})
    diff_feed = soup.find("div", {"class": "CardFeedback__StyledCardFeedback-lq6nix-0 frciyA"})
    notFound = soup.findAll("div", {"SearchResultsPage__SearchResultsPageHeader-sc-1srop1v-3 flHcYr"})

    #If professor isn't found
    if(len(notFound) == 0):
        return [name + " not found"]


    rating_numR = rating_numR[0]
    rating_numR = str(rating_numR)
    profName = str(profName)
    uni_depart = str(uni_depart)
    diff_feed = str(diff_feed)

    delim = "<", '"', "!", "--", "_", "%", "div", "/", "=", ",", "-", "\\d", "\\W", ' ', "\"\"", "CardName__StyledCardName", "class", "CardNumRating", "StyledCardNumRating", "CardNumRatingHeader", "Count", "QUALITY", "Number", "Header", "CardFeedback", "CardFeedbackItem", "CardSchool"
    regexPattern = '|'.join(map(re.escape, delim))

    #remove and keep only the needed information
    rating_numR = list(filter(sort, re.split(regexPattern, rating_numR)))
    profName = list(filter(sort, re.split(regexPattern, profName)))
    uni_depart = list(filter(sort, re.split(regexPattern, uni_depart)))
    diff_feed = list(filter(sort, re.split(regexPattern, diff_feed)))


    data_arr = [findValues(profName),findValues(rating_numR),findValues(uni_depart),findValues(diff_feed)]
    return data_arr

if __name__ == "__main__":
    #Get computer science instructors and courses from current semester
    url = 'https://www.cics.umass.edu/content/fall-21-course-descriptions'
    cpMap = main(url)
    print(cpMap)
    delim = ["Instructor(s):",","]
    dataCSV = []
    regexPattern = '|'.join(map(re.escape, delim))
    #for each professor scrape data from ratemyprofessor and added it into a csv file
    for course in cpMap:
        profStr = cpMap[course]
        profStr = profStr.replace("Instructor(s):","")
        print(course)
        dataCSV.append([course])
        for x in profStr.split(","):
            #print(x)
            dataCSV.append(lookUpProf(x))

    pd.DataFrame(dataCSV).to_csv('Data_Sheet.csv', index=None, header=None)

