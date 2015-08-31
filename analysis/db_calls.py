__author__ = 'Matt'
from sqlalchemy import Column, Integer, String, Boolean, REAL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import json

from profile_builder import generate_profiles
from api_calls import generate_champion_name_dictionary
from helper import array_to_str, str_to_array

average = 1097  # average number of games played
champion_name_dict = generate_champion_name_dictionary()

# list of DBs
engine = create_engine('sqlite:///profiles.db')
Base = declarative_base(bind=engine)

# DB Classes


class dbProfile(Base):
    __tablename__ = 'Profiles'
    id = Column(Integer, primary_key = True) # Going to use <champ_id><match_id> as unique ID
    champ_id = Column(Integer)
    match_id = Column(Integer)
    patch = Column(String(6))
    region = Column(String(2))
    queue = Column(String(15))

    result = Column(Boolean)
    kills = Column(Integer)
    deaths = Column(Integer)
    assists = Column(Integer)
    final_build = Column(String(40))
    build_order = Column(String(40))
    #  self.shopping_trips = None #don't do shopping trips for now
    damage_done = Column(Integer)
    damage_taken = Column(Integer)
    has_rylais = Column(Boolean)
    rylais_order = Column(Integer)

    def __init__(self, profile):
        self.id = str(profile.champ_id) + str(profile.match_id)
        self.champ_id = profile.champ_id
        self.match_id = profile.match_id
        self.patch = profile.patch
        self.region = profile.region
        self.queue = profile.queue

        self.result = profile.result
        self.kills = profile.kills
        self.deaths = profile.deaths
        self.assists = profile.assists
        self.final_build = array_to_str(profile.final_build)
        self.build_order = array_to_str(profile.build_order)
        #self.shopping_trips = None
        self.damage_done = profile.damage_done
        self.damage_taken = profile.damage_taken
        self.has_rylais = profile.has_rylais
        self.rylais_order = profile.rylais_order


class WinRate(Base):
    __tablename__ = 'winrates'
    champ_id = Column(Integer, primary_key=True)
    wins_511 = Column(Integer)
    losses_511 = Column(Integer)
    wins_514 = Column(Integer)
    losses_514 = Column(Integer)


    def __init__(self, champ_id, wins_511, losses_511, wins_514, losses_514):
        self.champ_id = int(champ_id)
        self.wins_511 = wins_511
        self.losses_511 = losses_511
        self.wins_514 = wins_514
        self.losses_514 = losses_514


class RylaisOrder(Base):
    __tablename__ = 'rylais_order'
    champ_id = Column(Integer, primary_key=True)
    percent_build = Column(REAL(5))
    built_winrate = Column(REAL(5))
    not_built_winrate = Column(REAL(5))
    wins = Column(String(40))
    losses = Column(String(40))
    winrates = Column(String(40))

    def __init__(self, champ_id, percent_build, built_winrate, not_built_winrate, wins, losses, winrates):
        self.champ_id = champ_id
        self.percent_build = percent_build
        self.built_winrate = built_winrate
        self.not_built_winrate = not_built_winrate
        self.wins = wins
        self.losses = losses
        self.winrates = winrates
# Table population methods


def populate_rylais_order_table(session):
    rylais_dict = generate_rylais_order_dictionary(session)
    keys = rylais_dict.keys()

    for champ in keys:
        champ_id = champ
        wins = []
        losses = []
        for i in range(7):
            wins.append(rylais_dict[champ][i][0])
            losses.append(rylais_dict[champ][i][1])
        winrate = []
        for i in range(len(wins)):
            if wins[i] + losses[i] <= 5: # too small a sample size
                wins[i] = 0
                losses[i] = 0
                winrate.append(0)
            else:
                if losses[i] == 0:
                    winrate.append(100.0)
                else:
                    winrate.append(round((float(wins[i])/(float(wins[i]) + float(losses[i])))*100.0, 2))
        games_with = sum(wins[1:]) + sum(losses[1:])
        games_without = wins[0] + losses[0]
        if (games_with + games_without) <= 25: # too small a sample size, continue
            continue
        percent_build = round((float(games_with) / float(games_with + games_without))*100.0, 2)

        if games_with <= 5:
            built_winrate = 0.0
        else:
            built_winrate = round((float(sum(wins[1:])) / float(sum(wins[1:]) + sum(losses[1:])))*100.0, 2)

        if games_without <= 5:
            not_built_winrate = 0.0
        else:
            not_built_winrate = round((float(wins[0]) / float(wins[0] + losses[0]))*100.0, 2)
        rylai_order = RylaisOrder(champ_id, percent_build, built_winrate, not_built_winrate, array_to_str(wins), array_to_str(losses), array_to_str(winrate))
        session.merge(rylai_order)

    session.commit()

