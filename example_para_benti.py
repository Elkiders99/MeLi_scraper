import requests
from bs4 import BeautifulSoup


html = request.get('tu-pagina-web.com').text
soup = BeautifulSoup(html, "html.parser")

# hacer cosas con la sopa para extraer lo que necesites: ://www.crummy.com/software/BeautifulSoup/bs4/doc/ 
data = parse_html(soup)

# output data:
print(data)
