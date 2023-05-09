import time, re
import smtplib
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date, timedelta

def getScope(messy_RFP_description):
    # old regex
    # service_regex = r"^\[B\] Scope of Service:"
    service_regex = r"\[\*\] Scope of Service:"
    print(f'messy RFP Desc: {messy_RFP_description}')

    # Use the finditer function to iterate over the matches in the text
    for service_match in re.finditer(service_regex, messy_RFP_description, flags=re.MULTILINE):
        start_index = service_match.start()
        print(f'START INEFX: {start_index}')
    scope_line = messy_RFP_description[start_index:].split('\n', 1)[1].split('\n', 1)[0]
    scope_line.replace("(1)", '')
    return scope_line


def compileResults(driver, li_elements, link_elements, initialURL, keywords, saveTo):
    for li in li_elements:
        link_elements.append(li.find_element_by_tag_name('a').get_attribute('href'))
    # Iterate over the `a` elements and follow the links
    for index, link in enumerate(link_elements):
        driver.get(link)
        # on the individual result..
        description = driver.find_element_by_tag_name("section")
        messy_RFP_description = re.sub(r"Cost to Download This RFP Document[\s\S]*$", "", description.text)
        posted_date_regex = r"Posted Date (.*)"
        expiry_date_regex = r"Expiry Date : (.*)"
        country_regex = r"Country : (.*)"
        state_regex = r"^State : ([\w\s]+)"

        # Use the search function to find the lines that match the regular expressions
        country_match = re.search(country_regex, messy_RFP_description, flags=re.MULTILINE)
        state_match = re.search(state_regex, messy_RFP_description, flags=re.MULTILINE)
        date_posted = re.search(posted_date_regex, messy_RFP_description, flags=re.MULTILINE)
        expiry_date_match = re.search(expiry_date_regex, messy_RFP_description)
        scope = getScope(messy_RFP_description)

        # Extract the values from the matches, making sure no erroneous values are set
        if country_match:
            country = country_match.group(1)
        else:
            country = 'Not found'

        if state_match:
            state = state_match.group(1)
        else:
            state = 'Not found'

        if date_posted:
            date_posted = date_posted.group(1)
        else:
            date_posted = 'Not found'

        if expiry_date_match:
            expiry_date = expiry_date_match.group(1)
        else:
            expiry_date = 'Not found'

        query = f'{scope} {state} {date_posted} {expiry_date}'
        print (query)
        print(f'\n Result {index+1}: \n Scope: {scope} \n Date Posted: {date_posted}\n Expires: {expiry_date} \n Country: {country}\n State: {state} Link to RFP: {link}\n')
        # searchGoogle = compileSearch(query) --> Martha axed this
        searchGoogle = None
        with open(f'scrapeRFPVendors/results/{saveTo}/{date.today()} {keywords}-RFPMart.txt', 'a', encoding="utf-8") as f:
            if searchGoogle!=None:
                f.write(f'\n <ul><h4>Result {index+1}</h4> <li> Scope: {scope}</li> \n <li>Date Posted: {date_posted}</li>\n <li>Expires: {expiry_date}</li> \n <li>Country: {country}</li>\n <li>State: {state}</li> <li><a href = {link}>Link to RFP Posting</a>\n\n </li> <li> {compileSearch(query)}</li></ul>')
            else:
                f.write(f'\n <ul><h4>Result {index+1}</h4> <li> Scope: {scope}</li> \n <li>Date Posted: {date_posted}</li>\n <li>Expires: {expiry_date}</li> \n <li>Country: {country}</li>\n <li>State: {state}</li> <li><a href = {link}>Link to RFP Posting</a></ul>\n')
            
