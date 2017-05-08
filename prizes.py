# -*- coding: utf-8 -*-
"""
Created on Sun Apr 23 19:12:11 2017
@author: Oore
"""
from bs4 import BeautifulSoup
import requests

class Game:
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
    
    
class Prize(Game):
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
        all_lottodata.append(g)
        
        
        p = requests.get(g.more)
        newsoup = BeautifulSoup(p.text,'lxml')
        prizes_table = newsoup.find('table',class_='draw_games tag_even')
        allprizes = prizes_table.findAll('tr')
        
        g.prizes=[]
        for prize in allprizes:
            if len(prize) ==5:
                pdata = prize.findAll('td')
                
                if all(char.isalpha() for char in str(pdata[0].text.strip()) ):
                    p=Prize()
                    p.amount = str(pdata[0].text.strip()).replace(',','')
                    p.odds = int(str(pdata[1].text.strip()).replace(',',''))
                    p.winners = int(str(pdata[2].text.strip()).replace(',',''))
                    p.claimed = int(str(pdata[3].text.strip()).replace(',',''))
                    p.available = int(str(pdata[4].text.strip()).replace(',',''))
                    g.prizes.append(p)
                else:
                    p = Prize()
                    p.amount = int(str(pdata[0].text.strip()).replace(',','')[1:])
                    p.odds = int(str(pdata[1].text.strip()).replace(',',''))
                    p.winners = int(str(pdata[2].text.strip()).replace(',',''))
                    p.claimed = int(str(pdata[3].text.strip()).replace(',',''))
                    p.available = int(str(pdata[4].text.strip()).replace(',',''))
                    g.prizes.append(p)

"""for x in all_lottodata:#Just some code to test out the classes and loops. Will be removed before final version.
    print(x.name)
    print(x.overall)
    for y in x.prizes:
        print (y.amount)"""

all_lottodata = [x for x in all_lottodata if x.name]

rows = []
for x in all_lottodata:
    for y in x.prizes:
        rows.append([x.name, y.amount, y.odds, y.winners, y.claimed,y.available, x.price])
        
        
class Ticket:
    name = ''
    prizes =[]
    expected_value=0
    new_expected_value = 0 
    value_change = 0
    price = 0
    prob = 0
    N=0
    n=0
    def predcount(self):
        N = sum(prize['total_winners'] for prize in self.prizes)/sum(prize['probability'] for prize in self.prizes)
        n = sum(prize['available'] for prize in self.prizes)/sum(prize['probability'] for prize in self.prizes)
        self.n = n
        self.N = N
        return(self)

    def new_prizes(self):
        for prize in self.prizes:
            prize['new_probability'] = prize['available']/self.n
        return(self)

tickets = []
def info(data):
    names =[]
    for row in rows:
        names.append((row[0],row[6]))
    names = set(names)
    for name in names:
        t=Ticket()
        t.name = name[0]
        t.price = int(name[1])
        tickets.append(t)
    return(tickets)

def prizes(lst, data):
    tickets=[]
    for ticket in lst:
        ticketdata = list(filter(lambda x: x[0]==ticket.name and x[6] == ticket.price,data))
        prizes=[]
        for row in ticketdata:
            try:
                prize = {'prize':int(row[1]),'probability':1/int(row[2]),'total_winners':int(row[3]),'claimed':int(row[4]), 'available':int(row[5])}
            except:
                prize = {'prize':row[1],'probability':1/int(row[2]),'total_winners':int(row[3]),'claimed':int(row[4]), 'available':int(row[5])}
            prizes.append(prize)
        ticket.prizes = prizes
        tickets.append(ticket)
    return(tickets)

def ev(item):
    prize_probs = []
    for prize in item.prizes:
        prize_prob = (prize['prize'],prize['probability'])
        prize_probs.append(prize_prob)
    initev = sum(i[0]*i[1] for i in prize_probs if i[0] != 'Ticket')
    if prize_probs[-1][0]=='Ticket':
        ticketprize = prize_probs[-1] 
        ticketprizevalue_wght = 1/(1/ticketprize[1]-1)
        item.expected_value= (initev+ticketprizevalue_wght*initev)/item.price
    else:
        item.expected_value = initev/item.price
    return(item)

def newev(item):
    prize_probs = []
    for prize in item.prizes:
        prize_prob = (prize['prize'],prize['new_probability'])
        prize_probs.append(prize_prob)
    initev = sum(i[0]*i[1] for i in prize_probs if i[0] != 'Ticket')
    if prize_probs[-1][0]=='Ticket':
        ticketprize = prize_probs[-1] 
        ticketprizevalue_wght = 1/(1/ticketprize[1]-1)
        item.new_expected_value= (initev+ticketprizevalue_wght*initev)/item.price
    else:
        item.new_expected_value = initev/item.price
    return(item)

def deltavalue(item):
    old=item.expected_value
    new=item.new_expected_value
    item.valuechange = (new-old)/old
    return(item)
                       
ticketlists = info(rows)
ticketlists = prizes(ticketlists,rows)
ticketlists = [ev(ticket) for ticket in ticketlists]
ticketlists = [t.predcount() for t in ticketlists]
ticketlists = [t.new_prizes() for t in ticketlists]
ticketlists = [newev(ticket) for ticket in ticketlists]
ticketlists = [deltavalue(ticket) for ticket in ticketlists]


for ticket in ticketlists:
    change = str(ticket.valuechange*100)
    print (ticket.name, change+"%", ticket.price)
