__author__ = 'Matt'
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from profile_builder import Profile, generate_profiles

average = 1097 #average number of games played

# list of DBs
engine = create_engine('sqlite:///profiles.db')
Base = declarative_base(bind=engine)

def array_to_str(arr):
    return " ".join(str(x) for x in arr)


def str_to_array(str):
    return str.split(' ')


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
    id = Column(Integer, primary_key=True)
    champ_id = Column(Integer)
    wins = Column(Integer)
    losses = Column(Integer)
    patch = Column(String(6))

    def __init__(self, champ_id, wins, losses, patch):
        self.id = int(patch[2:] + "000" + str(champ_id))
        self.champ_id = champ_id
        self.wins = wins
        self.losses = losses
        self.patch = patch


def populate_win_rate_table(session):
    winrate_dict_511 = generate_win_rate_dictionary(session, '5.11')
    winrate_dict_514 = generate_win_rate_dictionary(session, '5.14')

    for item in winrate_dict_511.keys():
        array = [item, winrate_dict_511[item][0], winrate_dict_511[item][1]]
        item_db = WinRate(array[0], array[1], array[2], '5.11')
        session.merge(item_db)

    for item in winrate_dict_514:
        array = [item, winrate_dict_514[item][0], winrate_dict_514[item][1]]
        item_db = WinRate(array[0], array[1], array[2], '5.14')
        session.merge(item_db)

    session.commit()


def generate_win_rate_dictionary(session, patch_no):
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


def populate_main_db(session):
    print("populate_main_db")

    test_profiles = generate_profiles(1)
    for p in test_profiles:
        db_p = dbProfile(p)
        session.merge(db_p)

    session.commit()


def main():
    Base.metadata.create_all()
    Session = sessionmaker(bind=engine)
    s = Session()
    print("session created")

    #populate_main_db(s)
    #populate_win_rate_table(s)
    calculate_std(s)

if __name__ == "__main__":
    main()
