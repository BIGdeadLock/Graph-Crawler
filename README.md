# Graph-Crawler
Repo for the project of email to graph crawler. 

# Design Overview
Schema of high level design:

![image](https://user-images.githubusercontent.com/64005996/226172833-bc4ea31a-db37-413e-8c38-e013fb14e87b.png)



### Crawler
The class `crawler.py` has a method that will crawl the internet beginning with the specified url. As may be seen in the picture, it begins the crawling loop.
Each new crawler was launched with a unique seed that the user provided.

I applied the following to quicken the crawling:
1) If several seeds are provided, each seed will launch a distinct crawler thread.
2) To submit several requests simultaneously, each crawler makes use of concurrency using async requests.
3) To conserve bandwidth and time, the scraped data is sent back encoded.
4) Caching: URLs that were visited will be normalized and saved in the cache to prevent from scraping them again.

### Parser
The `parsers` package include a `URLsParser.py` parser to parse the html for more links to visit and scrape. I used a seperate package to enable other developers in the future to add more parsers for more specific links they want to search and parse for.

### Filter
Using predefined rules, the filter is used to filter URLs. Rules might, for instance, filter urls that end in.pdf. The class `URLFilter.py` has the logic in implementation

### Callback
This phrase serves as a catch-all for all processing-related reasoning. It may involve indexing the data, processing it for specific information, adding the data to a database, etc. With the intention of including all callbacks associated with the graph data structure, I established a `graph/callbacks` package in the graph package. `graph\callbacks\callback.py` contains an interface called __GraphCallback__. Future developers will be able to use it and create new callback logic as a result.

## Speed
To speed up the crawling process I used multithreading. Each thread will crawl a different seed and each seed will
spawn a new thread for each new url it finds. This way we can crawl the internet faster.
When a depth is finished to be crawled, the crawler will scale up the number of threads to crawl the next depth.
If too many requests are made, the crawler will wait down scale the number of threads.

## Configuration
Using a configuration file we will be able to dynamically change the behavior of the crawler.
This way the user can easily change the behavior of the crawler without having to recompile the code.

## Client-Server
In order to run the program as a micro service I used flask to create a simple server that will
run the crawler and return the results to the user.

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

### TF-IDF
TF-IDF is a ranking algorithm that is used to rank words in a document. It is based on the number of times a word 
appears in a document and the number of documents that contain the word. To read more about TF-IDF please refer to
https://en.wikipedia.org/wiki/Tf%E2%80%93idf.
In our use case, if the email address is common it is considered junk, for example an email address of the university
or a spam email address. If the email address is rare it is considered good, for example a real email address.

### Email Domain Probability Distribution
In order to account for the possibility of fake email addresses, I decided to map the email domains to a probability.
To do so I used the following steps:
1) Extract all email addresses domain from the graph's email nodes.
2) For each domain, count the number of times it appears in the graph.
3) Calculate the probability of each domain by dividing the number of times it appears by the total number of counted domains.


### Ranking Algorithm
We need a ranking algorithm that will be able to rank the urls based on the number of email addresses and the weights.
For that purpose I used PageRank. PageRank is a ranking algorithm that is used to rank web pages. It is based on the
number of links that point to a page and the number of links that point to the pages that point to the page. To read more
about PageRank please refer to https://en.wikipedia.org/wiki/PageRank. 

To allow page rank to best understand the importance of each url we need to add weights to the edges.
The wight of each node is calculated as follows:
1) If the node is a URL address, the weight is 0
2) If the node is an email address, the weight is `TF-IDF(email_name) * alpha + (1-alpha) * Probability(email_domain)`
where `alpha` is a parameter that can be changed by the user.

**Using both TF-IDF & Probability together with PageRank helps us address different cases:**
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
4. Run the command `python3 main.py` or `\venv\Scripts\python3.exe main.py` in Windows

**NOTE:** I assume you have python version >= 3.8 installed locally.

## Docker
For simple deployment I created a `docker-compose.yml` that will run the server and expose the port 5000. To run the docker, open a cmd on the project directory and follow the following steps::

1. In the `./build-dcoker/run.sh` file, fill in the variable PASSWORD with your sudo password for the script to run.
2. Run the command `cd build-docker`
3. Run the command: `./run.sh build`
4. To veryify it works, run the command: `docker ps` and look the crawler image as seen in:

![image](https://user-images.githubusercontent.com/64005996/226116446-e577d18a-86bb-4dc6-819e-427e583b69e5.png)


**Docker functions:**
1) To kill the docker, run the command `./run.sh kill`
2) To monitor the docker logs, run the command: `./run.sh logging`
3) 

# API Documentation
This project is using swagger for api documentation. Available at [http://localhost:5000/apidocs](http://localhost:5000/apidocs/#/default/post_graph_build). After running
the server you can use the swagger ui to test the api.

![image](https://user-images.githubusercontent.com/64005996/226118961-4dd4f78d-bd83-4b65-a9f6-630dd5124d80.png)


# Visualization
I added an additional endpoint for you to view the generated graph in your own browser. After creating the graph you can navigate to `/graph/visualize` to see the graph that was generated from the crawling.

![image](https://user-images.githubusercontent.com/64005996/226120790-dc755f8c-3df4-47b4-bb19-745c9056b885.png)


**NOTE:** If the graph is too big (more than 20 nodes), the rendering will be done to the top 20 nodes to not crash the browser.