def populate_win_rate_table(session):
    """ This function pulls data from the Profiles table and creates the winrates table.

    :param session: The SQLAlchemy session.
    :return: None.
    """
    winrate_dict_511 = generate_win_rate_dictionary(session, '5.11')
    winrate_dict_514 = generate_win_rate_dictionary(session, '5.14')

    keys = list(set(winrate_dict_511.keys() + winrate_dict_514.keys()))
    for champ in keys:
        print(champ)
        # champion ID, champion win count, champion loss count (for both patches)
        champ_id = champ
        wins_511 = winrate_dict_511[champ][0] if champ in winrate_dict_511.keys() else 0
        losses_511 = winrate_dict_511[champ][1] if champ in winrate_dict_511.keys() else 0
        wins_514 = winrate_dict_514[champ][0] if champ in winrate_dict_514.keys() else 0
        losses_514 = winrate_dict_514[champ][1] if champ in winrate_dict_514.keys() else 0

        item_db = WinRate(champ_id, wins_511, losses_511, wins_514, losses_514)
        session.merge(item_db)

    session.commit()


def populate_profiles_table(session):
    """
    Generates the Profiles table.
    :param session: The SQLAlchemy session.
    :return: None.
    """

    print("populate_profiles_table")

    test_profiles = generate_profiles(1)
    for p in test_profiles:
        db_p = dbProfile(p)
        session.merge(db_p)

    session.commit()


# Helper methods


def generate_win_rate_dictionary(session, patch_no):
    """ Generates a dictionary file from the Profiles table, in order to generate
    the winrates table.
    :param session: The SQLAlchemy session.
    :param patch_no: The patch to be working with(either 5.11 or 5.14).
    :return: A dictionary object.
    """
    winrates = {}
    for profile in session.query(dbProfile).filter_by(patch=patch_no):
        if profile.patch == '5.11':
            if profile.champ_id not in winrates:
                winrates[profile.champ_id] = [0]*2
            if profile.result:
                winrates[profile.champ_id][0] += 1
            else:
                winrates[profile.champ_id][1] += 1
        else:
            if profile.champ_id not in winrates:
                winrates[profile.champ_id] = [0]*2
            if profile.result:
                winrates[profile.champ_id][0] += 1
            else:
                winrates[profile.champ_id][1] += 1
    return winrates


def generate_rylais_order_dictionary(session):
    rylais_dict = {}
    # array structure: [[wins_without, losses_without],
    # [wins_built_first, losses_built_first], ... [wins_built_last, losses_built_last]]
    for profile in session.query(dbProfile).filter_by(patch='5.14'):
        if profile.champ_id not in rylais_dict:
            rylais_dict[profile.champ_id] = [[0,0], [0,0], [0,0], [0,0], [0,0], [0,0], [0,0]]
        if profile.has_rylais:
            build_order = str_to_array(profile.build_order)
            rylais_index = build_order.index(3116) + 1
            if profile.result:
                rylais_dict[profile.champ_id][rylais_index][0] += 1
            else:
                rylais_dict[profile.champ_id][rylais_index][1] += 1
        else:
            if profile.result:
                rylais_dict[profile.champ_id][0][0] += 1
            else:
                rylais_dict[profile.champ_id][0][1] += 1
    return rylais_dict

# json methods

def generate_winrate_json(session, min_games=500):
    winrate_data = session.query(WinRate).filter((WinRate.wins_511 + WinRate.losses_511 + WinRate.wins_514 + WinRate.losses_514) >= min_games)
    print(winrate_data.count())
    json_array = []
    with open('../static/json/winrate.json', 'wb') as f:
        for row in winrate_data:
            winrate_511 = round((float(row.wins_511)/float(row.wins_511 + row.losses_511))*100.0, 2)
            winrate_514 = round((float(row.wins_514)/float(row.wins_514 + row.losses_514))*100.0, 2)
            percent_change = round( ((winrate_514 - winrate_511) / (winrate_511))*100.0, 1)
            json_array.append({"championName": champion_name_dict[row.champ_id],
                               "wins-(5.11)": row.wins_511,
                               "losses-(5.11)": row.losses_511,
                               "winrate-(5.11)": winrate_511,
                               "wins-(5.14)": row.wins_514,
                               "losses-(5.14)": row.losses_514,
                               "winrate-(5.14)": winrate_514,
                               "percentChange": percent_change
                               })
        json.dump(json_array, f)


def main():
    # Set up SQLAlchemy.
    Base.metadata.create_all()
    Session = sessionmaker(bind=engine)
    s = Session()
    print("session created")

    # populate_profiles_table(s)
    # populate_win_rate_table(s)
    generate_winrate_json(s)
    #populate_rylais_order_table(s)


if __name__ == "__main__":
    main()
