__author__ = 'Matt'
from file_calls import get_match_list_by_type, get_sample_matches, open_match
from api_calls import get_match, generate_champion_name_dictionary, \
    generate_list_of_ap_items, generate_ap_item_name_dictionary


#  rylai's item IDs
giants_belt_id = 1011
nlr_id = 1058
rylais_id = 3116

[ap_items, core_ap_items] = generate_list_of_ap_items()

champion_name_dict = generate_champion_name_dictionary()
ap_items_name_dict = generate_ap_item_name_dictionary()


#  Profile class methods


class Profile():
    """
    An outline of everything I want from the analysis.
    Using various function calls, fill out all these values, then build a database storing thousands of these
    for analysis.
    """
    def __init__(self, champ_id, patch, region, queue):
        self.champ_id = champ_id
        self.patch = patch
        self.region = region
        self.queue = queue

        # initialize just in case
        self.result = None
        self.kills = 0
        self.deaths = 0
        self.assists = 0
        self.final_build = []
        self.build_order = []
        self.shopping_trips = None
        self.damage_done = 0
        self.damage_taken = 0
        self.has_rylais = False
        self.rylais_order = -1

    def stats(self, result, kills, deaths, assists, final_build, build_order, shopping_trips, damage_done,
              damage_taken, has_rylais, rylais_order):
        self.result = result
        self.kills = kills
        self.deaths = deaths
        self.assists = assists
        self.final_build = final_build
        self.build_order = build_order
        self.shopping_trips = shopping_trips
        self.damage_done = damage_done
        self.damage_taken = damage_taken
        self.has_rylais = has_rylais
        self.rylais_order = rylais_order


def generate_profiles(match_count):
    match_type = ['5.11', 'RANKED_SOLO', 'BR']
    matches = get_sample_matches(match_type[0], match_type[1], match_type[2], match_count)
    # matches = get_all_matches('5.11', 'RANKED_SOLO', 'BR')
    count = 0
    profiles = []
    for m in matches:
        match = open_match(m)
        count += 1
        if count % 50 == 0:
            print(count)
        ap_champions = list_of_ap_participants(match)
        for champ in ap_champions:
            profiles.append(build_profile(match, match_type, champ))

    print(len(profiles))
    pass


def build_profile(match, match_type, participant_id):
    p = participant_frame(match, participant_id)
    champ_id = p["championId"]
    # Initialize Profile class with champion type and match type info
    champion = Profile(champ_id, match_type[0], match_type[1], match_type[2])
    get_profile_stats(champion, match, participant_id)
    return champion


def get_profile_stats(profile, match, participant_id):
    # initialize needed variables
    p = participant_frame(match, participant_id)
    stats = p["stats"]
    f_build = final_build(p)
    build_order = core_item_build_order(match, participant_id)[1]
    shopping_trips = generate_shopping_trips(match, participant_id)

    # handle rylai's stuff
    has_rylais = False
    rylais_order = 0

    if was_rylais_built(p):
        for i in range(len(build_order)):
            if build_order[i] == rylais_id:
                has_rylais = True
                rylais_order = i+1

    # fill out stats
    profile.stats(stats["winner"], stats["kills"], stats["deaths"], stats["assists"], f_build, build_order,
                  shopping_trips, stats["totalDamageDealtToChampions"], stats["totalDamageTaken"], has_rylais,
                  rylais_order)
    return

#  Display methods


def display_champion_win_rates(match_count):
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
        count += 1
        if count % 50 == 0:
            print(count)
        temp_results = get_ap_champions_by_match(open_match(m))
        for c in temp_results:
            if c[0] not in champions:
                champions[c[0]] = [0]*2
            if c[1]:
                champions[c[0]][0] += 1
            else:
                champions[c[0]][1] += 1
    pprint_win_rate(champions)


def display_core_item_build_orders(match_count):
    """
    This function pulls a sample of match data and displays a core item build order for people who build AP.
    :param match_count: The number of matches to sample.
    :return: Nothing. Only prints data.
    """

    matches = get_sample_matches('5.11', 'RANKED_SOLO', 'BR', match_count)
    # matches = get_all_matches('5.11', 'RANKED_SOLO', 'BR')
    # count = 0
    for m in matches:
        match = open_match(m)
        '''
        count += 1
        if count % 50 == 0:
            print(count)
        '''
        ap_participants = list_of_ap_participants(match)
        for participant_id in ap_participants:
            res = core_item_build_order(match, participant_id)
            printable_build_order = [ap_items_name_dict[x] for x in res[1]]
            print("{champ} : {item}".format(champ=res[0], item=printable_build_order))


