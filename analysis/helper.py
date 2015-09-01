__author__ = 'Matt'
import operator
import json
def array_to_str(arr):
    return " ".join(str(x) for x in arr)


def str_to_array(str):
    return map(int, str.split(' '))

def str_to_array_float(str):
    return map(float, str.split(' '))

def win_percent(win, loss):
    return (round((float(win)/(float(win) + float(loss)))*100.0, 2))


def calculate_piechart_percentages(json_dir, patch):
    """
    Calculates the top items in a distribution in order to make a good pie chart for CanvasJS.
    :param json_file: A JSON file to analyze
    :return: An associative array used for the dataPoints section of CanvasJS.
    """

    # create list of tuples for this patch
    playrates = []
    with open(json_dir, 'r') as f:
        json_dict_array = json.load(f)
        for dict in json_dict_array:
            playrates.append([dict[u'championName'], dict[u"gamesPlayed-({p})".format(p=patch)]])

    playrates = sorted(playrates, key=operator.itemgetter(1), reverse=True)
    total_games = float(sum([champ[1] for champ in playrates]))

    playrate_percents = []
    for champ in playrates:
        playrate_percents.append( [ champ[0], round((float(champ[1]) / total_games)*100.0, 2) ])


    # Print out dataPoints format for quick use.
    # I know this isn't the right way to do it, but it's the easy way :(
    sumVal = 0.0
    for item in playrate_percents[0:25][::-1]:
        print("{label: \"" + item[0] + "\", y: " + str(item[1]) + "}, ")
        sumVal += float(item[1])

    diff = 100.0 - sumVal
    print("{label: \"Other\", y: " + str(sumVal) + "}")

def main():
    calculate_piechart_percentages('../static/json/pickrate.json', '5.11')
    calculate_piechart_percentages('../static/json/pickrate.json', '5.14')

if __name__ == "__main__":
    main()