# saveTo is where the text is .txt file is being saved to (CMMS, UCIMS, etc)
def startSearchingRFPMart(keywords, saveTo):
    driver = webdriver.Chrome()
    # Navigate to the RFPMart website and select search form
    driver.get("https://www.rfpmart.com/filter.html")

    # Input keywords
    select_element = driver.find_element("id", "keyword")
    select_element.send_keys(keywords)

    # Tick box to active
    select_element = driver.find_element("id","type")
    select = Select(select_element)
    select.select_by_index(1) 

    # Search
    select_element = driver.find_element("name", "submit")
    select_element.click()

    # Check for existence of "Next". If it's there, search til it's not. If it isn't, just search the page.
    try:
        next_button = driver.find_element_by_link_text('Next')
    except NoSuchElementException:
        # The "Next" button does not exist, so there is only one page of results
        form_element = driver.find_element_by_class_name("category-detail-lists")
        li_elements = form_element.find_elements_by_tag_name("li")
        link_elements = []
        compileResults(driver, li_elements,link_elements, driver.current_url, keywords, saveTo)
    else:
        # The "Next" button exists, so there are multiple pages of results
        current_url = driver.current_url
        while True:
            # Find the li elements and store them in the link_elements array
            form_element = driver.find_element_by_class_name("category-detail-lists")
            li_elements = form_element.find_elements_by_tag_name("li")
            link_elements = []

            # Compile the results from the current page and go back to OG search page
            compileResults(driver, li_elements,link_elements, current_url, keywords)
            driver.get(current_url)

            # Check if the "Next" button still exists (it may have been removed after the last page)
            try:
                next_button = driver.find_element_by_link_text('Next')
            except NoSuchElementException:
                # The "Next" button does not exist, so we have reached the last page
                break
            else:
                # The "Next" button exists, so click it and navigate to the next page
                driver.get(next_button.get_attribute('href'))

# only works for first page
def startSearchingBidnet(keywords, saveTo):
    keywords = keywords.replace(' ' , '+')
    driver = webdriver.Chrome()
    allOpenRFPs = []
    resultsURLs = []
    # Navigate to the Bidnet website and search with custom URL
    driver.get(f"https://www.bidnetdirect.com/public/solicitations/open?keywords={keywords}&searchContentGroupId=&solSearchStatus=openSolicitationsTab")

    # Compile results URLs
    table = driver.find_element('id',"solicitationsList")
    a_elements = table.find_elements_by_tag_name("a")
    for a in a_elements:
        resultsURLs.append(a.get_attribute('href'))
    searchPageURL = driver.current_url
    for index, link in enumerate(resultsURLs):
        data = ''
        driver.get(link)
        h1 = driver.find_element("tag name","h1")
        data+= f'<ul><h4>Result {index+1} </h4>'
        data+=f'<li>Scope: {h1.text} </li>\n'
        index = 0
        for element in driver.find_elements(By.CLASS_NAME, 'mets-field-body '):
            index +=1
            if index == 3:
                data+=(f'<li> State: {element.text} </li>\n')
            elif index == 4:
                data+=(f'<li> Published: {element.text} </li> \n')
            elif index == 5:
                data+=(f'<li>Closes: {element.text} </li>\n')
        data+=(f'<li><a href = {link}>Link to RFP</a></li></ul>\n')
        with open(f'scrapeRFPVendors/results/{saveTo}/{date.today()} {keywords}-Bidnet.txt', 'a') as f:
            f.write(data +'\n')
        driver.get(searchPageURL)

def main(keywords):
    with open(f'scrapeRFPVendors/results/{date.today()} {keywords}-RFPMart.txt', 'r') as f:
        f.truncate()

    with open(f"scrapeRFPVendors/{date.today()} {keywords}-Bidnet.txt", "r") as f:
        f.truncate()
    
    startSearchingRFPMart(keywords)
    startSearchingBidnet(keywords)

    text = f'<h2>Search results for keyword "{keywords}"</h2> \n\n\n<h3>Beginning of RFPMart Results. The following RFPs are available for purchase for ~$5 per. </h3>\n'
    with open(f'scrapeRFPVendors/results/{date.today()} {keywords}-RFPMart.txt', 'a') as f:
        text += f.read()

    text+='<h3><h2>End of RFPMart results. \n\nBeginning of Bidnet Results. The following RFPs are available with a membership to the site.</h2>\n </h3>'
    with open(f'scrapeRFPVendors/results/{date.today()} {keywords}-Bidnet.txt', 'a') as f:
        text += f.read() +'\n'

    text += 'End. \n\n <i>Developed by Charles Fuss</i>'

    sendHTMLEmail(text, '')
    print('sent HTMLEmail')

