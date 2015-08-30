__author__ = 'Matt'
from api_calls import get_match
import os
import json
import glob
import random


def root_dir():
    """
    Gets the root directory in absolute terms.
    :return: A string containing the absolute path to the directory of this file.
    """
    return os.path.abspath(os.path.dirname(__file__))


def verify(patch, queue, region):
    """
    Verifies whether these parameters are valid when trying to access a match.
    :param patch: What patch the match was played on.
    :param queue: What queue type (ranked or solo) the match was played on.
    :param region: What region (NA, KR, BR, etc.) the match was played in.
    :return: True if the parameters are valid, False if not.
    """
    if patch not in ['5.11', '5.14']:
        return False
    if queue not in ['RANKED_SOLO', 'NORMAL_5X5']:
        return False
    if region not in ['BR', 'EUNE', 'EUW', 'KR', 'LAN', 'NA', 'OCE', 'RU', 'TR']:
        return False
    return True


def get_match_list_by_type(patch='5.14', queue="RANKED_SOLO", region='NA'):
    """
    The list of matches is organized by patch type, queue type, and region. The final file is a {region}.json file,
    which is an array of 10,000 integers. This function finds that file, parses it, and returns that array.
    :param patch: The patch of the matches we want (either '5.11' or '5.14'
    :param queue: The queue type of the matches we want (either 'RANKED_SOLO' or 'NORMAL_5X5'
    :param region: The region of the matches we want(choices are BR, EUNE, EUW, KR, LAN, NA, OCE, RU, and TR
    :return: An array of 10,000 integers containing match IDs dependant upon the given parameters.
    """

    if not verify(patch, queue, region):
        return False

    base_dir = 'E:\Workspace\AP_ITEM_DATASET'
    file_loc = base_dir + '/{p}/{q}/{r}.json'.format(p=patch, q=queue, r=region)
    with open(file_loc) as f:
        data = json.load(f)
    return data


def write_match_by_type(match_id, patch='5.14', queue="RANKED_SOLO", region='NA'):
    """
    Writes a specific match to a json file.
    :param match_id: The ID used to identify the match. Used to access the match from the Riot API.
    :param patch: What patch the match was played on.
    :param queue: What queue type (ranked or solo) the match was played on.
    :param region: What region (NA, KR, BR, etc.) the match was played in.
    :return: True if the match was successfully written, False if not.
    """
    if not verify(patch, queue, region):
        return False

    base_dir = 'E:\Workspace\MATCH_DATA'
    file_loc = base_dir + '/{p}/{q}/{r}/'.format(p=patch, q=queue, r=region)
    if not os.path.exists(file_loc):
        os.makedirs(file_loc)

    path = "{floc}{mid}.json".format(floc=file_loc, mid=match_id)
    if not os.path.isfile(path):
        m = get_match(match_id, region)
        if not isinstance(m, int):
            with open(path, 'w') as f:
                json.dump(m, f)
                print("Wrote match {mid}".format(mid=match_id))
        else:
            print("Error writing match {mid}, try again later".format(mid=match_id))
    else:
        print("Match {mid} already exists".format(mid=match_id))

    return True


def load_match(match_id, patch='5.14', queue="RANKED_SOLO", region='NA'):
    """
    Loads the match from the json file.
    :param match_id: The ID used to identify the match. Used to access the match from the Riot API.
    :param patch: What patch the match was played on.
    :param queue: What queue type (ranked or solo) the match was played on.
    :param region: What region (NA, KR, BR, etc.) the match was played in.
    :return: True if the match was successfully loaded, False if not.
    """
    if not verify(patch, queue, region):
        return False

    base_dir = 'E:\Workspace\MATCH_DATA'
    file_loc = base_dir + '/{p}/{q}/{r}/'.format(p=patch, q=queue, r=region)
    path = "{floc}{mid}.json".format(floc=file_loc, mid=match_id)

    if not os.path.isfile(path):
        write_match_by_type(match_id, patch, queue, region)
        load_match(match_id, patch, queue, region)
    else:
        with open(path, 'w') as f:
            return json.load(f)


def open_match(m):
    """
    Open a match file.
    :param m: A string that references the absolute location of that match in JSON.
    :return: A JSON file representing that match.
    """
    with open(m, 'r') as f:
        return json.load(f)


def get_sample_matches(patch='5.14', queue="RANKED_SOLO", region='NA', count=100):

    if not verify(patch, queue, region):
        return False

    base_dir = 'E:\Workspace\MATCH_DATA'
    file_loc = base_dir + '/{p}/{q}/{r}/'.format(p=patch, q=queue, r=region)

    files = glob.glob(file_loc + "/*.json")
    file_sample = random.sample(files, count)
    return file_sample


def get_all_matches(patch='5.14', queue="RANKED_SOLO", region='NA'):

    if not verify(patch, queue, region):
        return False

    base_dir = 'E:\Workspace\MATCH_DATA'
    file_loc = base_dir + '/{p}/{q}/{r}/'.format(p=patch, q=queue, r=region)

    files = glob.glob(file_loc + "/*.json")
    sample = [x for x in files]
    print(len(sample))
    return sample


def main():
    patches = ['5.11', '5.14']
    queues = ['RANKED_SOLO', 'NORMAL_5X5']

    # regions = ['BR', 'EUNE', 'EUW', 'KR', 'LAN', 'NA', 'OCE', 'RU', 'TR'] # master list don't change
    regions = ['OCE', 'RU', 'TR']  # skip certain regions with this one

    for patch in patches:
        for queue in queues:
            for region in regions:
                r = get_match_list_by_type(patch, queue, region)
                for item in r:
                    write_match_by_type(item, '5.14', queue, region)

if __name__ == '__main__':
    main()