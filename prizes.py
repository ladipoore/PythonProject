# -*- coding: utf-8 -*-
"""
Created on Sun Apr 23 19:12:11 2017
@author: Oore
"""
from bs4 import BeautifulSoup
import requests

class Game(object):
    price = 0
    num = 0
    name = ""
    top_prize = 0
    all_winners = 0
    claimed = 0
    available = 0
    more = ""
    prizes =[]
    overall = {}
    
    
class Prize(object):
    amount =0
    odds = 0
    winners =0
    claimed =0
    available = 0
    
    
    
prizes_url='http://www.calottery.com/play/scratchers-games/top-prizes-remaining'
all_lottodata =[]

#Will be put into a module to extract the relevant data from the website whenever the program is called
#or maybe not. 
r = requests.get(prizes_url)
soup = BeautifulSoup(r.text,"lxml")
data_table = soup.find('table',id='topprizetable')
rows = data_table.findAll('tr')

for row in rows:
    if len(row) != 8:
        continue
    else:
        cells = row.findAll('td')
        g = Game()
        g.price = int(str(cells[0].text.strip())[1:]) #convert to text, strip dollar sign and convert to int
        g.num = int(cells[1].text.strip())
        g.name = cells[2].text.strip()
        g.top_prize = int(str(cells[3].text.strip()).replace(',','')[1:]) #convert from currency
        g.all_winners = int(cells[4].text.strip().replace(',',''))
        g.claimed = int(cells[5].text.strip().replace(',',''))
        g.available = int(cells[6].text.strip().replace(',',''))
        g.more = 'http://www.calottery.com'+str(cells[7].find('a')['href']) #explore this link for more information on all the prizes.
        g.overall = {}
        all_lottodata.append(g)
        
        
        p = requests.get(g.more)
        newsoup = BeautifulSoup(p.text,'lxml')
        prizes_table = newsoup.find('table',class_='draw_games tag_even')
        allprizes = prizes_table.findAll('tr')
        
        for prize in allprizes:
            if len(prize) ==5:
                pdata = prize.findAll('td')
                
                if all(char.isalpha() for char in str(pdata[0].text.strip()) ):
                    g.overall['Odds']= int(str(pdata[1].text.strip()).replace(',',''))
                    g.overall['Winners']= int(str(pdata[2].text.strip()).replace(',',''))
                    g.overall['Pwon'] = int(str(pdata[3].text.strip()).replace(',',''))
                    g.overall['Pavail'] = int(str(pdata[4].text.strip()).replace(',',''))
                else:
                    p = Prize()
                    p.amount = int(str(pdata[0].text.strip()).replace(',','')[1:])
                    p.odds = int(str(pdata[1].text.strip()).replace(',',''))
                    p.winners = int(str(pdata[2].text.strip()).replace(',',''))
                    p.claimed = int(str(pdata[3].text.strip()).replace(',',''))
                    p.available = int(str(pdata[4].text.strip()).replace(',',''))
                    
                    g.prizes.append(p)

for x in all_lottodata:#Just some code to test out the classes and loops. Will be removed before final version.
    #print(x.name)
    #print(x.overall)
    print(x.more)
    #print (len(x.prizes))
    #for v in x.prizes:
        #print(v.amount)
    break
    #Note: The ticket "Super Ticket" does not have a summary line on their website sometimes so it might return an empty dict which should be ignored.