def searchCMMS():
    # for debugging -- will clear file if exists on new search
    try:
        with open(f"scrapeRFPVendors/results/CMMS/{date.today()} maintenance+management+system-Bidnet.txt", "w") as f:
            f.truncate()
        with open(f"scrapeRFPVendors/results/CMMS/{date.today()} maintenance management system-RFPMart.txt", "w") as f:
            f.truncate()
    except:
        pass
        
    startSearchingRFPMart('maintenance management system', 'CMMS')
    startSearchingBidnet('maintenance management system', 'CMMS')


    text = f'<h2>Beginning of RFPMart Results. The following RFPs are available for purchase for ~$5 per.</h2> \n'
    with open(f"scrapeRFPVendors/results/CMMS/{date.today()} maintenance management system-RFPMart.txt", "r", encoding="utf-8") as f:
        text += f.read()
    
    text+='<h2>End of RFPMart results. \n\nBeginning of Bidnet Results. The following RFPs are available with a membership to the site.</h2>\n'
    with open(f"scrapeRFPVendors/results/CMMS/{date.today()} maintenance+management+system-Bidnet.txt", "r") as f:
        text += f.read() +'\n'

    sendHTMLEmail(text, f'CMMS Software RFP Results for {date.today()}')
    print('sent email')

def searchUAMS():
    # for debugging -- will clear file if text alr exists
    try:
        with open(f"scrapeRFPVendors/results/UAMS/{date.today()} asset+management+system-Bidnet.txt", "w") as f:
            f.truncate()
        with open(f"scrapeRFPVendors/results/UAMS/{date.today()} asset management system-RFPMart.txt", "w") as f:
            f.truncate()
        with open(f"scrapeRFPVendors/results/UAMS/{date.today()} asset+management+software-Bidnet.txt", "w") as f: 
            f.truncate()
        with open(f"scrapeRFPVendors/results/UAMS/{date.today()} asset management software-RFPMart.txt", "w") as f: 
            f.truncate()
    except:
        pass

    startSearchingRFPMart('asset management system', 'UAMS')
    startSearchingRFPMart('asset management software', 'UAMS')
    startSearchingBidnet('asset management system', 'UAMS')
    startSearchingBidnet('asset management software', 'UAMS')
    text = f'<h2>Beginning of RFPMart Results. The following RFPs are available for purchase for ~$5 per.</h2> \n'
    with open(f"scrapeRFPVendors/results/UAMS/{date.today()} asset management system-RFPMart.txt", "r") as f:
        text += f.read() +'\n'
    with open(f"scrapeRFPVendors/results/UAMS/{date.today()} asset management software-RFPMart.txt", "r") as f: 
        text += f.read() + '\n'
    text+='<h2>End of RFPMart results. \n\nBeginning of Bidnet Results. The following RFPs are available with a membership to the site.</h2>\n'
    with open(f"scrapeRFPVendors/results/UAMS/{date.today()} asset+management+system-Bidnet.txt", "r") as f:
        text += f.read() + '\n'
    with open(f"scrapeRFPVendors/results/UAMS/{date.today()} asset+management+software-Bidnet.txt", "r") as f: 
        text += f.read() + '\n'
    sendHTMLEmail(text, f'UAMS Software RFP Results for {date.today()}')
    print('sent email')

