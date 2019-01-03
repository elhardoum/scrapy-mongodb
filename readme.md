## Usage

```bash
# create an env
virtualenv -p python3 env

# activate env
source env/bin/activate

# change dir
cd src

# install deps
pip install -r requirements.txt

# to run the scraper
scrapy runspider app.py -a company='leonardo-azpiri-sa'
```

## Todo

- [ ] Add `Dockerfile` build for Python, and docker instructions
