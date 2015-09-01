"""
api_calls.py
By Matthew Mettler (2015)

This python file contains all the necessary functions needed to communicate with the databases needed for analysis, and
to product JSON files.
"""

__author__ = 'Matt'
from sqlalchemy import Column, Integer, String, Boolean, REAL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import json

from profile_builder import generate_profiles
from api_calls import generate_champion_name_dictionary
from helper import array_to_str, str_to_array, str_to_array_float, win_percent

average = 1097  # average number of games played
champion_name_dict = generate_champion_name_dictionary()

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
    total_games_built = Column(Integer)
    wins = Column(String(40))
    losses = Column(String(40))
    winrates = Column(String(40))

    def __init__(self, champ_id, percent_build, built_winrate, not_built_winrate, total_games_built, wins, losses,
                 winrates):
        self.champ_id = champ_id
        self.percent_build = percent_build
        self.built_winrate = built_winrate
        self.not_built_winrate = not_built_winrate
        self.total_games_built = total_games_built
        self.wins = wins
        self.losses = losses
        self.winrates = winrates


# Table population methods


class RylaisDamage(Base):
    __tablename__ = 'rylais_damage'
    champ_id = Column(Integer, primary_key=True)
    kills_rylais = Column(REAL(5))
    kills_without = Column(REAL(5))
    deaths_rylais = Column(REAL(5))
    deaths_without = Column(REAL(5))
    assists_rylais = Column(REAL(5))
    assists_without = Column(REAL(5))
    kda_rylais = Column(REAL(5))
    kda_without = Column(REAL(5))
    damage_done_rylais = Column(REAL(5))
    damage_done_without = Column(REAL(5))
    damage_taken_rylais = Column(REAL(5))
    damage_taken_without = Column(REAL(5))
    damage_ratio_rylais = Column(REAL(5))
    damage_ratio_without = Column(REAL(5))

    def __init__(self, champ_id, k_r, k_w, d_r, d_w, a_r, a_w, kda_r, kda_w, dd_r, dd_w, dt_r, dt_w, dr_r, dr_w):
        self.champ_id = champ_id
        self.kills_rylais = k_r
        self.kills_without = k_w
        self.deaths_rylais = d_r
        self.deaths_without = d_w
        self.assists_rylais = a_r
        self.assists_without = a_w
        self.kda_rylais = kda_r
        self.kda_without = kda_w
        self.damage_done_rylais = dd_r
        self.damage_done_without = dd_w
        self.damage_taken_rylais = dt_r
        self.damage_taken_without = dt_w
        self.damage_ratio_rylais = dr_r
        self.damage_ratio_without = dr_w


def populate_rylais_damage_table(session):
    """
    Populates the Rylai's Damage table (the table needed for the third table on the web app.)
    :param session: The current DB session.
    :return: None.
    """
    rylais_dict = generate_rylais_damage_dictionary(session)
    keys = rylais_dict.keys()

    for champ in keys:
        games_with = float(rylais_dict[champ][0][0])
        if games_with <= 125:
            continue  # don't include champs with little to no rylai's
        games_without = float(rylais_dict[champ][1][0])
        kills_rylais = round(float(rylais_dict[champ][0][1]) / games_with, 2)
        kills_without = round(float(rylais_dict[champ][1][1]) / games_without, 2)
        deaths_rylais = round(float(rylais_dict[champ][0][2]) / games_with, 2)
        deaths_without = round(float(rylais_dict[champ][1][2]) / games_without, 2)
        assists_rylais = round(float(rylais_dict[champ][0][3]) / games_with, 2)
        assists_without = round(float(rylais_dict[champ][1][3]) / games_without, 2)
        kda_rylais = round((kills_rylais + assists_rylais) / deaths_rylais, 2)
        kda_without = round((kills_without + assists_without) / deaths_without, 2)
        damage_done_rylais = round(float(rylais_dict[champ][0][4]) / games_with, 2)
        damage_done_without = round(float(rylais_dict[champ][1][4]) / games_without, 2)
        damage_taken_rylais = round(float(rylais_dict[champ][0][5]) / games_with, 2)
        damage_taken_without = round(float(rylais_dict[champ][1][5]) / games_without, 2)
        damage_ratio_rylais = round(damage_done_rylais / damage_taken_rylais, 2)
        damage_ratio_without = round(damage_done_without / damage_taken_without, 2)

        rylai_damage = RylaisDamage(champ, kills_rylais, kills_without, deaths_rylais, deaths_without,
                                    assists_rylais, assists_without, kda_rylais, kda_without, damage_done_rylais,
                                    damage_done_without, damage_taken_rylais, damage_taken_without,
                                    damage_ratio_rylais, damage_ratio_without)
        session.merge(rylai_damage)

    session.commit()

