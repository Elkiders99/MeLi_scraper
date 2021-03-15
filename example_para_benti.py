import requests
from bs4 import BeautifulSoup


html = request.get('tu-pagina-web.com').text
soup = BeautifulSoup(html, "html.parser")

data = parse_html(soup)

# output data:
print(data)

def parse_html(soup):
    # hacer cosas con la sopa para extraer lo que necesites: ://www.crummy.com/software/BeautifulSoup/bs4/doc/ 
    return data