def searchUCIMS():
    # for debugging -- will clear file if exists on new search
    try:
        with open(f"scrapeRFPVendors/results/UCIMS/{date.today()} WAMS-RFPMart.txt", "w") as f:
           f.truncate()
        with open(f"scrapeRFPVendors/results/UCIMS/{date.today()} WAMS-Bidnet.txt", "w") as f:
            f.truncate()
    except:
        pass
    startSearchingRFPMart('WAMS', 'UCIMS')
    startSearchingBidnet('WAMS', 'UCIMS')

    text = f'<h2>Beginning of RFPMart Results. The following RFPs are available for purchase for ~$5 per.</h2> \n'
    with open(f"scrapeRFPVendors/results/UCIMS/{date.today()} WAMS-RFPMart.txt", "r") as f:
        text += f.read()

    text+='<h2>End of RFPMart results. \n\nBeginning of Bidnet Results. The following RFPs are available with a membership to the site.</h2>\n'
    with open(f"scrapeRFPVendors/results/UCIMS/{date.today()} WAMS-Bidnet.txt", "r") as f:
        text += f.read() +'\n'

    sendHTMLEmail(text, f'UCIMS RFP Results for {date.today()}')
    print('sent email')

def utilityBilling():
  # for debugging -- will clear file if exists on new search
    try:
        with open(f"scrapeRFPVendors/results/Utility Billing/{date.today()} utility+billing-Bidnet.txt", "w") as f:
            f.truncate()
        with open(f"scrapeRFPVendors/results/Utility Billing/{date.today()} utility billing-RFPMart.txt", "w") as f:
            f.truncate()
    except:
        pass
    startSearchingRFPMart('utility billing', 'Utility Billing')
    startSearchingBidnet('utility billing', 'Utility Billing')

    text = f'<h2>Beginning of RFPMart Results. The following RFPs are available for purchase for ~$5 per.</h2> \n'
    with open(f"scrapeRFPVendors/results/Utility Billing/{date.today()} utility billing-RFPMart.txt", "r") as f:
        text += f.read()

    text+='<h2>End of RFPMart results. \n\nBeginning of Bidnet Results. The following RFPs are available with a membership to the site.</h2>\n'
    with open(f"scrapeRFPVendors/results/Utility Billing/{date.today()} utility+billing-Bidnet.txt", "r") as f:
        text += f.read() +'\n'

    sendHTMLEmail(text, f'Utility Billing Software RFP Results for {date.today()}')
    print('sent email')

def sendHTMLEmail(body, subject):
    # Create the message
    msg = MIMEMultipart()
    msg['From'] = GMAIL_MAIN
    recepients = [f'{MY_EMAIL}', f'{MANAGER_EMAIL}']
    msg['To'] = ", ".join(recepients)
    msg['Subject'] = subject

    # Add the HTML message as an alternative
    # html = f'<html><body><h1>{body}</h1></body></html>'
    html = body
    msg.attach(MIMEText(html, 'html'))

    # Connect to the server and send the email
    server = smtplib.SMTP('smtp.outlook.com', 587)
    server.starttls()
    server.login("GMAIL_MAIN", "MY_PW")
    server.send_message(msg)
    print('HTML Email Sent')
    server.quit()

def dedupResults(keywords, subject, newData):
    dateLastRan=date.today() - timedelta(days = 2)
    print(dateLastRan)
    lastRanEntries = []
    flag = False
    counter = 0
    with open(f"scrapeRFPVendors/results/{subject}/2023-01-24 utility billing-RFPMart.txt", "r") as old:
        for index, line in enumerate(old):
            if '<ul>' in line:
                scope = line.split("Scope: ")[-1]
                lastRanEntries.append(scope)
    with open(f"scrapeRFPVendors/results/{subject}/2023-02-06 utility billing-RFPMart.txt", "r") as infile,  open("output.txt", "w") as outfile:
        for line in infile:
            if '<ul>' in line:
                scope = line.split("Scope: ")[-1]
                if scope not in lastRanEntries and flag == False:
                    print(f'{scope} was not found in lastRanEntries.')
                    outfile.write(line) 
                    flag = True
            elif flag == True:
                if(counter != 6):
                    outfile.write(line)
                    counter+=1
                else:
                    flag = False
                    counter = 0
            
if __name__ == '__main__':
    searchCMMS() # keyword = maintenance management system
    searchUAMS() # keyword = asset management system, asset management software
    searchUCIMS() # keyword = WAMS
    utilityBilling()