def populate_rylais_order_table(session):
    """
    Populates the rylai's order table (needed for the second table on the web app.)
    :param session: The current DB session.
    :return: None.
    """
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
                    winrate.append(win_percent(wins[i], losses[i]))
        games_with = sum(wins[1:]) + sum(losses[1:])
        games_without = wins[0] + losses[0]
        if (games_with + games_without) <= 25: # too small a sample size, continue
            continue
        percent_build = win_percent(games_with, games_without)

        if games_with <= 5:
            built_winrate = 0.0
        else:
            built_winrate = win_percent(sum(wins[1:]), sum(losses[1:]))

        if games_without <= 5:
            not_built_winrate = 0.0
        else:
            not_built_winrate = win_percent(wins[0], losses[0])
        rylai_order = RylaisOrder(champ_id, percent_build, built_winrate, not_built_winrate, games_with, array_to_str(wins), array_to_str(losses), array_to_str(winrate))
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
        # print(champ)
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


def generate_rylais_damage_dictionary(session):
    rylais_dict = {}
    # array structure: [games_with, kills, deaths, assists, damage done, damage taken]
    for profile in session.query(dbProfile).filter_by(patch='5.14'):
        if profile.champ_id not in rylais_dict:
            rylais_dict[profile.champ_id] = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
        if profile.has_rylais:
            i = 0
        else:
            i = 1
        rylais_dict[profile.champ_id][i][0] += 1 #games_with
        rylais_dict[profile.champ_id][i][1] += profile.kills
        rylais_dict[profile.champ_id][i][2] += profile.deaths
        rylais_dict[profile.champ_id][i][3] += profile.assists
        rylais_dict[profile.champ_id][i][4] += profile.damage_done
        rylais_dict[profile.champ_id][i][5] += profile.damage_taken

    return rylais_dict


# json methods


def generate_winrate_json(session, min_games=500):
    winrate_data = session.query(WinRate).filter((WinRate.wins_511 + WinRate.losses_511 + WinRate.wins_514 + WinRate.losses_514) >= min_games)
    print(winrate_data.count())
    json_array = []
    with open('../static/json/winrate.json', 'wb') as f:
        for row in winrate_data:
            winrate_511 = win_percent(row.wins_511, row.losses_511)
            winrate_514 = win_percent(row.wins_514, row.losses_514)
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


def generate_pickrate_json(session, min_games=250):
    pickrate_data = session.query(WinRate).filter((WinRate.wins_511 + WinRate.losses_511 + WinRate.wins_514 + WinRate.losses_514) >= min_games)
    print(pickrate_data.count())
    json_array = []
    with open('../static/json/pickrate.json', 'wb') as f:
        for row in pickrate_data:
            pickrate_511 = row.wins_511 + row.losses_511
            pickrate_514 = row.wins_514 + row.losses_514
            json_array.append({"championName": champion_name_dict[row.champ_id],
                               "gamesPlayed-(5.11)": pickrate_511,
                               "gamesPlayed-(5.14)": pickrate_514
                               })
        json.dump(json_array, f)


def generate_rylais_json(session, min_purchased=125):
    rylais_data = session.query(RylaisOrder).filter(RylaisOrder.total_games_built >= min_purchased)
    print(rylais_data.count())
    json_array = []
    with open('../static/json/rylais.json', 'wb') as f:
        for row in rylais_data:
            wins = str_to_array(row.wins)[1:]
            winrates = str_to_array_float(row.winrates)[1:]

            percent_build = row.percent_build
            built_winrate = row.built_winrate
            not_build_winrate = row.not_built_winrate
            built_first_count = wins[0]
            built_second_count = wins[1]
            built_third_count = wins[2]
            built_first_percent = winrates[0]
            built_second_percent = winrates[1]
            built_third_percent = winrates[2]

            percent_change = round( ((built_winrate - not_build_winrate) / not_build_winrate)*100.0, 1)
            json_array.append({"championName": champion_name_dict[row.champ_id],
                               "percentBuilt": percent_build,
                               "builtFirstWins": built_first_count,
                               "builtSecondWins": built_second_count,
                               "builtThirdWins": built_third_count,
                               "builtFirstWinPercent": built_first_percent,
                               "builtSecondWinPercent": built_second_percent,
                               "builtThirdWinPercent": built_third_percent,
                               "builtWinrate": built_winrate,
                               "notBuiltWinrate": not_build_winrate,
                               "percentDifference": percent_change
                               })
        json.dump(json_array, f)


def generate_damage_json(session):
    rylais_data = session.query(RylaisDamage)
    print(rylais_data.count())
    json_array = []
    with open('../static/json/damage.json', 'wb') as f:
        for row in rylais_data:
            kda_change = round(((float(row.kda_rylais) - float(row.kda_without))/(row.kda_without))*100.0, 2)
            json_array.append({ "championName": champion_name_dict[row.champ_id],
                                "rylaisKills": row.kills_rylais,
                                "rylaisDeaths": row.deaths_rylais,
                                "rylaisAssists": row.assists_rylais,
                                "withoutKills": row.kills_without,
                                "withoutDeaths": row.deaths_without,
                                "withoutAssists": row.assists_without,
                                "rylaisDamageRatio": row.damage_ratio_rylais,
                                "withoutDamageRatio": row.damage_ratio_without,
                                "rylaisKda": row.kda_rylais,
                                "withoutKda": row.kda_without,
                                "kdapercentChange": kda_change,
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
    # generate_winrate_json(s)

    # populate_rylais_order_table(s)
    # generate_pickrate_json(s)
    # generate_rylais_json(s)

    #populate_rylais_damage_table(s)
    generate_damage_json(s)

if __name__ == "__main__":
    main()