def pprint_win_rate(champ_dict):
    """
    Prints a pretty version of the win rate dictionary to the console.
    :param champ_dict: The results gathered that we're trying to print.
    :return: Nothing. This simply prints to the console.
    """

    print("\t %-15s %5s %5s %5s" % ("Champion", "Win", "Lose", "Percent"))
    for key in champ_dict:
        win = champ_dict[key][0]
        lose = champ_dict[key][1]
        percent = round((float(win) / (float(win) + float(lose))) * 100.0, 2)
        print("\t %-15s %5d %5d\t%.2f" % (champion_name_dict[key], win, lose, percent))


def calculate_frequency_of_roles(match_count):
    """
    Determines how frequent AP champions are picked in the top lane, middle lane, and in the jungle.
    :param match_count: Number of matches to look at.
    :return: An array of size 3, corresponding to [top, middle, jungle], where each index contains an array of size 2,
    corresponding to [number of ap champions, number of non-ap champions].
    """

    top = [0, 0]
    middle = [0, 0]
    jungle = [0, 0]
    matches = get_sample_matches('5.11', 'RANKED_SOLO', 'BR', match_count)
    # matches = get_all_matches('5.11', 'RANKED_SOLO', 'BR')
    count = 0
    for m in matches:
        count += 1
        if count % 50 == 0:
            print(count)
        match = open_match(m)
        participants = match["participants"]
        for p in participants:
                r = p["timeline"]["lane"]

                if r == u'JUNGLE':
                    if participant_built_ap(p):
                        jungle[0] += 1
                    else:
                        jungle[1] += 1

                elif r == u'MIDDLE':
                    if participant_built_ap(p):
                        middle[0] += 1
                    else:
                        middle[1] += 1

                elif r == u'TOP':
                    if participant_built_ap(p):
                        top[0] += 1
                    else:
                        top[1] += 1
    print(top)
    print(middle)
    print(jungle)
    return [top, middle, jungle]


#  Build order and item build methods


def core_item_build_order(match, participant_id):
    """
    Generates the order in which a participant finishes core AP items.
    :param match: The match in question (JSON file)
    :param participant_id: The participant in question.
    :return: A 2-item array, ['champion name', 'items built'], where 'items built' is also an array.
    """
    build_order = []
    item_timeline = build_timeline_for_participant(match, participant_id, True, False)
    core_items_built = get_core_ap_items_built(match["participants"][participant_id-1])
    champion_name = champion_name_dict[int(match["participants"][participant_id-1]["championId"])]
    # print(core_items_built)
    for event in item_timeline:
        for item in core_items_built:
            if int(event['itemId']) == item:
                if item not in build_order:  # avoid duplicates due to selling or re-buying
                    build_order.append(item)

    return [champion_name, build_order]


def participant_has_item(participant, item_id=rylais_id):
    """
    Checks whether a particular item was built.
    :param participant: The participant in question.
    :param item_id: The ID associated with the item in question. Defaults to Rylai's Crystal Scepter (the main focus of
    this project.)
    :return: True if the item was in the final build, False if not.
    """
    built_items = final_build(participant)
    for item in built_items:
        if item == item_id:
            return True
    return False


def final_build(participant):
    """
    Retrieves the final 7 items a participant built.
    :param participant: The person whose final build we want to see.
    :return: A 7 item array of integers
    """
    built_items = []

    for i in range(7):
        built_items.append(participant["stats"]["item{0}".format(i)])
    return built_items


def participant_built_ap(participant):
    """
    This function checks whether this participant built AP items. The threshold is that if at least two items were built
    that qualifies as AP, then they 'built AP.'
    :param participant: The participant in question.
    :return: True if they 'built AP', false if they did not.
    """
    built_items = final_build(participant)
    count = 0
    for item in built_items:
        if item in ap_items:
            count += 1
    if count >= 2:  # built at least 2 ap items
        return True
    return False


def get_core_ap_items_built(participant):
    """
    Gets a list of core AP items that the participant built.
    :param participant: The particular participant whose items we want to know.
    :return: An array of item IDs identifying what items he bought.
    """
    built_items = final_build(participant)
    core = []

    for item in built_items:
        if item in core_ap_items:
            core.append(item)
    return core


