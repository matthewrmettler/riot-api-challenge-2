__author__ = 'Matt'
from file_calls import getMatchListByType, getSampleMatches, getAllMatches
from api_calls import getMatch, generateChampionNamesDictionary, generateListOfAPItems
import json
from pprint import pprint

rylai_id = 3116
ap_items = generateListOfAPItems()

def championWinrates(noMatches):
    champions = {}

    matches = getSampleMatches('5.11', 'RANKED_SOLO', 'BR', noMatches)
    #matches = getAllMatches('5.11', 'RANKED_SOLO', 'BR')
    print("{0} matches to analyze".format(len(matches)))
    count = 0
    for m in matches:
        with open(m, 'r') as f:
            count +=1
            if count % 50 == 0: print(count)
            temp_results = getAPChampionsByMatch(json.load(f))
            for c in temp_results:
                if c[0] not in champions:
                    champions[c[0]] = [0]*2
                if c[1] == True:
                    champions[c[0]][0] += 1
                else:
                    champions[c[0]][1] += 1
    printPrettyWinrate(champions)

def printPrettyWinrate(champ_dict):
    champ_name = generateChampionNamesDictionary()
    print("\t %-15s %5s %5s %5s" % ("Champion", "Win", "Lose", "Percent"))
    for key in champ_dict:
        win= champ_dict[key][0]
        lose= champ_dict[key][1]
        percent = round((float(win) / (float(win) + float(lose))) * 100.0,3)
        print("\t %-15s %5d %5d\t%.2f" % (champ_name[key],win, lose, percent))

def getAPChampionsByMatch(match):
    champs = []
    participants = match["participants"]
    for p in participants:
        if (builtAP(p)):
            c = []
            c.append(p["championId"])
            won = p["stats"]["winner"]
            c.append(won)
            champs.append(c)
    #print(champs)
    return(champs)

def getMidIDs(match):
    '''
    Get the participant IDs of the people who are the 'mid laners' in any given match, by iterating
    over all 10 possible 10 values, and keeping the ones whose role is mid.
    :param match: JSON object associated with a specific match.
    :return: A 2-item array containing the IDs of the mid laners (one from each team).
    '''
    midlaners = []
    for i in range(10):
        temp = getRole(match, i)
        if temp == u'MIDDLE':
            midlaners.append(i)
    return midlaners

def getRole(match, participant_id):
    '''
    getRole returns the role (as a string) associated with this participant id.
    :param match: JSON object associated with a specific match.
    :param participant_id: ID value of specific player in this match.
    :return: The role of the person with this ID.
    '''
    p = match["participants"][participant_id]

    if (p["timeline"]["role"] == u'DUO_CARRY') or (p["timeline"]["role"] == u'DUO_SUPPORT'):
        return p["timeline"]["role"]
    return p["timeline"]["lane"]

def participantHasItem(match, participant_id, item_id=rylai_id):
    p = match["participants"][participant_id]["stats"]
    for i in range(7):
        if p["item{0}".format(i)] == item_id:
            return True
    return False

def builtAP(participant):
    built_items = []
    count = 0
    for i in range(7):
        built_items.append(participant["stats"]["item{0}".format(i)])
    for item in built_items:
        if item in ap_items:
            count += 1
    if count >= 2: return True #built at least 2 ap items
    return False

def getMatchItems(match, pID):
    """
    Get the items that this particular player purchased throughout the course of the game.
    :param match: The JSON file for our match.
    :param pID: ID identifying the user (there are 10 users per match)
    :return: A dictionary containing all the items the user purchasedm, with the key being the item ID and the value
             being the quantity of that item.
    """
    #print("getMatchItems")
    summoner_items = {}

    timeline_frames = match["timeline"]["frames"]

    for frame in timeline_frames:
        if "events" in frame:
            for event in frame["events"]:
                if (event["eventType"] == "ITEM_PURCHASED") and event["participantId"] == pID:
                    item = event["itemId"]
                    if item in summoner_items:
                        summoner_items[item] += 1
                    else:
                        summoner_items[item] = 1
    return summoner_items

def buildTimelineForParticipant(match, pID):
    timeline_frames = match["timeline"]["frames"]
    timeline = []
    for frame in timeline_frames:
        if "events" in frame:
            for event in frame["events"]:

                #check for items bought
                if (event["eventType"] == "ITEM_PURCHASED") and event["participantId"] == pID:
                    timeline.append(event)

                #check for kills
                if (event["eventType"] == "CHAMPION_KILL"):
                    if ("assistingParticipantIds" in event and pID in event["assistingParticipantIds"]):
                        timeline.append(event)
                    elif ((event["killerId"] == pID) or (event["victimId"] == pID)):
                        timeline.append(event)

    return timeline

def getItemBuildersByMatch(match, item_id=rylai_id):
    builders = []
    for i in range(10):
        if participantHasItem(match, i, item_id):
            builders.append(i)
    return builders

def main():
    print("main")
    default_matches = getMatchListByType()
    small_sample = default_matches[0:25]
    for id in small_sample:
        temp_match = getMatch(id)
        temp_rylais = getItemBuildersByMatch(temp_match)
        print(len(temp_rylais))
        #for m in temp_rylais:
            #temp_timeline = buildTimelineForParticipant(temp_match, m)
            #pprint(temp_timeline)

def main2():

    championWinrates(100)

if __name__ == "__main__":
    main2()