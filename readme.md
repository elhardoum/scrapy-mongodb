## Usage

```bash
# build and run containers
docker-compose up -d

# SSH into the container
docker-compose exec app /bin/bash

# to run the scraper
scrapy runspider app.py -a company='leonardo-azpiri-sa'
```