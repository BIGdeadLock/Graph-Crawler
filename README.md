# HW-Graph-Crawler
Repo for the homework assignment of email to graph crawler.


# Design Overview

## Configuration
Using a configuration file we will be able to dynamically change the behavior of the crawler.
This way the user can easily change the behavior of the crawler without having to recompile the code.

## Client-Server
In order to run the program as a micro service I used flask to create a simple server that will
run the crawler and return the results to the user.

## Scraper
I used a factory design pattern to dynamically create the scraper based on the configuration file or
the user http request.
The developer can easily add new scrapers by implementing the Scraper interface in 
`scraper.py` and adding the scraper to the factory by adding it to the `SCRAPERS` list in `scraper\__init__.py`.

## Crawler
The `crawler.py` is class with a recursive function that will crawl the internet starting from the given url.
to speed up the crawling process I used a thread pool to run the scraper in parallel.
Each new crawler was started with a different seed which was given by the user.

## Datastructures - Graph
I used a graph data structure to store the crawled data. The graph is implemented in `ds.py`.
I consider the possibility that future developers will want to use other data structures to store the data.
As so, I created a data structure package with a graph package inside it. Each data structure will have its own package.
Each data structure will have to implement the method `get_top_n_for_each_domain` that will return the top n nodes
in each domain. This way the user can easily change the data structure without having to change the rest of the code.

# Business Logic 
In order to select the best ranking algorithm for selecting the best url in each domain I came up with the following
possible business questions i.e. use cases:
For a marketing campaign the company want to start scraping the interesting data and look for emails. 
For the crawling process they want to select the best url in each domain. The best url is the one with the most
email addresses in it or with the most links to other pages in the domain that host email addresses.

Another possible use case is for a hacker who want to start a phishing campaign. He wants to crawl the internet
and look for email addresses. He wants to select the best url in each domain. The best url is the one with the most
email addresses in it or with the most links to other pages in the domain that host email addresses.

### Graph structure
The graph structure is an undirected graph. Each node is a url or an email address. Each edge is a link between two nodes.
Each node has two attributes: `domain` and `type`. The `domain` attribute is the domain of the url or the email address.
The `type` attribute is either `url` or `email`. Each edge has a weight of 1 if one of the nodes is an email address and
0 otherwise.

### Ranking Algorithm
Several were tested as can be seen in the `EDA.ipynb` notebook:
1. `cloness centrality` - Closeness centrality identifies a node's importance based on how close it is to all the other nodes in the graph
2. `degree centrality` - Degree centrality defines the importance of a node based on the degree of that node. The higher the degree, the more crucial it becomes in the graph
3. `betweenness centrality` - Betweenness centrality defines the importance of a node based on the number of shortest paths that pass through it
4. `eigenvector centrality` - Eigenvector centrality defines the importance of a node based on the importance of its neighbors
5. `pagerank` - PageRank defines the importance of a node based on the importance of the nodes that link to it

**Note:** For more information, please refer to https://www.turing.com/kb/graph-centrality-measures

The best ranking algorithm was `eigenvecotr` as it had the most sense. The reason is that each edge between two nodes
that one is an email node has a weight of 1. As a result, the eigenvecotr centrality will give a higher score to the node
that has more email nodes connected to it, or more links to other pages in the domain that host email addresses.
Using the method on the test website `https://miet.ac.in/` we can see that the best url is `https://miet.ac.in/applied-science-engineering`

# Docker
For simple deployment I created a `docker-compose.yml` that will run the server and expose the port 8080.

# API Documentation
This project is using swagger for api documentation. Available at `http://localhost:5000/apidocs`. After running
the server you can use the swagger ui to test the api.