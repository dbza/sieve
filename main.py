#abandoned, Linkedin blacklists c9 servers
from bs4 import BeautifulSoup
from urllib2 import urlopen

BASE_URL = "https://www.linkedin.com/jobs/search?keywords=ETL&locationId=us%3A0&f_TP=1%2C2&f_GC=us%2E7-1-0-38-1%2Cus%2E7-3-0-17-29%2Cus%2E7-1-0-19-57&trk=jobs_jserp_facet_geo_city"

def get_JDPage_numbers(list_page_url):
    htmltxt = urlopen(list_page_url).read()
    soup = BeautifulSoup(htmltxt,"lxml")
    result_list = soup.find("ul","search-results")
    item_list = ["this" + dd.a["href"] for dd in result_list.findAll ("li")]
    return item_list
    
if __name__ == '__main__':
    unparsed= get_JDPage_numbers(BASE_URL)
    data = []
    for singleitem in unparsed:
        data.append(singleitem)
        #sleep(1)
    print data
    