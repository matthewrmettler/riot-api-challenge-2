__author__ = 'Matt'
from api_calls import getMatch
import os
import json
import glob
import random

def root_dir():  # pragma: no cover
    return os.path.abspath(os.path.dirname(__file__))

def verify(patch, queue, region):
    if patch not in ['5.11', '5.14']:
        return False
    if queue not in ['RANKED_SOLO', 'NORMAL_5X5']:
        return False
    if region not in ['BR', 'EUNE', 'EUW', 'KR', 'LAN', 'NA', 'OCE', 'RU', 'TR']:
        return False

    return True

def getMatchListByType(patch='5.14', queue="RANKED_SOLO", region='NA'):
    '''
    The list of matches is organized by patch type, queue type, and region. The final file is a {region}.json file,
    which is an array with 10000 integers inside of it. This function finds that file, parses it, and returns that array.
    :param patch: The patch of the matches we want (either '5.11' or '5.14'
    :param queue: The queue type of the matches we want (either 'RANKED_SOLO' or 'NORMAL_5X5'
    :param region: The region of the matches we want(choices are BR, EUNE, EUW, KR, LAN, NA, OCE, RU, and TR
    :return: An array of 10,000 integers containing match IDs dependant upon the given parameters.
    '''
    #should be a valid call
    if not verify(patch, queue, region): return False

    dir = root_dir()
    file_loc = dir + '/AP_ITEM_DATASET/{p}/{q}/{r}.json'.format(p=patch, q=queue, r=region)
    with open(file_loc) as f:
        data = json.load(f)
    return data

def writeMatchByType(id, patch='5.14', queue="RANKED_SOLO", region='NA'):
    #should be a valid call
    if not verify(patch, queue, region): return False

    dir = 'E:\Workspace\MATCH_DATA'
    file_loc = dir + '/{p}/{q}/{r}/'.format(p=patch, q=queue, r=region)
    if not os.path.exists(file_loc):
        os.makedirs(file_loc)

    path = "{floc}{mid}.json".format(floc=file_loc, mid=id)
    if not os.path.isfile(path):
        with open(path, 'w') as f:
            m = getMatch(id, region)
            if not isinstance(m, int):
                json.dump(m, f)
                print("Wrote match {mid}".format(mid=id))
            else:
                print("Error writing match {mid}, try again later".format(mid=id))
    else:
        print("Match {mid} already exists".format(mid=id))

    return True

def loadMatch(id, patch='5.14', queue="RANKED_SOLO", region='NA'):
    #should be a valid call
    if not verify(patch, queue, region): return False

    dir = 'E:\Workspace\MATCH_DATA'
    file_loc = dir + '/{p}/{q}/{r}/'.format(p=patch, q=queue, r=region)
    path = "{floc}{mid}.json".format(floc=file_loc, mid=id)

    if not os.path.isfile(path):
        writeMatchByType(id, patch, queue, region)
    else:
        with open(path, 'w') as f:
            return json.load(f)

def getSampleMatches(patch='5.14', queue="RANKED_SOLO", region='NA', count=100):
    #should be a valid call
    if not verify(patch, queue, region): return False

    dir = 'E:\Workspace\MATCH_DATA'
    file_loc = dir + '/{p}/{q}/{r}/'.format(p=patch, q=queue, r=region)

    files = glob.glob(file_loc + "/*.json")
    file_sample = random.sample(files, count)
    return file_sample

def getAllMatches(patch='5.14', queue="RANKED_SOLO", region='NA'):
    #should be a valid call
    if not verify(patch, queue, region): return False

    dir = 'E:\Workspace\MATCH_DATA'
    file_loc = dir + '/{p}/{q}/{r}/'.format(p=patch, q=queue, r=region)

    files = glob.glob(file_loc + "/*.json")
    sample = [x for x in files]
    print(len(sample))
    return sample

def main():
    patches = ['5.11', '5.14'] 
    queues = ['RANKED_SOLO', 'NORMAL_5X5']

    #regions = ['BR', 'EUNE', 'EUW', 'KR', 'LAN', 'NA', 'OCE', 'RU', 'TR'] #master list don't change
    regions = ['NA', 'OCE', 'RU', 'TR']  #skip certain regions with this one

    for patch in patches:
        for queue in queues:
            for region  in regions:
                r = getMatchListByType(patch, queue, region)
                for item in r:
                    writeMatchByType(item, '5.14', queue, region)

if __name__ == '__main__':
    main()