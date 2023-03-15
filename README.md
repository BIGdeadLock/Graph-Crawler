# HW-Graph-Crawler
Repo for the homework assignment of email to graph crawler.


# Design Overview

## Configuration
Using a configuration file we will be able to dynamically change the behavior of the crawler.
This way the user can easily change the behavior of the crawler without having to recompile the code.

## Client-Server
In order to run the program as a micro service I used flask to create a simple server that will
run the crawler and return the results to the user.

# Docker
For simple deployment I created a `docker-compose.yml` that will run the server and expose the port 8080.

## Scraper
I used a factory design pattern to dynamically create the scraper based on the configuration file or
the user http request.
The developer can easily add new scrapers by implementing the Scraper interface in 
`scraper.py` and adding the scraper to the factory by adding it to the `SCRAPERS` list in `scraper\__init__.py`.

## Crawler
The `crawler.py` is class with a recursive function that will crawl the internet starting from the given url.
to speed up the crawling process I used a thread pool to run the scraper in parallel.
Each new crawler was started with a different seed which was given by the user.