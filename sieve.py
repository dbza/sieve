#Scrape Linkedin Job listings and do advanced filtering on JD 
#be nice re volume
#todo: learn more about object referencing and trim excess if any
from bs4 import BeautifulSoup
from urllib.request import urlopen
import csv
import math
from time import sleep

BASE_URL = "https://www.linkedin.com/jobs/search?keywords=ETL+NOT+Manager+NOT+Staffing+NOT+BeyondSoft+NOT+CyberCoders+NOT+%22Central+Business%22+NOT+%22Strategic+IT%22+NOT+%22TechConnect+LLC%22+NOT+Infosys+NOT+Partners&locationId=us:0&f_TP=1"

def make_soup(list_page_url):
    htmltxt = urlopen(list_page_url).read()
    soup = BeautifulSoup(htmltxt,"lxml")
    return soup
    
def get_parsed_dict(soup):
    listings=[]
    result_list = soup.find("ul","search-results")
    for li in result_list.findAll ("li"):
        listing = {
        "URL": li.a['href'][:44], #need substr later
        "imageUrl": li.a.img['data-delayed-url'],
        "Company": li.find('span', class_="company-name-text").string,
        "Title": " ".join([child_tag.string for child_tag in li.find('span', class_="job-title-text").children]),
        "Location": li.find('span', class_="job-location").span.string
         }       
        listings.append(listing)
    return listings
    
def is_company_blacklisted(companyname):
    blacklist = ['CyberCoders','Central Business Solutions',
                 'K2 Partnering Solutions','Pandera Systems',
                 'Beyondsoft','Strategic IT Staffing','Jobspring Partners',
                 'Cyma','Experis','Bridgepoint Education',
                 'PennyMac Loan Services, LLC','Avanti Recruitment Solutions',
                 'HERO.jobs','Insitu Inc.','RouteMatch Software',
                 'AVANI Technology Solutions Inc','Intellisoft Technologies',
                 'Staff Perm LLC','Key Business Solutions, Inc','GlobalTranz',
                 'FILD Inc. ','ARC Government Solutions','SkillStorm',
                 'Volt Workforce Solutions','Applied Resource Group']
    for badcompany in blacklist:
        if badcompany in companyname:
            return True
    return False

def location_preference_level(state):
    pref_0 = ['California', 'Oregon', 'Washington','Utah']
    pref_1 = ['Texas', 'Arizona', 'Georgia']
    if state in pref_0:
        return 0
    elif state in pref_1:
        return 1
    else:
        return 2
    

#evaluate results from page based on full JD and append to main list
def evaluate_and_append(page_listings,filtered_listings):
    for listing in page_listings:
        if is_company_blacklisted(listing["Company"]):
            listing["Reject_reason"]="Blacklisted company"
            listing["Reject_level"]="10"
        else:
            if listing["Location"].find(','):
                location_pref = location_preference_level(listing["Location"].split(",")[1].strip())
            else:
                location_pref=99
            listing["Reject_level"]= location_pref
            if location_pref > 1 :
                listing["Reject_reason"]="Location"
            else:    
                listing["Reject_reason"]="NA"
                listing["JD"]="TBD"
        filtered_listings.append(listing)
    return filtered_listings
    
if __name__ == '__main__':
    filtered_listings=[]       

    #get first page of results and read count
    instantsoup = make_soup(BASE_URL)
    result_count = instantsoup.find('div',class_="results-context").strong.string
    page_count = math.ceil(int(result_count)/ 25)
    
    try:
        #read and parse rest of the search result pages    
        for i in range(1,page_count):
            #for page numbers > 1         
            if i > 1:
                suffix = "&start=" + str((i-1) *25) +"&count=25&trk=jobs_jserp_pagination_"+str(i)
                instantsoup = make_soup(BASE_URL+suffix)
                
            page_listings = get_parsed_dict(instantsoup)
            filtered_listings = evaluate_and_append(page_listings,filtered_listings) 
            sleep(5)  #no overloading
    except:
        print("exception occured, writing partial results")        
        
    #Write to CSV
    with open ('data_file.csv','w')     as csvfile:
        fieldnames=['URL','imageUrl','Company','Title','Location','Reject_reason','Reject_level','JD']
        writer=csv.DictWriter(csvfile,fieldnames=fieldnames)
        writer.writeheader()
        for singleitm in filtered_listings:
            writer.writerow(singleitm)
    
    