def get_item_builders_by_match(match, item_id=rylais_id):
    """
    Returns a list of participants (by id) that built a specific item.
    :param match: A json file of the match.
    :param item_id: the item ID to search for in that match.
    :return: An array of participant IDs.
    """
    builders = []
    for participant_id in range(10):
        if participant_has_item(match["participants"][participant_id-1], item_id):
            builders.append(participant_id)
    return builders


# Shopping Trip stuff


class ShoppingTrip():
        def __init__(self, items_bought, timestamp, order):
            self.items = items_bought
            self.time = timestamp
            self.order = order


class ItemPurchases():
    def __init__(self, champion, match_id, purchases):
        self.champion = champion
        self.matchId = match_id
        self.purchases = purchases


def generate_shopping_trips(match, participant_id):
    """
    This method modifies the class to show what kind of shopping trips a champion took over the course of the game.
    :param match: The match in question.
    :param participant_id: The person who we're looking at.
    :return: None, modifies the instance of the class.
    """
    item_buy_threshold = 15000  # How many milliseconds in between purchases for one trip
    item_timeline = build_timeline_for_participant(match, participant_id, True, False)

    purchases = []
    count = 0
    last_purchase_timestemp = item_timeline[0]["timestamp"]
    items_bought = []
    times_bought = []
    for purchase in item_timeline:
        if int(purchase["timestamp"]) - last_purchase_timestemp >= item_buy_threshold:
            trip = ShoppingTrip(items_bought, sum(times_bought) / float(len(times_bought)), count)

            #  reset everything, increment count for next trip
            count += 1
            purchases.append(trip)
            items_bought = []
            times_bought = []

        items_bought.append(purchase["itemId"])
        times_bought.append(purchase["timestamp"])
        last_purchase_timestemp = purchase["timestamp"]

    p = participant_frame(match, participant_id)
    champ_id = p["championId"]
    return ItemPurchases(champ_id, match["matchId"], purchases)


#  Rylai's methods


def was_rylais_built(participant):
    """
    Checks whether Rylai's was built.
    :param participant: The participant's JSON data.
    :return: True if it was built, false otherwise.
    """
    return participant_has_item(participant)


#  Champion methods


def participant_frame(match, participant_id):
    """
    Helper method to get the dictionary associated with a participant in a specific match.
    :param match: The match in question
    :param participant_id: The id associated with the participant.
    :return: A dictionary with the contents of that participant.
    """
    return match["participants"][participant_id-1]


def get_ap_champions_by_match(match):
    """
    Gets a list of champions who built AP in a particular match.
    :param match: The specific match to look at.
    :return: An array of champions who built AP, and whether they won.
    """
    champion_list = []
    participants = match["participants"]
    for p in participants:
        if participant_built_ap(p):
            # Found a player who built AP. Include the champion's ID and whether they won.
            ap_champ = [p["championId"], p["stats"]["winner"]]
            champion_list.append(ap_champ)
    return champion_list


def list_of_ap_participants(match):
    """
    This function returns a list of participant IDs who built AP in a given match.
    :param match: A JSON file representing a match.
    :return: An array of integers representing IDs of participants who built AP items.
    """
    ap_participants = []
    participants = match["participants"]
    for p in participants:
        if participant_built_ap(p):
            # Found a player who built AP. Include the champion's ID and whether they won.
            ap_participants.append(p["participantId"])
    # print(ap_participants)
    return ap_participants


def build_timeline_for_participant(match, participant_id, include_items=True, include_kills=True):
    """
    Builds a timeline (a list of events) for a specific participant in a specific match.
    :param match: What match to parse (a json file)
    :param participant_id: What participant to look at.
    :param include_items: Whether or not to include item purchases in the timeline.
    :param include_kills: Whether or not in to include kills, deaths, or assists in the timeline.
    :return: An array of events (dictionary objects describing an event that happened).
    """
    timeline_frames = match["timeline"]["frames"]
    timeline = []
    for frame in timeline_frames:
        if "events" in frame:
            for event in frame["events"]:

                # Check for items bought.
                if include_items:
                    if (event["eventType"] == "ITEM_PURCHASED") and event["participantId"] == participant_id:
                        timeline.append(event)

                # Check for kills.
                if include_kills:
                    if event["eventType"] == "CHAMPION_KILL":
                        if "assistingParticipantIds" in event and participant_id in event["assistingParticipantIds"]:
                            timeline.append(event)
                        elif event["killerId"] == participant_id or event["victimId"] == participant_id:
                            timeline.append(event)

    return timeline


#  main method
def main():
    generate_profiles(1)


if __name__ == "__main__":
    main()