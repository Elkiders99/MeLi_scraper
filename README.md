# MeLi Scraper

Scrapes mercadolibre.com for product data and submits the results to a database for further analysis. 
The analysis's goal is to determine the number of distinct products in the first `n` pages of a product search.


## Installation

Requirements:


>`docker`, `docker-compose`, `Python >= 3.6`


* Once you have set up your Python environment:



>pip install -r requirements.txt


* Initialize containerized database:

>docker-compose up -d


## Usage

Scrapper can be run with a CLI. Just pass in as arguments the search term and the number of pages it should look for in the site.

>python main.py search number-of-pages
  
## How does it work?

The process can be described as follows:

* The first n search pages are fetched: 

>https://listado.mercadolibre.com.ar/xioami/\_Desde\_1

* By parsing this we generate a list of products with their title, url, and whether the product is new or used.

* We request (in parallel) the html for each product url found in that page. The of number of parallel connections is limited and can be parametrized:

> https://www.mercadolibre.com.ar/xiaomi-redmi-note-8-dual-sim-64-gb-negro-espacial-4-gb-ram/p/MLA15188552?source=search#searchVariation=MLA15188552&position=1&type=product&tracking_id=428ffb2f-ad69-4ea7-b4c0-ac59aac16c14

* Each product is parsed to get the data in the "Características Principales" chart. 

* Each product is uploaded as a row to the database with its characteristics in a single column.

* As a separate process, the data is retrieved from the database and an analysis is run to determine how many products are unique.



## Justification

First I thought about using just the product titles to determine whether they were distinct from the rest or not, since most of the time, the information provided in the titles seemed to be sufficient. This seemed like a good idea, because it meant very little requests and resources invested into parsing. 

Nonetheless, this proved to be harder than I first thought. First I tried using the Levenshtein distance in a tokenized fashion, but results were not good. This led me to believe that I would have had to look into some sort of clustering or machine learning algorithm.

Luckily I found that inside each of the products HTML page was a chart providing structured information about every product.
This seemed to definitely be the way to go since it would provided deterministic results in a much cheaper way and without the need for a training process. It also has the advantage that the analysis could be applied to any type of product without a need for re-training an algorithm.

Even though this data is submited by publishers and may contain errors, for my search "Xiaomi" the results demonstrated to be pretty good.

The challenge then became to making the scraping as efficient as possible.

While testing, I found out that if too many url requests were made in parallel, data wasn't consistent. Lots of times the HTML did not contain the required chart. A good configuration proved to be:

* Set parallel requests to a maximum of 50 simultaneous connections.

* Set a timeout of 10 seconds for each request.

* Retry a maximum of 10 times for each product.  This limit is important since there exists a possibility that the e-commerce has changed its source HTML and the parser designed no longer applies. 

Sometimes the HTML downloaded doesn't have the data we are looking for. I do not know exactly why and when this happens. It might have to do with javascript taking a long time to render the charts.

Fine-tunning and optmizing this numbers seems to require a lot of trial and error. This numbers can be configured. Maybe we could automate this process.
