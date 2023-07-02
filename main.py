#!/usr/bin/python3
#By: AstrumStorm

import requests
import time, warnings
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

#########     CONFIG   ####################
###########################################3
warnings.filterwarnings("ignore", category=Warning)
chrome_options = Options()
chrome_options.add_argument("--headless")#FOR HIDDEN EXECUTE
chrome_options.add_argument('--lang=en')#Change the lang. to ENGLISH
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
path_webdriver = 'chromedriver.exe'#########PATH OF CHROMEDRIVER, YOU HAVE TO CHANGE IT
service = Service(executable_path=path_webdriver)
driver = webdriver.Chrome(service=service, options=chrome_options)
############################################

#Short the url of the picture url
def short_url(url):

    payload = {
    'url': url,
    'domain': 0
    }

    r = requests.post('https://cutt.ly/scripts/shortenUrl.php',data=payload)

    return r.text

#Scrap the basic data (n_posts,followers,following,bio) of the user
def scrap_userdata():

    username = input('Type the username: ').lower()

    print('\n[*] Username:',username)

    driver.get('https://instagram.com/'+username)

    time.sleep(4)

    html_document = driver.page_source

    # Check if the user exists
    if "Sorry, this page isn't available" in html_document:
        print('Error, this username does not exists')
        driver.quit()
        exit(1)
    else:
        pass

    print('\n[*] Scraping the basic info\n')

    user_data = {}

    soup = BeautifulSoup(html_document,'html.parser')

    #Here start the scrap, and get the information
    try:
        user_data['name'] = soup.find('span', {'class':'_aacw'}).text
    except:
        user_data['name'] = None

    try:
        user_data['biography'] = soup.find('h1', {'class':'_aacu'}).text.strip('\n')
    except:
        user_data['biography'] = None

    # There are 2 ways to get the profile url
    try:
        user_data['picture_url'] = short_url(soup.find('img', {'class':'_aadp'})['src'])
    except TypeError:
        user_data['picture_url'] = short_url(soup.find('img', {'crossorigin':'anonymous','draggable':'false','class':'x6umtig'})['src'])
 
    instagram_basic_data = soup.find_all('span', {'class':'_ac2a'})

    user_data['posts'] = instagram_basic_data[0].text
    user_data['followers'] = instagram_basic_data[1].text
    user_data['following'] = instagram_basic_data[2].text
    
    if 'This Account is Private' in html_document:
        user_data['private_account'] = True
        driver.quit()

    else:
        user_data['private_account'] = False

    return user_data

#If the user has posts, the script will scrap the data from the posts
def scrap_postsdata():
    
    posts_data = {}

    links_posts = []

    html_document = driver.page_source

    soup = BeautifulSoup(html_document, 'html.parser')

    box_links = soup.find_all('a',{'class':'x1i10hfl'})

    # Check all the links
    for link in box_links:
        
        # If the link has 'p' (publication) it will be added to the list
        if '/p/' in link['href']:
            links_posts.append(link['href'])
        else:
            pass
    
    if len(links_posts) == 0:
        driver.quit()
    else:

        print('[*] Scraping the posts\n')

        count = 1

        # For each link in the list, the script will do the next:
        for i in links_posts:

            aux_dic = {}

            driver.get('https://instagram.com'+i)

            time.sleep(4)

            html_post = driver.page_source

            soup = BeautifulSoup(html_post, 'html.parser')
            
            link_by = i+'liked_by/'

            aaux = soup.find('a', {'href': link_by})

            try:
                aux_dic['likes'] = aaux.find('span').text
            except:
                aux_dic['likes'] = 0

            aux_dic['date'] = soup.find('time', {'class':'_aaqe'}).text

            aux_dic['link'] = 'https://instagram.com'+i

            aux_dic['n_comments'] = len(soup.find_all('ul', {'class':'_a9ym'}))
            
            if aux_dic['n_comments'] != 0:
                aux_commenters = []
                all_commenters = soup.find_all('h3', {'class':'_a9zc'})

                for name in all_commenters:
                    af = name.find('a').text
                    aux_commenters.append(af)

                aux_dic['commenters'] = aux_commenters

            else:
                aux_dic['commenters'] = [None]

            posts_data[count] = aux_dic

            count += 1

        return posts_data

#Show all the data
def show_alldata(user_data,posts_data):

    print('Information from the profile'.center(50,'-'))

    print(f'''
    Name: {user_data['name']}
    Bio: {user_data['biography']}
    Posts: {user_data['posts']}
    Followers: {user_data['followers']}
    Following: {user_data['following']}
    Picture URL: {user_data['picture_url']}
    Private Profile: {user_data['private_account']}
    ''')

    #If the posts data has none, the script will stop because there are not posts
    if posts_data == None:
        exit(0)
    else:

        print('Information of posts'.center(50,'-'))

        for post in posts_data:
            print(f'''
            Publication: {post}
            Date: {posts_data[post]['date']}
            Likes: {posts_data[post]['likes']}
            N comments: {posts_data[post]['n_comments']}
            Commenters list: {posts_data[post]['commenters']}
            Link: {posts_data[post]['link']}
            ''')


if __name__ == '__main__':

    u_data = scrap_userdata()

    #If is a private accounte only will print the basic info
    if u_data['private_account'] == True:
        show_alldata(u_data,posts_data=None)
    #Print the posts data and the user data
    else:
        p_data = scrap_postsdata()
        show_alldata(u_data,p_data)
        driver.quit()
