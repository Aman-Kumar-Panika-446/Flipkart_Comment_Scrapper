from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import csv
import logging
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)

app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","%20")
            product_name = request.form['content']
            flipkart_url = f"https://www.flipkart.com/search?q={searchString}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"
            # Opening the link
            urlclient = urlopen(flipkart_url)
            # Reading the entire html code of site
            flipkart_page = urlclient.read()
            # Beautifying it so that searching and extracting become easy
            flipkart_html = bs(flipkart_page,'html.parser')
            # Storing the link of each product
            Box = flipkart_html.find_all('div',{"class":"cPHDOP col-12-12"})
            
            # Removing unwanted link & fetching link of first product
            product_link = ""
            flag = True
            while (flag):
                try:
                    for i in Box: 
                        product_link = "https://www.flipkart.com" + i.div.div.div.a['href']
                        flag = False
                        break 
                except:
                    del Box[0:1]

            # Opening & Reading the product link
            product_req = requests.get(product_link)

            product_html = bs(product_req.text,'html.parser')

            # Looking for entire comment box which includes name, rating, comment
            comment_box = product_html.find_all('div',{"class":"RcXBOT"})
            
            reviews =[]
            try:
                for i in comment_box:
                    user_name = i.div.div.find_all('p',{"class": "_2NsDsF AwS1CA"})[0].text
                    user_tittle = i.div.div.div.find_all('p',{"class": "z9E0IG"})[0].text 
                    user_rating = i.div.div.div.div.text
                    user_comment = i.div.div.find_all('div',{"class": ""})[0].div.text
                    reviews.append({"Product":product_name,"Name":user_name,"Rating":user_rating,"CommentHead":user_tittle,"Comment":user_comment})
            except:
                print("ALL DATA HAS BEEN LOADED\n")

            # Storing in CSV FILE
            try:
                file_name = product_name.replace(" ","_")+".csv"
                with open(file_name,mode='w',newline='', encoding= 'utf-8') as file:
                    writer = csv.DictWriter(file,fieldnames=["Product","Name","Rating","CommentHead","Comment"])
                    writer.writeheader()
                    writer.writerows(reviews)
            except Exception as e:
                print(f"Error while creating csv file. {e}")    

            # Sending result
            logging.info("log my final result {}".format(reviews))
            return render_template('result.html', reviews=reviews[0:len(reviews)])
        
        except Exception as e:
            logging.info(e)
            return 'something is wrong'

    else:
        return render_template('index.html')


if __name__=="__main__":
    app.run(host="0.0.0.0")
