import heapq
import http.cookiejar as cookielib
import matplotlib.pyplot as plt
import mechanize
import numpy as np
from bs4 import BeautifulSoup

br = mechanize.Browser()
# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)
# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
br.addheaders = [
    (
        "User-agent",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1",
    )
]


class Artist:
    def __init__(self, name):
        self.name = name
        self.ratings = []

    """
    def opener(self,url):
        br.open(url)
        html = br.response().read()
        soup = BeautifulSoup(html, "html.parser")
    """

    def compileWorks(self, URL):
        br.open(URL)
        html = br.response().read()
        soup = BeautifulSoup(html, "html.parser")
        director = soup.find_all(
            "div", id=lambda value: value and value.startswith(category)
        )
        """
        oscar = soup.find("div", class_="article highlighted")
        if oscar != None:
            url = oscar.find("a")["href"]
            url = "https://www.imdb.com" + url
            br.open(url)
            html = 
        """
        for result in director:
            title = result.find("a")
            url = result.find("a")["href"]
            url = "https://www.imdb.com" + url
            br.open(url)
            html = br.response().read()
            soup = BeautifulSoup(html, "html.parser")
            rating = soup.find("span", itemprop="ratingValue")
            year = soup.find("span", id="titleYear")
            year = year.find("a")
            if rating == None:
                continue
            tup = (float(rating.text), title.text, year.text)
            self.ratings.append(tup)

    def returnStatistics(self):
        num_data = []
        for rating in self.ratings:
            num_data.append(rating[0])
        avg = np.average(num_data)
        avg = "{:.2f}".format(avg)
        print("The average of " + self.name + "'s works is: " + avg)
        med = np.median(num_data)
        med = "{:.2f}".format(med)
        print("The median of " + self.name + "'s works is: " + med)
        std = np.std(num_data)
        std = "{:.2f}".format(std)
        print("The standard deviation of " + self.name + "'s works is: " + std)

    def topMovies(self):
        heapq.heapify(self.ratings)
        print(self.name + "'s best movies are: ")
        print(heapq.nlargest(3, self.ratings))

    def graph(self):
        years = []
        rat = []
        for rating in reversed(self.ratings):
            rat.append(rating[0])
            years.append(rating[2])
        plt.tick_params(axis="x", which="major", labelsize=3)
        plt.figure(figsize=(15, 5))
        plt.scatter(years, rat)
        plt.xlabel("Rating")
        plt.ylabel("Time")
        plt.title("Scatterplot of " + self.name + "'s ratings")
        plt.show()


br.open("https://www.imdb.com/")
br._factory.is_html = True
br.select_form(nr=0)
person = input(
    "Please enter the names of the people who you would like to learn more about. Type 'exit' to stop "
)
while person != "exit":
    br.form["q"] = person
    br.submit()
    html = br.response().read()
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find(id="main")
    quentin = results.find("tr", class_="findResult odd")
    URL = quentin.find("a")["href"]
    category = input("Please enter a category ")
    URL = "https://www.imdb.com" + URL + "#" + category
    a = Artist(person)
    a.compileWorks(URL)
    a.returnStatistics()
    a.topMovies
    a.graph()
    person = input("Would you like to continue? Type 'exit' to stop ")
    br.open("https://www.imdb.com/")
    br._factory.is_html = True
    br.select_form(nr=0)
