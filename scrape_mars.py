#Import dependencies
from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import pymongo
from webdriver_manager.chrome import ChromeDriverManager
from flask import Flask, render_template, redirect

def init_browser():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    return Browser('chrome', **executable_path, headless=False)

def scrape():
    browser=init_browser()
    mars_data_dict ={}

    #Scraped Mars News URL
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    html = browser.html
    soup = bs(html, 'html.parser')
    news_title = soup.find_all('div', class_='content_title')[1].text
    news_p = soup.find('div', class_='article_teaser_body').text

    #Scraped jpl images
    jpl_url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(jpl_url)
    jpm_html = browser.html
    soup_image = bs(jpm_html, 'html.parser')
    image = soup_image.find_all('img', class_='headerimage fade-in')[0]['src']
    cleaned_url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/'
    featured_image_url = cleaned_url + image

    #Scraped Mars Facts Data
    facts_url = 'https://space-facts.com/mars/'
    tables = pd.read_html(facts_url)
    facts_df = tables[0]
    facts_df = facts_df.rename(columns={0:"Description", 1:"Value"})
    html_table = facts_df.to_html()

    #Scraped Hemisphere Data
    geo_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    image_url = 'https://astrogeology.usgs.gov'
    browser.visit(geo_url)
    geo_html = browser.html
    soup_geo = bs(geo_html, 'html.parser')
    items = soup_geo.find('div', class_='collapsible results')
    images = items.find_all('div', class_='item')
    
    mars_hemispheres = []
    
    for image in images:
        hemisphere = image.find('div', class_="description")
        title = hemisphere.h3.text.strip()
        link = hemisphere.a['href']
        browser.visit(image_url + link)     
        img_html = browser.html
        img_soup = bs(img_html, 'html.parser')    
        img_link = img_soup.find('div', class_='downloads')
        img_url= img_link.find('li').a['href']
    
        hemisphere_dict = {}
        hemisphere_dict['title'] = title
        hemisphere_dict['img_url'] = img_url
    
        mars_hemispheres.append(hemisphere_dict)
    
    #Create a dictionary of all above scraped data to facilitate coversion
    mars_data_dict = {
        "News_Headlines": news_title,
        "News_Tagline": news_p,
        "Featured_Image": featured_image_url,
        "Mars_Facts":html_table,
        "Mars_Hemispheres": mars_hemispheres}

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data_dict
