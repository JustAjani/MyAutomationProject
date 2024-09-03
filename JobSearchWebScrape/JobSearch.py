from bs4 import BeautifulSoup
import requests

def searchJobs():
    skillsInput = input('Preferred Programming Language: ').strip().lower()
    baseUrl = 'https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords='
    nextPage = 1
    return skillsInput, baseUrl, nextPage

def getJobs():
    try:
        while True:
            skillsInput, baseUrl, nextPage = searchJobs()
            userInput = input('Type "Job" to list jobs or "quit" to exit: ').strip().lower()
            if userInput == 'job':
                url = f"{baseUrl}{skillsInput}&txtLocation=&pg={nextPage}"
                response = requests.get(url).text
                soup = BeautifulSoup(response, 'lxml')
                jobs = soup.find_all('li', class_='clearfix job-bx wht-shd-bx')

                if jobs:
                    for job in jobs:
                        companyName = job.find('h3', class_='joblist-comp-name').text.strip()
                        skillsRequired = job.find('span', class_='srp-skills').text.strip().replace(' ', '')
                        jobDescription = job.find('ul', class_='list-job-dtl clearfix').li.text.strip()
                        postTime = job.find('span', class_='sim-posted').span.text
                        jobLink = job.header.h2.a['href']

                        if 'few' in postTime.lower() and skillsInput in skillsRequired:
                            print(f'Company Name: {companyName}')
                            print(jobDescription)
                            print(f'Skills Required: {skillsRequired}')
                            print(f'More Details: {jobLink}')
                            print('-'*170)
                else:
                    print('No Jobs Found')

                nextPage += 1

            elif userInput == 'quit' or userInput == 'exit':
                print("Exiting Program")
                break
            else:
                print("Invalid Input")

    except requests.RequestException as e:
        print(e)

getJobs()
