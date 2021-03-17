from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import pymongo
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager
from flask import Flask, render_template, redirect


def scrape_info():
    # Set up Splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)

    #Establish Mars News URL to be scraped
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    html = browser.html
    # response = requests.get(url)

    # Create BeautifulSoup object; parse with 'html.parser'
    soup = bs(html, 'html.parser')

    # Return the latest news title and paragraph stored as variables
    news_title = soup.find_all('div', class_='content_title')[1].text
    news_p = soup.find_all('div', class_='article_teaser_body')[0].text

    #establish splinter base jpl url space images link
    jpl_url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(jpl_url)
    jpm_html = browser.html
    response = requests.get(jpl_url)

    # Create BeautifulSoup object; parse with 'html.parser'
    soup_image = bs(jpm_html, 'html.parser')

    #Find the image url to the full size .jpg image.
    image = soup_image.find_all('img', class_='headerimage fade-in')[0]['src']

    #clean existing URL to avoid code errors
    cleaned_url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/'

    #assign the url string to a variable called featured_image_url.
    featured_image_url = cleaned_url + image

    #Access the mars facts url
    facts_url = 'https://space-facts.com/mars/'

    #Load the url in using pandas
    tables = pd.read_html(facts_url)

    #Convert table into a dataframe displaying facts about the planet including Diameter, Mass, etc.
    facts_df = tables[0]

    #Rename columns
    facts_df.columns = ["Description", "Value"]

    #convert dataframe back to html table string
    html_table = facts_df.to_html()

    #Capture the usgs astrogeology website
    geo_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    image_url = 'https://astrogeology.usgs.gov'

    #Establish splinter connection
    browser.visit(geo_url)
    geo_html = browser.html
    response = requests.get(geo_url)

    # Create BeautifulSoup object; parse with 'html.parser'
    soup_geo = bs(geo_html, 'html.parser')

    # Retrieve initial elements that contain hemisphere information
    items = soup_geo.find('div', class_='collapsible results')
    images = items.find_all('div', class_='item')

    #create placeholder hemisphere list
    mars_hemispheres = []

    #Create loop to move through each of the web pages
    for image in images:
        #collect title information
        hemisphere = image.find('div', class_="description")
        title = hemisphere.h3.text.strip()
    
        #collect link information which clicks to the next website where full resolution available
        link = hemisphere.a['href']
        browser.visit(image_url + link)     
    
        #collect links from second website for full resolition image
        img_html = browser.html
        img_soup = bs(img_html, 'html.parser')
    
        img_link = img_soup.find('div', class_='downloads')
        img_url= img_link.find('li').a['href']
    
        #Create dictionary to store title and image data
        hemisphere_dict = {}
        hemisphere_dict['title'] = title
        hemisphere_dict['img_url'] = img_url
    
        mars_hemispheres.append(hemisphere_dict)
    
    #Create a dictionary of all above scraped data to facilitate coversion
    mars_data_dict = {
        "News_Headlines": news_title,
        "News_Tagline": news_p,
        "Featured_Image": featured_image_url,
        "Mars_Facts":facts_df,
        "Mars_Hemispheres": mars_hemispheres}

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data_dict
