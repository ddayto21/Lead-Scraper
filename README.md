# Repository Overview
This repository was built to provide business owners a way to save time by collecting thousands of business leads from Yellow Pages, a website that contains over 27 million businesses in the United States. 

![Python-Cover](images/python-image.jpg)
We use 'requests', a Python library to collect large amounts of unstructured data from Yellow Pages. Then, we use BeautifulSoup to parse relevant information from HTML format. After this process, we use Pandas to create dataframes and save those leads to .CSV files that can be used for marketing campaigns. 

## Requests Library Installation
```
$ pip install requests

```

```python

import requests
response = requests.get(url)

```