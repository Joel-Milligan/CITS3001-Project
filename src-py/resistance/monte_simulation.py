from agent import Agent
from random_agent import RandomAgent
import random
from typing import List
from monte_node import Phase


class SimulationGame:
    '''
    A class for maintaining the state of a game of The Resistance.
    A agent oriented architecture is maintained where the 
    game has a list of Agents and methods are called on those agents 
    to share information and get game actions
    '''

    def __init__(self, num_players: int, agent_id: int, spy_list: List[int], round: int, failed_missions: int, phase: Phase):
        '''
        Simulates a game of The Resistance from a specified state.
        '''
        self.num_players = num_players
        self.agents: List[Agent] = []

        # Create agent array
        for i in range(num_players):
            self.agents.append(RandomAgent(f'r{i}'))

        # Allocate spies
        self.spies = list(spy_list)

        # Start game for each agent
        for agent_id in range(self.num_players):
            spy_list = self.spies.copy() if agent_id in self.spies else []
            self.agents[agent_id].new_game(
                self.num_players, agent_id, spy_list)

        # Initialise rounds
        self.agent_id = agent_id
        self.missions_lost = failed_missions
        self.rounds = []
        self.round = round
        self.phase = phase

    def simulate(self) -> bool:
        """
        Returns true if the resistance win, false if the spies win.
        """
        leader = self.agent_id

        for i in range(5 - self.round):
            new_round = SimulationRound(leader, self.agents, self.spies, i)
            self.rounds.append(new_round)
            # TODO: Why does i not work in place of -1? Seems to be running like 9 rounds
            if not self.rounds[-1].play():
                self.missions_lost += 1
            for a in self.agents:
                a.round_outcome(i + 1, self.missions_lost)
            leader = (leader + len(self.rounds[i].missions)) % len(self.agents)

        return self.missions_lost < 3


class SimulationRound():
    '''
    a representation of a round in the game.
    '''

    def __init__(self, leader_id, agents, spies, rnd):
        '''
        leader_id is the current leader (next to propose a mission)
        agents is the list of agents in the game,
        spies is the list of indexes of spies in the game
        rnd is what round the game is up to 
        '''
        self.leader_id = leader_id
        self.agents = agents
        self.spies = spies
        self.rnd = rnd
        self.missions = []

    def play(self):
        '''
        runs team assignment until a team is approved
        or five missions are proposed, 
        and returns True is the final mission was successful
        '''
        mission_size = Agent.mission_sizes[len(self.agents)][self.rnd]
        fails_required = Agent.fails_required[len(self.agents)][self.rnd]
        while len(self.missions) < 5:
            team = self.agents[self.leader_id].propose_mission(
                mission_size, fails_required)
            mission = SimulationMission(self.leader_id, team,
                                        self.agents, self.spies, self.rnd)
            self.missions.append(mission)
            self.leader_id = (self.leader_id + 1) % len(self.agents)
            if mission.is_approved():
                return mission.is_successful()
        return mission.is_successful()

    def is_successful(self):
        '''
        returns true is the mission was successful
        '''
        return len(self.missions) > 0 and self.missions[-1].is_successful()


class SimulationMission():
    '''
    a representation of a proposed mission
    '''

    def __init__(self, leader_id, team, agents, spies, rnd):
        '''
        leader_id is the id of the agent who proposed the mission
        team is the list of agent indexes on the mission
        agents is the list of agents in the game,
        spies is the list of indexes of spies in the game
        rnd is the round number of the game
        '''
        self.leader_id = leader_id
        self.team = team
        self.agents = agents
        self.spies = spies
        self.rnd = rnd
        self.run()

    def run(self):
        '''
        Runs the mission, by asking agents to vote, 
        and if the vote is in favour,
        asking spies if they wish to fail the mission
        '''
        self.votes_for = [i for i in range(
            len(self.agents)) if self.agents[i].vote(self.team, self.leader_id)]
        for a in self.agents:
            a.vote_outcome(self.team, self.leader_id, self.votes_for)
        if 2*len(self.votes_for) > len(self.agents):
            self.fails = [i for i in self.team if i in self.spies and self.agents[i].betray(
                self.team, self.leader_id)]
            success = len(self.fails) < Agent.fails_required[len(
                self.agents)][self.rnd]
            for a in self.agents:
                a.mission_outcome(self.team, self.leader_id,
                                  len(self.fails), success)

    def is_approved(self):
        '''
        Returns True if the mission is approved, 
        False if the mission is not approved,
        and 
        Raises an exception if the mission has not yet had the votes recorded
        '''
        return 2*len(self.votes_for) > len(self.agents)

    def is_successful(self):
        '''
        Returns True is no agents failed the mission 
        (or only one agent failed round 4 in a game of 7 or more players)
        raises an exception if the mission is not approved or fails not recorded.
        '''
        return self.is_approved() and len(self.fails) < Agent.fails_required[len(self.agents)][self.rnd]
