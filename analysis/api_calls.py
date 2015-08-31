"""
api_calls.py
By Matthew Mettler (2015)

This python file contains all the necessary functions needed to make calls to the Riot Games API.
"""
import requests
from time import sleep
from key import key

__author__ = 'Matt'

timeout_length = 5.0


def call_api(url, call_id, param, region, attempt_no=0, print_call=False):
    """
    For ease of use, simpler API calls use this method.
    :param url: The specific type of API call being made
    :param call_id: A specific ID made for this call. Could be a summoner ID, could be a match ID, etc.
    :param param: Additional parameters that might be needed, such as 'only ranked games.'
    :param region: What region (US, EUNW, KR) to use in this call.
    :param attempt_no: Number of times this specific call has been attempted. Used to determine whether to
    determine failure and move on.
    :param print_call: Print out the actual call being made to the console (for debugging purposes). Default to False.
    :return: The requests response from the API call.
    """

    r = u"https://{0}.api.pvp.net/{1}{2}{3}{4}{5}".format(region, url, call_id, param, "api_key=", key)
    if print_call:
        print(u"CallAPI: {req}".format(req=r))
    attempt_no += 1
    try:
        call = requests.get(r, timeout=timeout_length)
    except requests.exceptions.Timeout as e:
        # Try again
        print(e)
        return call_api(url, call_id, param, attempt_no)
    except requests.exceptions.TooManyRedirects as e:
        # Tell the user their URL was bad and try a different one
        print(e)
        return 400
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        print(e)
        return 400

    if not hasattr(call, 'status_code'):
        return call_api(url, call_id, param, attempt_no)

    if call.status_code == 200:  # Everything's fine
        return call
    else:
        print(call.status_code)
        print(call.headers)
        if attempt_no >= 8:  # if it doesnt work after 8 tries, give up
            return call
        if call.status_code == 400:
            # Bad request -- something is wrong with my code, show an error, DO NOT keep making calls
            return 400
        if call.status_code == 401:
            # Unauthorized -- my api key isn't valid, show a page for this
            return 401
        if call.status_code == 404:
            # item not found -- do something about this
            return 404
        if call.status_code == 429:
            # Rate limit exceeded -- wait a few seconds
            if 'Retry-After' in call.headers:
                print("retry-after: {rt} ".format(rt=call.headers['Retry-After']))
                sleep(float(call.headers['Retry-After']))
            else:
                sleep(1.2)
            return call_api(url, call_id, param, attempt_no)
        if call.status_code == 500:  # Internal server error -- something wrong on riot's end -- wait?
            sleep(1.2)
            return call_api(url, call_id, param, attempt_no)
        if call.status_code == 503:  # service unavailable -- something wrong on riot's end
            sleep(1.2)
            return call_api(url, call_id, param, attempt_no)


def generate_champion_name_dictionary():
    """
    Generates a dictionary, where the key-value pair is {id : name}. All data stored in match data is given with
    'championId', an integer, so this provides an easy way to translate that ID into the name of the champion.
    :return: A dictionary, where the key-value pair is {id : name}.
    """
    champ_dict = {}
    r = requests.get("http://ddragon.leagueoflegends.com/cdn/5.16.1/data/en_US/champion.json")
    call = r.json()
    champ_names = call["data"].keys()
    data = call["data"]
    for c in champ_names:
        name = c
        champ_id = int(data[c]["key"])
        champ_dict[champ_id] = name

    return champ_dict


def generate_ap_item_name_dictionary():
    item_dict = {}
    ap_item_ids = generate_list_of_ap_items()[0]

    call = requests.get("http://ddragon.leagueoflegends.com/cdn/5.14.1/data/en_US/item.json")
    r = call.json()
    data = r["data"]
    for item in ap_item_ids:
        if str(item) in data:
            item_dict[item] = data[str(item)]["name"]
    return item_dict


def generate_list_of_ap_items():
    """
    Generates a list of item IDs that are associated with 'Ability Power' items, by looking through the statuc item
    file and finding all items that have a "SpellDamage" tag.
    :return: An array of integers, each integer being the id of an item.
    """
    ap_items = []
    core_ap_items = []
    for patch in ['5.11', '5.14']:
        call = requests.get("http://ddragon.leagueoflegends.com/cdn/{p}.1/data/en_US/item.json".format(p=patch))
        r = call.json()
        data = r["data"]
        items = data.keys()
        for i in items:
            if "SpellDamage" in data[i]["tags"]:
                ap_items.append(int(i))
                if "into" in data[i] and "from" in data[i]:
                    if (len(data[i]["into"]) == 0) and (len(data[i]["from"]) >= 1):
                        core_ap_items.append(int(i))
    return [ap_items, core_ap_items]


def get_match(match_id, region):
    """
    Load a specific match with its map ID.
    :param match_id: The ID identifying the specific match we're trying to look at.
    :return: A json object representing the match, or an error code representing that it wasn't found.
    """
    match_call = call_api("api/lol/{r}/v2.2/match/".format(r=region.lower()), match_id,
                          "?includeTimeline=true&", region.lower())
    if isinstance(match_call, int):
        return match_call
    return match_call.json()
