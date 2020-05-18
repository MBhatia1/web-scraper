import heapq
import http.cookiejar as cookielib
import matplotlib.pyplot as plt
import mechanize
import requests
import numpy as np
from bs4 import BeautifulSoup
from collections import defaultdict
import argparse
from adjustText import adjust_text
from multiprocessing import Pool
import unicodedata
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


def generateURLS(URL, category):
    urls = []
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    director = soup.find_all(
        "div", id=lambda value: value and value.startswith(category)
    )
    for result in director:
        urls.append("https://www.imdb.com" + result.find("a")["href"])
    return urls


def getOscars(URL):
    oscars = {}
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
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
            oscars[name.text] = int(year.text[1:5])
        i = 0
        for k, v in oscars.items():
            tup = (v, outcomes[i])
            oscars[k] = tup
            i = i + 1
    return oscars


def getGenres(URL):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    info = soup.find("div", class_="title_wrapper")
    title = info.find("h1")
    title = title.text[:-7]
    t = unicodedata.normalize("NFKD", title).strip()
    rating = soup.find("span", itemprop="ratingValue")
    if rating != None:
        genres = soup.find_all("div", class_="see-more inline canwrap")
        if len(genres) != 0:
            gen = genres[len(genres) - 1].find_all("a")
            for g in gen:
                tup = (float(rating.text), t)
                return g.text.strip(), tup


def getRatings(URL):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    year = soup.find("span", id="titleYear")
    info = soup.find("div", class_="title_wrapper")
    title = info.find("h1")
    title = title.text[:-7]
    t = unicodedata.normalize("NFKD", title).strip()
    rating = soup.find("span", itemprop="ratingValue")
    if year != None and rating != None:
        year = year.find("a")
        tup = (float(rating.text), t, year.text)
        return tup


def topMovies(name, ratings, oscars):
    print(name + "'s highest rated movies on IMDb are: ")
    best_movies = heapq.nlargest(min(3, len(ratings)), ratings)
    for movie in best_movies:
        print(movie[1])
    print()
    if len(oscars) > 0:
        print(name + "'s critically acclaimed movies are: ")
        for k in oscars:
            print(k)


def returnGenres(name, genres, genre):
    movies = genres.get(genre)
    if movies != None:
        movies = heapq.nlargest(min(3, len(movies)), movies)
        print(name + "'s Top " + genre + " movies are :")
        for movie in movies:
            print(movie[1])
    else:
        print(name + " has no " + genre + " movies ")


def graph(name, ratings, oscars):
    years = []
    rat = []
    for rating in ratings:
        rat.append(rating[0])
        years.append(int(rating[2]))
    years = list(reversed(years))
    rat = list(reversed(rat))
    corr = np.corrcoef(years, rat)[0][1]
    if corr >= 0.9:
        print(name + " become better solely due to age")
    elif corr >= 0.7:
        print(name + " got significantly better with age")
    elif corr >= 0.5:
        print(name + " seems to have improved at least in part due to age")
    elif corr >= 0.3:
        print("Age might have impacted " + name + "a little bit")
    else:
        print("Age did not affect " + name + "s work at all")
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.scatter(years, rat)
    texts = []
    for rating in ratings:
        v = oscars.get(rating[1])
        if v != None:
            txt = v[1] + " , " + rating[1] + " (" + rating[2] + ")"
            texts.append(ax.text(int(rating[2]), rating[0], txt))
    adjust_text(texts)
    plt.ylabel("Rating")
    plt.xlabel("Time")
    plt.title("Scatterplot of " + name + "'s ratings")
    plt.show()


def returnStatistics(ratings, name, genres):
    num_data = []
    for rating in ratings:
        num_data.append(rating[0])
    avg = np.average(num_data)
    avg = "{:.2f}".format(avg)
    print("The average of " + name + "'s works is: " + avg)
    med = np.median(num_data)
    med = "{:.2f}".format(med)
    print("The median of " + name + "'s works is: " + med)
    std = np.std(num_data)
    std = "{:.2f}".format(std)
    print("The standard deviation of " + name + "'s works is: " + std)
    maxLen = 0
    maxGenre = ""
    for k, v in genres.items():
        if len(v) > maxLen:
            maxLen = len(v)
            maxGenre = k
    print(
        name
        + " most popular genre is "
        + maxGenre
        + ", having made "
        + str(maxLen)
        + " "
        + maxGenre
        + " films "
    )


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
URL = "https://www.imdb.com" + URL
all_urls = generateURLS(URL, category)
genr = defaultdict(list)
ratings = []
oscars = getOscars(URL)
p = Pool(10)
genre_map = p.map(getGenres, all_urls)
rating_map = p.map(getRatings, all_urls)
for genre, rating in (g for g in genre_map if g is not None):
    genr[genre].append(rating)
for tup in (t for t in rating_map if t is not None):
    ratings.append(tup)
p.close()
p.join()
if args.stats != None:
    print("------------------------------------------")
    returnGenres(person, genr, args.stats)
    print("------------------------------------------")
    print("Statistics: ")
    returnStatistics(ratings, person, genr)
    print("------------------------------------------------------------------")
    topMovies(person, ratings, oscars)
    print("---------------------------------------------")
if args.graph != None:
    graph(person, ratings, oscars)
