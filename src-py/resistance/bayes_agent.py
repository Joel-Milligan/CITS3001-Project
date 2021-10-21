from typing import List, Dict
from agent import Agent
import random
from heapq import nsmallest


class BayesAgent(Agent):
    '''
    Agent that uses Bayes' Theorem.
    '''

    def __init__(self, name: str = 'Mr. Bayesian') -> None:
        '''
        Initialises the agent.
        '''
        self.name = name

    def new_game(self, number_of_players: int, player_number: int, spy_list: List[int]) -> None:
        '''
        Initialises the game, informing the agent of the 
        number_of_players, the player_number,
        and a list of agent indexes which are the spies, 
        if the agent is a spy, or empty otherwise
        '''
        self.number_of_players = number_of_players
        self.player_number = player_number
        self.spy_list = spy_list

        if self.player_number not in self.spy_list:
            self.suspicion = dict()

            # Minus one because we know we aren't a spy.
            # number_of_spies = Agent.spy_count[number_of_players]
            # spy_chance = number_of_spies / (number_of_players - 1)
            spy_chance = 1

            for p in range(number_of_players):
                self.suspicion.update({p: spy_chance})

            # Set our own suspicion to 0 due to secret knowledge
            self.suspicion.update({player_number: 0})
        else:
            self.suspicion = dict()

            for p in range(number_of_players):
                if p in spy_list:
                    self.suspicion.update({p: 100})
                else:
                    self.suspicion.update({p: 0})

    def is_spy(self) -> bool:
        '''
        returns True iff the agent is a spy
        '''
        return self.player_number in self.spy_list

    def propose_mission(self, team_size: int, betrayals_required: int = 1) -> List[int]:
        '''
        expects a team_size list of distinct agents with id between 
        0 (inclusive) and number_of_players (exclusive) to be returned. 
        betrayals_required are the number of betrayals required for the mission to fail.
        '''
        if self.is_spy():
            team: List[int] = []
            while len(team) < team_size:
                agent = random.randrange(team_size)
                if agent not in team:
                    team.append(agent)
            return team

        team = nsmallest(team_size, self.suspicion, key=self.suspicion.get)
        return team

    def vote(self, mission: List[int], proposer: int) -> bool:
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The function should return True if the vote is for the mission, and False if the vote is against the mission.
        '''
        total_suspicion = 0

        for player in mission:
            total_suspicion += self.suspicion[player]

        total_suspicion += self.suspicion[player] / 2

        if not self.is_spy():
            average_sus = total_suspicion / len(mission)
            total_sus = sum(self.suspicion.values())
            return average_sus < total_sus * 0.5
        else:
            return True

    def vote_outcome(self, mission: List[int], proposer: int, votes: dict[int, bool]) -> None:
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        votes is a dictionary mapping player indexes to Booleans (True if they voted for the mission, False otherwise).
        No return value is required or expected.
        '''
        # nothing to do here
        pass

    def betray(self, mission: List[int], proposer: int) -> bool:
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players, and include this agent.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The method should return True if this agent chooses to betray the mission, and False otherwise. 
        By default, spies will betray 30% of the time. 
        '''
        if self.is_spy():
            return random.random() < 1

        return False

    def mission_outcome(self, mission: List[int], proposer: int, betrayals: int, mission_success: bool) -> None:
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        betrayals is the number of people on the mission who betrayed the mission, 
        and mission_success is True if there were not enough betrayals to cause the mission to fail, False otherwise.
        It is not expected or required for this function to return anything.
        '''
        if not mission_success:
            for player in mission:
                self.suspicion[player] += 1

            if proposer not in mission:
                self.suspicion[proposer] += 0.5
        else:
            for player in mission:
                self.suspicion[player] -= 1

            if proposer not in mission:
                self.suspicion[proposer] -= 0.5

    def round_outcome(self, rounds_complete: int, missions_failed: int) -> None:
        '''
        basic informative function, where the parameters indicate:
        rounds_complete, the number of rounds (0-5) that have been completed
        missions_failed, the number of missions (0-3) that have failed.
        '''
        # nothing to do here
        pass

    def game_outcome(self, spies_win: bool, spies: List[int]) -> None:
        '''
        basic informative function, where the parameters indicate:
        spies_win, True iff the spies caused 3+ missions to fail
        spies, a list of the player indexes for the spies.
        '''
        # nothing to do here
        pass
