import requests
import pandas as pd
import lxml
import re
from bs4 import BeautifulSoup

from datetime import datetime, timezone

print("judy")

s = requests.Session()
s.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"
})
r = s.get("https://bulkbox.co.ke/login/?return_url=index.php")
login_soup = BeautifulSoup(r.text,'lxml')
crsf_token = login_soup.find("input", class_="cm-no-hide-input")["value"]

login_form_data = {
    "result_ids": "login_error_popup390",
    "error_container_id": "login_error_popup390",
    "quick_login": "1",
    "return_url": "index.php",
    "user_login": "jgitahi@637capital.com",
    "password": "qwertyuiop",
    "security_hash": crsf_token,
    "full_render": "Y",
    "is_ajax": "1",
    "dispatch[auth.login]": ""
}

login_response = s.post("https://bulkbox.co.ke", data=login_form_data)

page = s.get("https://bulkbox.co.ke/categories-catalog/")
soup = BeautifulSoup(page.text, 'lxml')

all_links =[]

data = soup.findAll('div',attrs={'class':'ab-lc-group'})
for d in data:
    links= d.findAll('a')
    for link in links:
        link.get('href')
        all_links.append(link.get('href'))

all_links2= list(dict.fromkeys(all_links))

category_links1=list(filter(lambda x: [x for i in all_links2 if x in i and x != i] == [], all_links2))
category_links=[]


for k in category_links1:
    category_links.append(k)
    compp =s.get(k)
    soup = BeautifulSoup(compp.text,'lxml')
    n=2
    while soup.find('span',attrs={'class':'ut2-load-more'}):
        add = str(k) + 'page-' + str(n)+ '/'
        category_links.append(add)
        comp=s.get(add)
        soup= BeautifulSoup(comp.text,'lxml')
        n=n+1
       
print(category_links)
print(len(category_links))


product_links=[]

for j in category_links:
    comp =s.get(j)
    soup = BeautifulSoup(comp.text,'lxml')
    data2 = soup.findAll('div',attrs={'class':'ut2-gl__name'})
    for i in data2:
        links2=i.findAll('a')
        for lin in links2:
            lin=lin.get('href')
            if str(lin).find('?') == -1:
                product_links.append(lin)
            else:
                comp5=s.get(lin)
                soup = BeautifulSoup(comp5.text,'lxml')
                data3 = soup.find('div',attrs={'class':'ut2-gl__name'})
                lin2 = data3.find('a')
                lin= lin2.get('href')
                product_links.append(lin)
                

all_products=list(set(product_links))
all_prods= list(dict.fromkeys(product_links))


print(len(product_links))
print(len(all_prods))
print(len(all_products))

output=[]

for k in all_products:
    comp2= s.get(k)
    soup= BeautifulSoup(comp2.text,'lxml')
    if soup.find('div',attrs={'class':'ut2-pb__sku'}):
        product_idd = soup.find('div',attrs={'class':'ut2-pb__sku'})
        product_idd= product_idd.text.strip()
        product_id=re.sub('[^0-9]','', product_idd)
    else:
        product_id = None
    
    if soup.find('h1',attrs={'class':'ut2-pb__title'}):
        name2=soup.find('h1',attrs={'class':'ut2-pb__title'})
        name=name2.text.strip()
        quantity_list= re.findall(r"(?i)(\d+\.?\d*\s*x\s*)*?((\/|\d*\/?\d*\.?\d+\s*)(ml|g|Kg|mlg|'s|packs|Pnt|pcs|Ply|packs|gm|Pairs|s|l|wipes|filters)\b)(\s*\d*x?\-?\s*\d*(packs|'s|wipes)?)?",name,flags=0)
        
        if len(quantity_list)==0:
            quants=soup.findAll('div',attrs={'class':'ty-product-feature__value'})
            quants2=[r.text.strip() for r in quants]
            quants3=''.join(quants2)
            quant4= re.findall(r"(?i)(\d+\.?\d*\s*x\s*)*?((\/|\d*\/?\d*\.?\d+\s*)(ml|g|Kg|mlg|'s|packs|Pnt|pcs|Ply|packs|gm|Pairs|s|l|wipes|filters)\b)(\s*\d*x?\-?\s*\d*(packs|'s|wipes)?)?",quants3,flags=0)
            
            if not quant4:
                quantity = None
            else:
                quantity1 = list(quant4[0]) 
                quantity2=''.join(quantity1[0:2])
                quantity=quantity2

            print(quantity)

        else:
            quantity1 = list(quantity_list[0])
            quantity2=''.join(quantity1[0:2])
            quantity=quantity2
    else:
        name=None
        
    page_url=str(k)
    categories= soup.findAll('a',attrs={'class':'ty-breadcrumbs__a'})
    cats=[x.text for x in categories]
    category_name = cats[3] if len(cats) > 3 else None
    parent_category_name=cats[2]if len(cats) > 2 else None
        
    if soup.find('div',attrs={'class':'ty-qty-out-of-stock ty-control-group__item'}):
        in_stock=False
    else:
        in_stock=True

    if soup.find('span',attrs={'class':'ty-price'}):
        price_effective1=soup.find('span',attrs={'class':'ty-price'})
        price_effective= price_effective1.text.strip()
    else:
        price_effective=None

    if soup.find('span',attrs={'class':'ty-list-price'}):
        if soup.find('span',attrs={'class':'ty-list-price'}).text.strip() == 'KSh 99':
            price_full=price_effective
        else:
            pricey=soup.find('span',attrs={'class':'ty-list-price'})
            price_full=pricey.text.strip()
    else:
        price_full=price_effective
    
    if soup.find('span',attrs={'class':'ty-price-num'}):
        currency1=soup.find('span',attrs={'class':'ty-price-num'})
        currency=currency1.text.strip()
    else:
        currency=None

    if soup.find('div',attrs={'class':'ty-product-feature__value'}):
        brandd=soup.findAll('div',attrs={'class':'ty-product-feature__value'})
        brand=brandd[0].text.strip()
    else:
        brand=None
        
    if soup.find('a',attrs={'class':'cm-image-previewer cm-previewer ty-previewer'}):
        image_url= soup.find('a',attrs={'class':'cm-image-previewer cm-previewer ty-previewer'})
        product_image_url= image_url.get('href')
    else:
        product_image_url=None
    timestamp_utc=datetime.utcnow().strftime('%Y-%m-%d-%H:%M:%S')

    diction={
        "product_id":product_id,
        "name":name,
        "page_url":str(k),
        "categories": [{"category_name":category_name,"parent_category_name":parent_category_name}],
        "in_stock":in_stock,
        "price_effective":price_effective,
        "price_full":price_full,
        "currency":currency,
        "brand":brand,
        "quantity":quantity,
        "product_image_url":product_image_url,
        "description": None,
        "timestamp_utc": timestamp_utc
    }
    output.append(diction)
    print(diction)

df = pd.DataFrame.from_dict(output)
df.to_csv('Bulkbox-30-Nov-20.csv')




