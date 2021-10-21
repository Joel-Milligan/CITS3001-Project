from typing import List, Dict, Union, Tuple
from agent import Agent
from monte_node import Node, StateNode, ActionNode, Phase
from monte_simulation import SimulationGame
from game import Game
import random
from math import sqrt, log
from itertools import combinations


class MonteAgent(Agent):
    '''
    Agent that uses Monte Carlo Tree Search.
    '''

    def __init__(self, name: str = 'Mr. Monte') -> None:
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
        self.players = [*range(number_of_players)]
        self.player_number = player_number
        self.spy_list = spy_list
        self.rounds_completed = 0
        self.missions_failed = 0

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
        state = StateNode(Phase.PROPOSE, self.is_spy(), Agent.spy_count[len(self.players)],
                          self.players, team_size=team_size)
        action: ActionNode = self.monte_carlo(state)
        return action.proposal

    def vote(self, mission: List[int], proposer: int) -> bool:
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The function should return True if the vote is for the mission, and False if the vote is against the mission.
        '''
        state = StateNode(Phase.VOTE, self.is_spy(), Agent.spy_count[len(self.players)],
                          self.players, mission=mission)
        state.generate_actions()

        action: ActionNode = self.monte_carlo(state)
        return action.vote

    def vote_outcome(self, mission: List[int], proposer: int, votes: dict[int, bool]) -> None:
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        votes is a dictionary mapping player indexes to Booleans (True if they voted for the mission, False otherwise).
        No return value is required or expected.
        '''
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
            return random.random() < 0.3

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
        pass

    def round_outcome(self, rounds_completed: int, missions_failed: int) -> None:
        '''
        basic informative function, where the parameters indicate:
        rounds_complete, the number of rounds (0-5) that have been completed
        missions_failed, the numbe of missions (0-3) that have failed.
        '''
        self.rounds_completed = rounds_completed
        self.missions_failed = missions_failed

    def game_outcome(self, spies_win: bool, spies: List[int]) -> None:
        '''
        basic informative function, where the parameters indicate:
        spies_win, True iff the spies caused 3+ missions to fail
        spies, a list of the player indexes for the spies.
        '''
        pass

    def uct_value(self, node: Node) -> float:
        if node.visits == 0:
            return float('inf')

        explore_weight = sqrt(2)

        if node.parent:
            parent_visit_ratio = log(node.parent.visits) / node.visits
        else:
            parent_visit_ratio = log(node.visits) / node.visits

        exploration = explore_weight * sqrt(parent_visit_ratio)
        exploitation = node.wins / node.visits

        return exploitation + exploration

    def monte_carlo(self, state: StateNode) -> ActionNode:
        for i in range(10):
            unvisited_children = filter(
                lambda c: c.visits == 0, state.children)
            unvisited_children = list(unvisited_children)
            if len(unvisited_children) != 0:
                action_to_take = random.choice(unvisited_children)
            else:
                max_uct = 0
                action_to_take = None

                for child in state.children:
                    uct = self.uct_value(child)
                    if uct > max_uct:
                        max_uct = uct
                        action_to_take = child

            win_ratio = self.simulate(state, action_to_take)
            self.update_value(action_to_take, win_ratio)

        return max(state.children, key=lambda child: child.wins)

    def expand(state: StateNode) -> None:
        state.visits = 1
        state.value = 0

    def simulate(self, state: StateNode, action: ActionNode) -> float:
        """
        Runs many rollouts for every possible configuration of spies.
        """
        # 0 - Initialise variables for return value.
        total_rollouts = 0
        total_wins = 0

        # 1 - Generate all possible combinations of spies.
        spy_combos = combinations(state.players, state.num_spys)

        # 2 - Run a random game for every combination of spies.
        for spys in spy_combos:
            total_rollouts += 1

            # TODO - Action never gets passed and therefore has no influence.
            if self.rollout(spys, self.rounds_completed, self.missions_failed, state.phase):
                total_wins += 1

        # 3 - Return the percentage of wins from all the rollouts.
        return total_wins / total_rollouts

    def rollout(self, spys: List[int], rnd: int, failed_missions: int, phase: Phase) -> bool:
        game = SimulationGame(len(self.players), self.player_number, spys,
                              rnd, failed_missions, phase)

        won_as_resistance = game.simulate() and not self.is_spy()
        won_as_spies = not game.simulate() and self.is_spy()

        return won_as_resistance or won_as_spies

    def update_value(self, node: Node, win_ratio) -> None:
        node.wins += win_ratio
        node.visits += 1

        if node.parent:
            self.update_value(node.parent, win_ratio)
