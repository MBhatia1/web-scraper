# web-scraper
Scrapes IMDb for information about a particular artist  
After cloning the repository, simply run the following command:
 `python3 imdbScraper.py -h`. 
 Calling -h will explain in further detail how the CLI operates. As a sample  
 `python3 imdbScraper.py Stanley Kubrick director -s Drama -mg`  
 * Considers the movies **Stanley Kubrick directed** 
 * Returns statistics as the **-s** flag was specified
 * Returns his best **Drama** movies as that was the flag specified for the **-s** option
 * Returns his top movies as the **-m** flag was specified
 * Graph all of his movies, highlighting any oscar nominee/winners as the **-g** flag was specified.
 All flags are optional.
 # Note:
 Make sure you have the following libraries installed:
 * BeautifulSoup (install with `pip3 install bs4`)
 * numpy (install with `pip3 install numpy`)
 * requests (install with `pip3 install requests`)
 * mechanize (install with `pip3 install mechanize`)
 * matplotlib (install with `pip3 install matplotlib`)
 * cookiejar (install with `pip3 install cookiejar`)
 * adjustText (install with `pip3 install adjustText`)
 * argparse (install with `pip3 install argparse`)  
 
 The Web scraper might take a while, especially if its scraping a popular actor such as Tom Holland, so if the program freezes, don't worry,  its still runnning in the background
