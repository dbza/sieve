#Scrap Linkedin Job listings 
#limit request frequency if you plan to use this
#todo: learn object referencing in detail and optimize
from bs4 import BeautifulSoup
from urllib.request import urlopen
import csv
import math
from time import sleep,strftime

BASE_URL = "https://www.linkedin.com/jobs/search?keywords=ETL+NOT+Manager+NOT+Staffing+NOT+BeyondSoft+NOT+CyberCoders+NOT+%22Central+Business%22+NOT+%22Strategic+IT%22+NOT+%22TechConnect+LLC%22+NOT+Infosys+NOT+Partners&locationId=us:0&f_TP=1"

def make_soup(list_page_url):
    htmltxt = urlopen(list_page_url).read()
    soup = BeautifulSoup(htmltxt,"lxml")
    return soup

#parse html using beautifulsoup and return a list
def parse_listings(soup):
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

def location_preference_level(state):
    pref_0 = ['California', 'Oregon', 'Washington','Utah']
    pref_1 = ['Texas', 'Arizona', 'Georgia']
    if state in pref_0:
        return 0
    elif state in pref_1:
        return 1
    else:
        return 2
 
def is_company_blacklisted(companyname,blacklist):
    for badcompany in blacklist:
        if badcompany in companyname:
            return True
    return False   

#evaluate results from page based on location and commpany
def evaluate_listings(page_listings,filtered_listings):
    with open('blacklist_cos.txt') as f:
        blacklist = f.read().splitlines()
    for listing in page_listings:
        if is_company_blacklisted(listing["Company"],blacklist):
            listing["Reject_reason"]="Blacklisted company"
            listing["Reject_level"]="10"
        else:
            try:
                location_pref = location_preference_level(listing["Location"].split(",")[1].strip())
            except:
                location_pref=99 #location parse error
            listing["Reject_level"]= location_pref
            if location_pref > 1 :
                listing["Reject_reason"]="Location"
            else:    
                listing["Reject_reason"]="NA"
                listing["JD"]="TBD"
        filtered_listings.append(listing)
    return filtered_listings
    
if __name__ == '__main__':
    all_listings=[]       

    #get first page of results and read count
    instantsoup = make_soup(BASE_URL)
    result_count = instantsoup.find('div',class_="results-context").strong.string
    page_count = math.ceil(int(result_count)/ 25)
    
    #read and parse rest of the search result pages    
    for i in range(1,page_count):
        #for page numbers > 1         
        if i > 1:
            suffix = "&start=" + str((i-1) *25) +"&count=25&trk=jobs_jserp_pagination_"+str(i)
            instantsoup = make_soup(BASE_URL+suffix)
        
        page_listings = parse_listings(instantsoup)
        all_listings.extend(page_listings)
        sleep(3)  #no overloading
    
    #evaluate and prioritize level 1        
    filtered_listings= []
    filtered_listings=evaluate_listings(all_listings,filtered_listings) 
   
    #Write to CSV
    filename = 'listings_'+ strftime("%Y%m%d") +'.csv'
    with open (filename,'w') as csvfile:
        fieldnames=['URL','imageUrl','Company','Title','Location','Reject_reason','Reject_level','JD']
        writer=csv.DictWriter(csvfile,fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filtered_listings) 
    
    #todo: Read marked entries from csv for detailed look
    #todo: fetch details page, filter on years, technologies