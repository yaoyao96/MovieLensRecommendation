import os
from math import sqrt

script_dir = os.path.dirname(__file__)

print("Script_dir="+script_dir)
print("path="+ os.path.abspath(os.path.join(script_dir, '../data/u.item')))

# load data from data file
def loadMovieLens(path= script_dir):
    movies = {};
    # load movie data
    for line in open(os.path.join(path, '../data/u.item')):
        (id,title) = line.split('|')[0:2]
        movies[id] =title
    # load rating data
    prefs={};
    for line in open(os.path.join(path, '../data/u.data')):
        (user,movieid,rating,ts) = line.split('\t')
        prefs.setdefault(user,{})
        prefs[user][movies[movieid]] = float(rating)
    return prefs

def sim_pearson(prefs, p1,p2):
    si={}
    for item in prefs[p1]:
        if item in prefs[p2]: si[item] = 1

    # see if they have common item records
    n =  len(si)
    if n == 0: return 1

    # sum list of rating of common items
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])

    # sum of squre
    sum1Sq = sum([pow(prefs[p1][it], 2) for it in si ])
    sum2Sq = sum([pow(prefs[p1][it], 2) for it in si ])

    # sum of multiplication
    pSum = sum([prefs[p1][it]*prefs[p2][it] for it in si])

    num =  pSum -(sum1*sum2/n)
    denTemp = (sum1Sq - pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n)
    if denTemp < 0:
        den = -sqrt(-denTemp)
    else:
        den = sqrt(denTemp)

    if den==0: return 0

    r=num/den
    return r

# build recommandation item dict for one person by finding the similar people and calculate the weight*rating of unknown items to this person.
def getRecommendations(prefs, person, similarity=sim_pearson):
    totals = {}
    simSum = {}
    for other in prefs:
        if other==person: continue
        sim = similarity(prefs, person, other)

        if sim <= 0: continue
        for item in prefs[other]:
            if item not in prefs[person] or prefs[person][item]==0:
                totals.setdefault(item,0)
                totals[item]+= prefs[other][item]*sim
                simSum.setdefault(item,0)
                simSum[item]+=sim;

    rankings = [(total/simSum[item], item) for item,total in totals.items()]

    rankings.sort()
    rankings.reverse()
    return rankings

# change position of item and key
def transformPrefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item,{})
            result[item][person] = prefs[person][item]
    return result

# build similarity dict for 1 item return dict(r, other items)
def topMatches(prefs, person, n=5, similarity = sim_pearson):
    scores =[(similarity(prefs, person, other),other) for other in prefs if other != person]
    scores.sort()
    scores.reverse();
    return scores[0:n]

# build similarity dict for items return dict(item, dict(r, other items))
def calculateSimilarItems(prefs, n=10):
    result = {}
    itemPrefs = transformPrefs(prefs)
    c=0
    for item in itemPrefs:
        c+=1
        # words = "Item = {} Value = {}"
        # print(words.format(item, itemPrefs[item]))
        if c % 100 ==0: print("%d / %d" % (c,len(itemPrefs)))
        scores = topMatches(itemPrefs, item, n, sim_pearson)
        result[item] = scores
    return result

# rating unknown items by calculating their similarity(r)* rating of the known items
def getRecommendedItems(prefs,itemMatch, user):
    userRating = prefs[user]
    scores = {}
    totalSim = {}
    for (item, rating) in userRating.items():
        for(similarity, item2) in itemMatch[item]:
            if item2 in userRating: continue
            scores.setdefault(item2,0)
            totalSim.setdefault(item2,0)
            scores[item2] += similarity*rating
            totalSim[item2] += similarity

    rankings = [(score/totalSim[item], item) for (item, score) in scores.items()]
    rankings.sort()
    rankings.reverse()
    return rankings


prefs = loadMovieLens()
# person based recommendation
print(getRecommendations(prefs,'87'))
# item based recommendation
# find top 50 similar items for each items in dictionary by comparing items one by one
ItemSim = calculateSimilarItems(prefs,50)
print(getRecommendedItems(prefs, ItemSim, '87')[0:30]);

