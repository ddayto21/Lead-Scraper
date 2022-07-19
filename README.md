# Repository Overview
This repository was built to provide business owners a way to save time by collecting thousands of business leads from Yellow Pages, a website that contains over 27 million businesses in the United States. 

![Python-Cover](images/python-image.jpg)

We use 'requests', a Python library to collect large amounts of unstructured data from Yellow Pages. Then, we use BeautifulSoup to parse relevant information from HTML format. After this process, we use Pandas to create dataframes and save those leads to .CSV files that can be used for marketing campaigns. 

## Install the 'Requests' Library
```
$ pip install requests
```

## Import the Requests Library 
```python

import requests

```
## Send HTTP Request to Server 
```python

response = requests.get(url)

```

## Extract Relevant Data from Response 
We use BeautifulSoup, a Python library that makes it easy to parse data in HTML files.

### Install the Beautiful Soup Library
```
$ pip install beautifulsoup4
```

### Import the Beautiful Soup Library

```python
 from bs4 import BeautifulSoup
```
