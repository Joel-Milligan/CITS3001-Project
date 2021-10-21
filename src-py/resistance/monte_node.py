from typing import Optional, List
from enum import Enum
from itertools import combinations


class Phase(Enum):
    PROPOSE = 1
    VOTE = 2
    MISSION = 3


class Node():
    def __init__(self) -> None:
        self.wins: int = 0
        self.visits: int = 0
        self.parent: Optional[Node] = None
        self.children: List[Node] = []


class StateNode(Node):
    """
    Represents a single state in a game of The Resistance.
    """

    def __init__(self, phase: Phase, is_spy: bool, num_spys: int, players: List[int], team_size: int = 0, mission: List[int] = []) -> None:
        Node.__init__(self)

        self.phase = phase
        self.is_spy = is_spy
        self.num_spys = num_spys
        self.players = players
        self.team_size = team_size
        self.generate_actions()

    def generate_actions(self) -> None:
        if self.phase == Phase.PROPOSE:
            teams = combinations(self.players, self.team_size)

            for team in teams:
                proposal = ActionNode(self.phase)
                proposal.propose(team)
                proposal.parent = self
                self.children.append(proposal)
        elif self.phase == Phase.VOTE:
            vote_yes = ActionNode(self.phase)
            vote_yes.vote = True
            vote_yes.parent = self

            vote_no = ActionNode(self.phase)
            vote_yes.vote = False
            vote_no.parent = self

            self.children = [vote_yes, vote_no]
        elif self.phase == Phase.MISSION:
            succeed = ActionNode(self.phase)
            succeed.parent = self

            sabotage = ActionNode(self.phase)
            sabotage.parent = self

            if self.is_spy:
                self.children = [succeed, sabotage]
            else:
                self.children = [succeed]


class ActionNode(Node):
    """
    Represents a single action that can be taken from a state in a game of The Resistance.
    """

    def __init__(self, phase: Phase) -> None:
        Node.__init__(self)
        self.phase = phase

    def vote(self, vote: bool) -> None:
        if self.phase == Phase.VOTE:
            self.vote = vote

    def mission(self, action: bool) -> None:
        if self.phase == Phase.MISSION:
            self.action = action

    def propose(self, team: List[int]) -> None:
        if self.phase == Phase.PROPOSE:
            self.proposal = team
