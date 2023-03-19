# Graph-Crawler
Repo for the project of email to graph crawler.


# Design Overview
Schema of high level design:

![image](https://user-images.githubusercontent.com/64005996/226172833-bc4ea31a-db37-413e-8c38-e013fb14e87b.png)


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
The `crawler.py` is a class with a function that will crawl the internet starting from the given url.
to speed up the crawling process I used a thread pool to run the scrapers in a concurrent fashion.
Each new crawler was started with a different seed which was given by the user.

## Datastructures - Graph
I used a graph data structure to store the crawled data. The graph is implemented in `ds.py`.
I consider the possibility that future developers will want to use other data structures to store the data.
As so, I created a data structure package with a graph package inside it. Each data structure will have its own package.
Each data structure will have to implement the method `get_top_n_for_each_domain` that will return the top n nodes
in each domain. This way the user can easily change the data structure without having to change the rest of the code.

### Graph structure
The graph structure is an undirected graph. Each node is a url or an email address. Each edge is a link between two nodes.
Each node has two attributes: `domain` and `type`. The `domain` attribute is the domain of the url or the email address.
The `type` attribute is either `url` or `email`. Each edge has a weight of 1 if one of the nodes is an email address and
0 otherwise.

![image](https://user-images.githubusercontent.com/64005996/226116477-8a410f4d-6593-44f1-ad0c-99433243889e.png)

## Decoupeling
I tried to decouple the logic between classes as much as I could so that future development could be easier. Some thing I did:
1. The data-structure is responsible with handaling the scraped data
2. The crawler is only responsible for crawling the internet
3. The scrapers are responsible for only scraped the data passed from the crawler.

# Business Logic 
In order to state which URL is considered better and which is not, we need to define a ranking algorithm.
First, there need to be a scoring system. The scoring system will be based on the number of email addresses each
url has. But there can be cases where an email is considered junk, for example a random email address that is not
real or a spam email. In order to solve this problem I used IDF to rank the email addresses. 

### IDF
IDF stands for Inverse Document Frequency. IDF is a ranking algorithm that is used to rank words in a document.
If the word is rare in the corpus it will be ranked high. If the word is common in the corpus it will be ranked low.
To read more about IDF please refer to https://en.wikipedia.org/wiki/Tf%E2%80%93idf.

In our use case, if the email address is common it is considered junk, for example an email address of the university
or a spam email address. If the email address is rare it is considered good, for example a real email address.


### Ranking Algorithm
We need a ranking algorithm that will be able to rank the urls based on the number of email addresses and the weights.
For that purpose I used PageRank. PageRank is a ranking algorithm that is used to rank web pages. It is based on the
number of links that point to a page and the number of links that point to the pages that point to the page. To read more
about PageRank please refer to https://en.wikipedia.org/wiki/PageRank. 

**Using both IDF and PageRank helps us address different cases:**
1) The email address is rare (good) but is the only one in the url (not good) - The url will be ranked low
2) The email address is rare (good) but is not the only one in the url (good) - The url will be ranked high
3) The email address is common (not good) but is the only one in the url (not good) - The url will be ranked low
4) The email address is common (not good) but is not the only one in the url (good) - The url will be ranked high

# Starting the service
You have two options to run the program:
1) Python with venv
2) Docker

## Python way
You can run the program using python. 1. Open a cmd on the project directory and follow the following steps:
1. Run the command `python -m venv venv`
2. Depend on you OS, run the command `source venv/Scrips/activate` in Windows (in linux replace Scripts with bin)
3. Run the command `python3 -r ./build-docker/requirements.txt
4. Run the command `python3 main.py`

**NOTE:** I assume you have python version >= 3.8 installed locally.

## Docker
For simple deployment I created a `docker-compose.yml` that will run the server and expose the port 5000. To run the docker, open a cmd on the project directory and follow the following steps::

1. In the `./build-dcoker/run.sh` file, fill in the variable PASSWORD with your sudo password for the script to run.
2. Run the command `cd build-docker`
3. Run the command: `./run.sh build`
4. To veryify it works, run the command: `docker ps` and look the crawler image as seen in:

![image](https://user-images.githubusercontent.com/64005996/226116446-e577d18a-86bb-4dc6-819e-427e583b69e5.png)


**NOTE:** To kill the docker run the command `./run.sh kill`

# API Documentation
This project is using swagger for api documentation. Available at [http://localhost:5000/apidocs](http://localhost:5000/apidocs/#/default/post_graph_build). After running
the server you can use the swagger ui to test the api.

![image](https://user-images.githubusercontent.com/64005996/226118961-4dd4f78d-bd83-4b65-a9f6-630dd5124d80.png)


# Visualization
I added an additional endpoint for you to view the generated graph in your own browser. After creating the graph you can navigate to `/graph/visualize` to see the graph that was generated from the crawling.

![image](https://user-images.githubusercontent.com/64005996/226120790-dc755f8c-3df4-47b4-bb19-745c9056b885.png)


**NOTE:** If the graph is too big (more than 20 nodes), the rendering will be done to the top 20 nodes to not crash the browser.
