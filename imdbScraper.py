import heapq
import http.cookiejar as cookielib
import matplotlib.pyplot as plt
import mechanize
import requests
import numpy as np
from bs4 import BeautifulSoup
from collections import defaultdict
import argparse

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
        self.oscars = {}
        self.genres = defaultdict(list)

    def compileWorks(self, URL):
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        director = soup.find_all(
            "div", id=lambda value: value and value.startswith(category)
        )
        oscar = soup.find("div", class_="article highlighted")
        if oscar != None:
            url = oscar.find("a")["href"]
            url = "https://www.imdb.com" + url
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")
            tb = soup.find("table", class_="awards")
            movies = tb.find_all("td", class_="award_description")
            award_outcomes = tb.find_all("td", class_="award_outcome")
            outcomes = []
            for outcome in award_outcomes:
                outcomes.append(outcome.find("b").text)
            for movie in movies:
                name = movie.find("a")
                year = movie.find("span", class_="title_year")
                if name == None or year == None:
                    continue
                self.oscars[name.text] = int(year.text[1:5])
            i = 0
            for k, v in self.oscars.items():
                tup = (v, outcomes[i])
                self.oscars[k] = tup
                i = i + 1
        for result in director:
            title = result.find("a")
            url = result.find("a")["href"]
            url = "https://www.imdb.com" + url
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")
            rating = soup.find("span", itemprop="ratingValue")
            if rating == None:
                continue
            results = soup.find(id="titleStoryLine")
            genres = results.find_all("div", class_="see-more inline canwrap")
            if len(genres) == 0:
                continue
            gen = genres[len(genres) - 1].find_all("a")
            for g in gen:
                tup = (float(rating.text), title.text)
                self.genres[g.text.strip()].append(tup)
            year = soup.find("span", id="titleYear")
            if year == None:
                continue
            year = year.find("a")
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
        maxLen = 0
        maxGenre = ""
        for k, v in self.genres.items():
            # movies = self.genres.get(k)
            if len(v) > maxLen:
                maxLen = len(v)
                maxGenre = k

        print(
            self.name
            + " most popular genre is "
            + maxGenre
            + ", having made "
            + str(maxLen)
            + " "
            + maxGenre
            + " films "
        )

    def topMovies(self):
        heapq.heapify(self.ratings)
        print(self.name + "'s highest rated movies on IMDb are: ")
        best_movies = heapq.nlargest(min(3, len(self.ratings)), self.ratings)
        for movie in best_movies:
            print(movie[1])
        if len(self.oscars) > 0:
            print(self.name + "'s critically acclaimed movies are: ")
            for k in self.oscars:
                print(k)

    def graph(self):
        years = []
        rat = []
        for rating in self.ratings:
            rat.append(rating[0])
            years.append(int(rating[2]))
        years = list(reversed(years))
        rat = list(reversed(rat))
        corr = np.corrcoef(years, rat)[0][1]
        if corr >= 0.9:
            print(self.name + " become better solely due to age")
        elif corr >= 0.7:
            print(self.name + " got significantly better with age")
        elif corr >= 0.5:
            print(self.name + " seems to have improved at least in part due to age")
        elif corr >= 0.3:
            print("Age might have impacted " + self.name + "'s a little bit")
        else:
            print("Age did not affect " + self.name + "s work at all")
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.scatter(years, rat)
        for rating in self.ratings:
            v = self.oscars.get(rating[1])
            if v != None:
                ax.annotate(v[1] + " , " + rating[1], (int(rating[2]), rating[0]))
        plt.ylabel("Rating")
        plt.xlabel("Time")
        plt.title("Scatterplot of " + self.name + "'s ratings")
        plt.show()

    def returnGenres(self, genre):
        movies = self.genres.get(genre)
        if movies != None:
            movies = heapq.nlargest(min(3, len(movies)), movies)
            print(self.name + "'s Top " + genre + " movies are :")
            for movie in movies:
                print(movie[1])
        else:
            print(self.name + " has no " + genre + " movies ")


parser = argparse.ArgumentParser(
    description="A web scraper that takes an artist and returns information from IMDb about them"
)
parser.add_argument(
    "firstName",
    type=str,
    help="The first name of the artist you would like to know more about. eg. Tom Holland",
)
parser.add_argument(
    "lastName",
    type=str,
    help="The last name of the artist you would like to know more about. eg. Tom Holland",
)
parser.add_argument("category", type=str, help="What type of artist they are eg. Actor")
parser.add_argument(
    "-s",
    "--stats",
    help="Enter if you want stats about the artist, followed by a genre the artist might be known for",
)
parser.add_argument(
    "-m",
    "--movies",
    help="Enter if you want to know the top movies about the arist",
    action="store_true",
)
parser.add_argument(
    "-g",
    "--graph",
    help="Enter if you want to see the artist's ratings plotted on a graph",
    action="store_true",
)
args = parser.parse_args()
br.open("https://www.imdb.com/")
br._factory.is_html = True
br.select_form(nr=0)
person = args.firstName + " " + args.lastName
br.form["q"] = person
br.submit()
html = br.response().read()
soup = BeautifulSoup(html, "html.parser")
results = soup.find(id="main")
quentin = results.find("tr", class_="findResult odd")
URL = quentin.find("a")["href"]
category = args.category.lower()
URL = "https://www.imdb.com" + URL + "#" + category
a = Artist(person)
a.compileWorks(URL)
if args.stats != None:
    print("------------------------------------------")
    a.returnGenres(args.stats)
    print("------------------------------------------")
    print("Statistics: ")
    a.returnStatistics()
    print("------------------------------------------------------------------")
if args.movies != None:
    a.topMovies()
    print("---------------------------------------------")
if args.graph != None:
    a.graph()
