__author__ = 'Matt'
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from profile_builder import Profile, generate_profiles

engine = create_engine('sqlite:///temp/test.db', echo=True)
Base = declarative_base(bind=engine)

def array_to_str(arr):
    return " ".join(x for x in arr)


def str_to_array(str):
    return str.split(' ')


class dbProfile(Base):
    __tablename__ = 'Profiles'
    id = Column(Integer, primary_key = True)
    champ_id = Column(Integer)
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
        self.champ_id = profile.champ_id
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


def main():
    Base.metadata.create_all()
    Session = sessionmaker(bind=engine)
    s = Session()

    test_profile = generate_profiles(1)[0]
    test_dbProfile = dbProfile(test_profile)
    s.add_all(test_dbProfile)
    s.commit()

    for p in s.query(dbProfile):
        print type(p), p.champ_id, p.result, p.has_rylais

if __name__ == "__main__":
    main()
