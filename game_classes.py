class Game:
    """Class to store game information"""
    def __init__(self):
        self.map = Map()

    def isEmpty(self):
        return all(attr is None for attr in dir(self))


class Map:
    """Class to store map information"""
    def __init__(self):
        self.name = None
        self.match_id = None
        self.game_time = None
        self.clock_time = None
        self.daytime = None
        # self.nightstalker_night = None
        self.game_state = None
        self.paused = None
        # self.win_team = None
        # self.customgamename = None
        # self.ward_purchase_cooldown = None


class Hero:
    def __init__(self, hero_id, name, name_loc, primary_attr, complexity):
        self.hero_id = hero_id
        self.name = name
        self.name_loc = name_loc
        self.primary_attr = primary_attr
        self.complexity = complexity
