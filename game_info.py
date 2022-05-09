from enum import IntEnum, Enum
import pandas as pd

from game_classes import Game, Map, Hero


class GameStates(IntEnum):
    DOTA_GAMERULES_STATE_INIT = 0
    DOTA_GAMERULES_STATE_WAIT_FOR_PLAYERS_TO_LOAD = 1
    DOTA_GAMERULES_STATE_HERO_SELECTION = 2
    DOTA_GAMERULES_STATE_STRATEGY_TIME = 3
    DOTA_GAMERULES_STATE_PRE_GAME = 4
    DOTA_GAMERULES_STATE_GAME_IN_PROGRESS = 5
    DOTA_GAMERULES_STATE_POST_GAME = 6
    DOTA_GAMERULES_STATE_DISCONNECT = 7
    DOTA_GAMERULES_STATE_TEAM_SHOWCASE = 8
    DOTA_GAMERULES_STATE_LAST = 9


class GameAttributes(IntEnum):
    strength = 0
    agility = 1
    intelligence = 2


class GameJSONParser:
    def parse_game_json(self, game_json, game):
        if game_json:
            for item in game_json:  # provider, map, player, hero, abilities, items
                for i in game_json[item]:  # params of item
                    try:
                        setattr(getattr(game, item), i, game_json[item][i])
                    except:
                        pass
        else:
            game.__init__()


GameHeroes = [Hero(hero['id'], hero['name'], hero['name_loc'], hero['primary_attr'], hero['complexity'])
              for i, hero in pd.read_csv('heroes/heroes_list.csv', sep='\t').iterrows()]


def find_hero_by_name(name):
    return list(filter(lambda x: x.name == name, GameHeroes))[0]
