__author__ = 'Matt'
from file_calls import get_match_list_by_type, get_sample_matches
from api_calls import get_match, generate_champion_name_dictionary, generate_list_of_ap_items
import json

rylai_id = 3116
[ap_items, core_ap_items] = generate_list_of_ap_items()

def display_champion_winrates(match_count):
    """
    Prints out a pretty grid of the win rates of various champions, gained from the number of random matches it was
    asked to get.
    :param match_count: How many matches to look at.
    :return: Nothing. Prints out the results.
    """
    champions = {}

    matches = get_sample_matches('5.11', 'RANKED_SOLO', 'BR', match_count)
    # matches = get_all_matches('5.11', 'RANKED_SOLO', 'BR')
    count = 0
    for m in matches:
        count +=1
        if count % 50 == 0: print(count)
        temp_results = get_ap_champions_by_match(open_match(m))
        for c in temp_results:
            if c[0] not in champions:
                champions[c[0]] = [0]*2
            if c[1] == True:
                champions[c[0]][0] += 1
            else:
                champions[c[0]][1] += 1
    pprint_winrate(champions)

def calculate_frequency_of_roles(noMatches):
    '''
    Determines how frequent AP champions are picked in the top lane, middle lane, and in the jungle.
    :param noMatches: Number of matches to look at.
    :return: An array of size 3, corresponding to [top, middle, jungle], where each index contains an array of size 2,
    corresponding to [number of ap champions, number of non-ap champions].
    '''
    top = [0, 0]
    middle = [0, 0]
    jungle = [0, 0]
    matches = get_sample_matches('5.11', 'RANKED_SOLO', 'BR', noMatches)
    #matches = get_all_matches('5.11', 'RANKED_SOLO', 'BR')
    count = 0
    for m in matches:
        count +=1
        if count % 50 == 0: print(count)
        match = open_match(m)
        participants = match["participants"]
        for p in participants:
                r = p["timeline"]["lane"]
                if r == u'JUNGLE':
                    if participant_built_AP(p):  jungle[0] += 1
                    else:           jungle[1] += 1
                if r == u'MIDDLE':
                    if participant_built_AP(p):  middle[0] += 1
                    else:           middle[1] += 1
                if r == u'TOP':
                    if participant_built_AP(p):  top[0] += 1
                    else:           top[1] += 1
    print(top)
    print(middle)
    print(jungle)
    return [top, middle, jungle]

def was_rylais_built(match, participant):
    return participant_has_item(match, participant)

def core_item_build_order(match, pID):
    item_timeline = build_timeline_for_participant(match, pID, True, False)
    core_items_built = get_core_ap_items_built(match["participants"][pID])
    pass

def open_match(m):
    with open(m, 'r') as f:
        return json.load(f)

def pprint_winrate(champ_dict):
    champ_name = generate_champion_name_dictionary()
    print("\t %-15s %5s %5s %5s" % ("Champion", "Win", "Lose", "Percent"))
    for key in champ_dict:
        win= champ_dict[key][0]
        lose= champ_dict[key][1]
        percent = round((float(win) / (float(win) + float(lose))) * 100.0,3)
        print("\t %-15s %5d %5d\t%.2f" % (champ_name[key],win, lose, percent))

def get_ap_champions_by_match(match):
    champs = []
    participants = match["participants"]
    for p in participants:
        if (participant_built_AP(p)):
            c = []
            c.append(p["championId"])
            won = p["stats"]["winner"]
            c.append(won)
            champs.append(c)
    #print(champs)
    return(champs)

def get_role(match, participant_id):
    """
    get_role returns the role (as a string) associated with this participant id.
    :param match: JSON object associated with a specific match.
    :param participant_id: ID value of specific player in this match.
    :return: The role of the person with this ID.
    """
    p = match["participants"][participant_id]

    if (p["timeline"]["role"] == u'DUO_CARRY') or (p["timeline"]["role"] == u'DUO_SUPPORT'):
        return p["timeline"]["role"]
    return p["timeline"]["lane"]

def participant_has_item(match, participant_id, item_id=rylai_id):
    p = match["participants"][participant_id]["stats"]
    for i in range(7):
        if p["item{0}".format(i)] == item_id:
            return True
    return False

def get_core_ap_items_built(participant):
    built_items = []
    count = 0
    core = []
    for i in range(7):
        built_items.append(participant["stats"]["item{0}".format(i)])
    for item in built_items:
        if item in core_ap_items:
            core.append(item)
    return core

def participant_built_AP(participant):
    """
    This function checks whether this participant built AP items. The threshold is that if at least two items were built
    that qualifies as AP, then they 'built AP.'
    :param participant: The participant in question.
    :return: True if they 'built AP', false if they did not.
    """
    built_items = []
    count = 0
    for i in range(7):
        built_items.append(participant["stats"]["item{0}".format(i)])
    for item in built_items:
        if item in ap_items:
            count += 1
    if count >= 2: return True #built at least 2 ap items
    return False

def build_timeline_for_participant(match, pID, includeItems=True, includeKills=True):
    timeline_frames = match["timeline"]["frames"]
    timeline = []
    for frame in timeline_frames:
        if "events" in frame:
            for event in frame["events"]:

                #check for items bought
                if (includeItems):
                    if (event["eventType"] == "ITEM_PURCHASED") and event["participantId"] == pID:
                        timeline.append(event)

                #check for kills
                if (includeKills):
                    if (event["eventType"] == "CHAMPION_KILL"):
                        if ("assistingParticipantIds" in event and pID in event["assistingParticipantIds"]):
                            timeline.append(event)
                        elif ((event["killerId"] == pID) or (event["victimId"] == pID)):
                            timeline.append(event)

    return timeline

def get_item_builders_by_match(match, item_id=rylai_id):
    builders = []
    for i in range(10):
        if participant_has_item(match, i, item_id):
            builders.append(i)
    return builders

def main():
    print("main")
    default_matches = get_match_list_by_type()
    small_sample = default_matches[0:25]
    for id in small_sample:
        temp_match = get_match(id)
        temp_rylais = get_item_builders_by_match(temp_match)
        print(len(temp_rylais))
        #for m in temp_rylais:
            #temp_timeline = build_timeline_for_participant(temp_match, m)
            #pprint(temp_timeline)

def main2():
    calculate_frequency_of_roles(5)
    #display_champion_winrates(100)

if __name__ == "__main__":
    main2()