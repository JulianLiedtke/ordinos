from src.crypto.paillier_abb import PaillierABB
from src.crypto.plain_abb import PlainABB
from src.election.borda.borda_implementations import EscElection
from src.election.election_authority import ElectionAuthority
from src.election.condorcet.condorcet_election_system import Condorcet
from src.election.condorcet.condorcet_no_winner_evaluations import SmithEvaluation
from src.protocols.sublinear import SubLinearProtocolSuite
from src.util.logging import setup_logging
from src.util.point_vote import PointVote
import logging
from src.protocols.protocol_suite import EmptyProtocolSuite


def esc_2019(key_generator):
    """https://de.wikipedia.org/wiki/Eurovision_Song_Contest_2019#Punktetafel_Finale"""
    candidates = ['Malta', 'Albanien', 'Tschechien', 'Deutschland', 'Russland', 'Dänemark', 'San Marino', 'Nordmazedonien', 'Schweden', 'Slowenien', 'Zypern', 'Niederlande', 'Griechenland', 'Israel', 'Norwegen', 'Vereinigtes Königreich', 'Island', 'Estland', 'Weißrussland', 'Aserbaidschan', 'Frankreich', 'Italien', 'Serbien', 'Schweiz', 'Australien', 'Spanien']
    e = ElectionAuthority(key_generator, EscElection(candidates))
    #e = ElectionAuthority(key_generator, Condorcet(candidates, [SmithEvaluation], leak_better_half=False))
    e.add_generic_vote(PointVote([-1, -1, 10, -1, -1, -1, -1, 5, 2, 3, -1, 12, -1, -1, 4, -1, -1, -1, -1, 8, -1, 6, -1, 1, 7, -1]), count=1)   # PT - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, 10, 1, -1, -1, -1, -1, -1, 8, -1, -1, 6, -1, 3, -1, -1, -1, 2, 7, -1, 5, 4, 12]), count=1)   # PT - Televoting;
    e.add_generic_vote(PointVote([10, 7, -1, -1, 12, -1, -1, 8, -1, 4, 3, -1, 6, -1, -1, -1, -1, -1, 1, -1, -1, 5, -1, -1, 2, -1]), count=1)   # AZ - Jury;
    e.add_generic_vote(PointVote([4, -1, -1, -1, 12, -1, 10, 3, -1, -1, -1, 7, -1, -1, 1, -1, -1, -1, 5, -1, -1, 6, -1, 8, -1, 2]), count=1)   # AZ - Televoting;
    e.add_generic_vote(PointVote([-1, 2, -1, -1, 10, -1, 1, 3, 5, -1, 6, 7, 4, -1, -1, -1, -1, -1, -1, 8, -1, 12, -1, -1, -1, -1]), count=1)   # MT - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, 4, -1, -1, 5, 6, -1, -1, 10, -1, -1, 7, -1, 1, -1, -1, 2, -1, 12, -1, 8, 3, -1]), count=1)   # MT - Televoting;
    e.add_generic_vote(PointVote([5, 8, -1, -1, 6, -1, -1, -1, -1, -1, 1, 7, -1, -1, -1, -1, 2, -1, -1, 4, -1, 12, -1, 3, 10, -1]), count=1)   # MK - Jury;
    e.add_generic_vote(PointVote([6, 12, -1, -1, -1, -1, 8, -1, -1, 2, -1, 7, -1, -1, 5, -1, -1, -1, -1, 1, -1, 3, 10, 4, -1, -1]), count=1)   # MK - Televoting;
    e.add_generic_vote(PointVote([-1, 7, -1, -1, 10, -1, -1, 1, -1, -1, 5, 3, 8, -1, -1, -1, 6, -1, -1, 4, -1, 12, -1, 2, -1, -1]), count=1)   # SM - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, 12, -1, -1, -1, -1, -1, 7, 6, 10, 1, 3, -1, 2, -1, -1, 4, -1, 8, -1, 5, -1, -1]), count=1)   # SM - Televoting;
    e.add_generic_vote(PointVote([8, -1, 4, -1, 5, 7, -1, 3, 12, -1, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 6, -1, 10, 2, -1]), count=1)   # NL - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, -1, 5, -1, 1, 8, -1, -1, -1, -1, -1, 12, -1, 7, -1, -1, 4, -1, 10, -1, 6, 2, 3]), count=1)   # NL - Televoting;
    e.add_generic_vote(PointVote([6, 8, 1, -1, 10, 3, -1, 7, -1, -1, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 2, 12, -1, 4, -1]), count=1)   # ME - Jury;
    e.add_generic_vote(PointVote([-1, 7, -1, -1, 10, -1, 8, 6, -1, 4, -1, 1, -1, -1, -1, -1, 2, -1, -1, 3, -1, 5, 12, -1, -1, -1]), count=1)   # ME - Televoting;
    e.add_generic_vote(PointVote([-1, -1, 8, -1, 6, 2, -1, -1, 12, -1, -1, 7, -1, -1, -1, -1, -1, -1, 1, 5, 3, -1, 4, 10, -1, -1]), count=1)   # EE - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, 12, 6, -1, -1, 3, 7, -1, 8, -1, -1, 10, -1, 5, -1, -1, 1, -1, -1, -1, 4, 2, -1]), count=1)   # EE - Televoting;
    e.add_generic_vote(PointVote([4, -1, -1, -1, -1, 5, -1, 8, -1, 10, -1, -1, -1, -1, 1, -1, 3, -1, -1, 2, 6, -1, 7, -1, 12, -1]), count=1)   # PL - Jury;
    e.add_generic_vote(PointVote([-1, -1, 1, -1, 3, -1, -1, -1, -1, 4, -1, 10, -1, -1, 8, -1, 12, -1, -1, 2, -1, 7, -1, 5, 6, -1]), count=1)   # PL - Televoting;
    e.add_generic_vote(PointVote([-1, -1, 12, -1, -1, 4, -1, 10, 8, -1, 1, 7, -1, -1, -1, 2, -1, -1, -1, 5, -1, 3, -1, 6, -1, -1]), count=1)   # NO - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, 1, 5, -1, -1, 12, -1, -1, 8, -1, -1, -1, -1, 10, 2, -1, 3, -1, 7, -1, 6, 4, -1]), count=1)   # NO - Televoting;
    e.add_generic_vote(PointVote([-1, -1, 6, -1, 2, -1, -1, -1, 12, 1, 5, 8, -1, -1, -1, -1, -1, -1, -1, 7, -1, 4, -1, 3, 10, -1]), count=1)   # ES - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, 2, -1, -1, -1, 6, -1, -1, 8, -1, -1, 7, -1, 3, -1, -1, 1, 4, 12, -1, 10, 5, -1]), count=1)   # ES - Televoting;
    e.add_generic_vote(PointVote([-1, -1, 3, -1, -1, -1, -1, 12, 6, -1, -1, 8, -1, -1, 1, -1, -1, -1, -1, 4, 5, 7, 2, 10, -1, -1]), count=1)   # AT - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, 5, -1, -1, -1, -1, 2, -1, 7, -1, -1, 8, -1, 6, -1, -1, 1, -1, 10, 4, 12, 3, -1]), count=1)   # AT - Televoting;
    e.add_generic_vote(PointVote([-1, -1, 1, -1, 4, 3, -1, 12, 10, -1, -1, 6, -1, -1, -1, -1, -1, -1, -1, 7, 2, -1, -1, 5, 8, -1]), count=1)   # UK - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, -1, 6, -1, -1, 5, -1, 1, 4, -1, -1, 12, -1, 8, -1, -1, 3, -1, -1, -1, 7, 10, 2]), count=1)   # UK - Televoting;
    e.add_generic_vote(PointVote([8, 1, 4, -1, -1, 12, -1, 10, 2, -1, -1, -1, -1, -1, -1, -1, -1, 5, -1, 7, 3, -1, -1, -1, 6, -1]), count=1)   # IT - Jury;
    e.add_generic_vote(PointVote([-1, 12, -1, -1, 8, 4, -1, -1, -1, -1, -1, 5, -1, -1, 10, -1, 7, -1, -1, 1, 2, -1, -1, 3, 6, -1]), count=1)   # IT - Televoting;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, 1, -1, -1, 12, 6, -1, 7, -1, 4, -1, -1, -1, -1, -1, -1, 8, 3, 5, -1, 10, 2, -1]), count=1)   # AL - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, 12, -1, 10, 6, -1, -1, -1, 7, 2, -1, 5, -1, -1, -1, -1, 3, -1, 8, -1, 4, 1, -1]), count=1)   # AL - Televoting;
    e.add_generic_vote(PointVote([-1, -1, 12, -1, -1, 6, -1, 10, 4, -1, -1, 1, -1, -1, -1, 2, -1, -1, 8, 5, -1, 7, -1, 3, -1, -1]), count=1)   # HU - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, 7, -1, 6, -1, -1, 3, -1, 8, -1, -1, 10, -1, 12, -1, -1, 2, 1, 4, -1, 5, -1, -1]), count=1)   # HU - Televoting;
    e.add_generic_vote(PointVote([1, -1, 8, -1, 5, 4, -1, 12, 2, -1, -1, 3, -1, -1, 7, -1, -1, -1, -1, 6, -1, -1, -1, -1, 10, -1]), count=1)   # MD - Jury;
    e.add_generic_vote(PointVote([-1, -1, 2, -1, 12, -1, 8, -1, -1, -1, -1, 6, -1, 7, 3, -1, 1, -1, -1, 10, -1, 5, -1, 4, -1, -1]), count=1)   # MD - Televoting;
    e.add_generic_vote(PointVote([-1, -1, -1, 2, 3, -1, -1, 5, 12, -1, -1, 8, -1, -1, 6, -1, -1, -1, -1, 7, -1, 1, -1, 10, 4, -1]), count=1)   # IE - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, 5, -1, -1, -1, 2, -1, -1, 8, -1, -1, 12, 3, 6, 1, -1, -1, -1, 4, -1, 7, 10, -1]), count=1)   # IE - Televoting;
    e.add_generic_vote(PointVote([12, -1, -1, -1, 1, -1, -1, 10, 2, -1, 8, 6, 3, -1, -1, -1, -1, -1, -1, 5, -1, 7, -1, 4, -1, -1]), count=1)   # BY - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, 12, -1, 1, -1, -1, 5, -1, 10, -1, -1, 8, -1, 7, -1, -1, 6, -1, 3, -1, 4, 2, -1]), count=1)   # BY - Televoting;
    e.add_generic_vote(PointVote([4, -1, 3, -1, 5, -1, -1, 10, 12, -1, -1, 6, -1, -1, -1, 2, -1, -1, 1, -1, -1, 8, -1, 7, -1, -1]), count=1)   # AM - Jury;
    e.add_generic_vote(PointVote([6, -1, -1, -1, 12, -1, -1, -1, 2, -1, -1, 10, -1, -1, 5, -1, 3, -1, -1, -1, 4, 7, -1, 8, 1, -1]), count=1)   # AM - Televoting;
    e.add_generic_vote(PointVote([-1, 2, 8, -1, 6, -1, -1, 7, 1, -1, -1, 5, -1, -1, -1, -1, -1, -1, -1, 10, -1, -1, 3, 4, 12, -1]), count=1)   # RO - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, 7, -1, -1, -1, -1, -1, -1, 12, -1, 3, 4, -1, 5, -1, -1, 6, 1, 8, -1, 10, 2, -1]), count=1)   # RO - Televoting;
    e.add_generic_vote(PointVote([3, 2, -1, -1, 10, -1, -1, -1, 7, -1, -1, 5, 12, -1, -1, -1, -1, -1, -1, 6, 4, 8, -1, 1, -1, -1]), count=1)   # CY - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, 10, -1, -1, -1, -1, -1, -1, 6, 12, 5, 1, -1, -1, -1, -1, -1, 3, 8, -1, 7, 2, 4]), count=1)   # CY - Televoting;
    e.add_generic_vote(PointVote([-1, -1, 5, 3, 4, -1, -1, 7, 12, -1, -1, 6, -1, -1, -1, -1, 8, -1, -1, 2, 10, -1, 1, -1, -1, -1]), count=1)   # AU - Jury;
    e.add_generic_vote(PointVote([4, -1, 2, -1, -1, -1, -1, -1, 8, -1, -1, 6, -1, -1, 12, -1, 10, -1, -1, 1, 3, 5, -1, 7, -1, -1]), count=1)   # AU - Televoting;
    e.add_generic_vote(PointVote([6, 3, -1, -1, -1, -1, 5, 4, -1, -1, 8, -1, 10, -1, -1, -1, 2, -1, 7, 12, -1, -1, -1, -1, -1, 1]), count=1)   # RU - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, -1, -1, -1, -1, -1, 6, -1, 5, -1, -1, 10, -1, 7, -1, 8, 12, -1, 1, 3, 2, 4, -1]), count=1)   # RU - Televoting;
    e.add_generic_vote(PointVote([3, -1, -1, -1, -1, 1, -1, 7, 2, -1, -1, 8, -1, -1, 5, -1, -1, -1, -1, -1, 4, 12, -1, 6, 10, -1]), count=1)   # DE - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, 8, 4, -1, -1, 1, 3, -1, 7, -1, -1, 12, -1, 2, -1, -1, -1, -1, 6, -1, 10, 5, -1]), count=1)   # DE - Televoting;
    e.add_generic_vote(PointVote([-1, -1, 5, -1, -1, 1, -1, -1, -1, -1, 2, 6, 3, -1, -1, -1, 10, -1, -1, -1, 8, 12, -1, 7, 4, -1]), count=1)   # BE - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, 1, -1, -1, -1, 2, -1, -1, 12, -1, -1, 7, -1, 3, -1, -1, -1, 10, 8, -1, 5, 4, 6]), count=1)   # BE - Televoting;
    e.add_generic_vote(PointVote([2, -1, 1, -1, 3, -1, -1, -1, -1, -1, 7, 12, -1, -1, 4, -1, -1, -1, -1, 5, -1, 8, -1, 10, 6, -1]), count=1)   # SE - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, -1, 7, -1, 2, -1, -1, -1, 6, -1, -1, 12, -1, 8, 10, -1, 3, -1, 4, -1, 1, 5, -1]), count=1)   # SE - Televoting;
    e.add_generic_vote(PointVote([-1, -1, 7, -1, 2, -1, -1, 10, 5, -1, -1, 6, -1, -1, -1, -1, -1, 1, -1, -1, 3, 12, 4, 8, -1, -1]), count=1)   # HR - Jury;
    e.add_generic_vote(PointVote([-1, 1, -1, -1, -1, -1, 2, 7, -1, 10, -1, 4, -1, -1, 5, -1, 3, -1, -1, -1, -1, 12, 8, 6, -1, -1]), count=1)   # HR - Televoting;
    e.add_generic_vote(PointVote([-1, -1, 7, 5, 1, -1, -1, -1, 8, 4, -1, 12, -1, -1, -1, -1, 6, -1, -1, 10, -1, 3, -1, -1, 2, -1]), count=1)   # LT - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, 12, -1, -1, -1, 3, -1, -1, 7, -1, -1, 8, -1, 6, 4, -1, 5, -1, 10, -1, 2, 1, -1]), count=1)   # LT - Televoting;
    e.add_generic_vote(PointVote([-1, -1, 4, -1, -1, 2, -1, 12, 8, -1, -1, -1, -1, -1, -1, -1, -1, 6, -1, 3, 1, 10, -1, 5, 7, -1]), count=1)   # RS - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, 8, -1, 1, 12, -1, 10, -1, 3, -1, -1, 4, -1, 5, -1, -1, -1, -1, 7, -1, 6, -1, 2]), count=1)   # RS - Televoting;
    e.add_generic_vote(PointVote([-1, -1, 6, -1, -1, -1, -1, 8, 12, -1, -1, 7, -1, -1, -1, -1, -1, -1, -1, 4, 1, 3, 2, 5, 10, -1]), count=1)   # IS - Jury;
    e.add_generic_vote(PointVote([-1, -1, 2, -1, -1, 4, 1, -1, 8, -1, -1, 5, -1, -1, 12, -1, -1, 3, -1, -1, -1, 6, -1, 7, 10, -1]), count=1)   # IS - Televoting;
    e.add_generic_vote(PointVote([-1, -1, 12, -1, -1, 7, -1, -1, 2, 4, 6, 8, -1, -1, -1, 1, -1, -1, -1, 10, 5, -1, -1, 3, -1, -1]), count=1)   # GE - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, 8, -1, 10, 2, 6, -1, 12, 5, -1, 4, -1, -1, 3, -1, -1, 7, -1, 1, -1, -1, -1, -1]), count=1)   # GE - Televoting;
    e.add_generic_vote(PointVote([5, 3, -1, -1, 10, -1, 6, 1, -1, 4, 12, -1, -1, -1, -1, -1, -1, -1, -1, 8, -1, 7, -1, -1, 2, -1]), count=1)   # GR - Jury;
    e.add_generic_vote(PointVote([-1, 5, -1, -1, 8, -1, -1, -1, -1, -1, 12, 6, -1, -1, -1, -1, 2, -1, -1, -1, 1, 10, -1, 7, 3, 4]), count=1)   # GR - Televoting;
    e.add_generic_vote(PointVote([1, -1, 3, -1, 4, 7, -1, 8, 10, -1, -1, 12, -1, -1, -1, -1, -1, 5, -1, 6, -1, 2, -1, -1, -1, -1]), count=1)   # LV - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, 12, -1, -1, -1, -1, 2, -1, 5, -1, -1, 8, -1, 7, 10, -1, 4, -1, 3, -1, 1, 6, -1]), count=1)   # LV - Televoting;
    e.add_generic_vote(PointVote([3, -1, -1, -1, -1, -1, -1, 7, 12, 10, -1, 6, -1, -1, -1, -1, 4, 1, -1, 5, 2, 8, -1, -1, -1, -1]), count=1)   # CZ - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, 12, -1, -1, -1, -1, -1, -1, 4, -1, 3, 10, -1, 6, 1, -1, 7, -1, 2, -1, 5, 8, -1]), count=1)   # CZ - Televoting;
    e.add_generic_vote(PointVote([-1, -1, -1, 8, 3, -1, -1, 10, 12, -1, -1, 7, -1, -1, 5, -1, -1, 2, -1, 4, -1, 1, -1, 6, -1, -1]), count=1)   # DK - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, -1, -1, -1, -1, 10, -1, -1, 7, -1, -1, 12, -1, 4, 8, -1, 5, -1, 3, -1, 6, 2, 1]), count=1)   # DK - Televoting;
    e.add_generic_vote(PointVote([-1, -1, 3, -1, -1, 1, -1, 7, 10, -1, -1, 12, -1, -1, -1, -1, 5, -1, -1, 6, -1, 8, -1, 2, 4, -1]), count=1)   # FR - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, 3, 4, -1, -1, -1, -1, -1, 5, -1, 12, 8, -1, 1, -1, -1, -1, -1, 10, -1, 2, 6, 7]), count=1)   # FR - Televoting;
    e.add_generic_vote(PointVote([1, -1, 4, -1, -1, -1, -1, 7, 12, 6, -1, 8, -1, -1, -1, -1, -1, -1, -1, 2, -1, 5, -1, 3, 10, -1]), count=1)   # FI - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, 4, -1, -1, -1, 7, 1, -1, 5, -1, -1, 10, -1, 12, 8, -1, -1, -1, 3, -1, 2, 6, -1]), count=1)   # FI - Televoting;
    e.add_generic_vote(PointVote([-1, -1, -1, 6, 3, -1, -1, 12, 8, -1, -1, 10, -1, -1, 7, 1, -1, -1, -1, -1, 2, 5, -1, -1, 4, -1]), count=1)   # CH - Jury;
    e.add_generic_vote(PointVote([-1, 10, -1, -1, -1, 1, -1, 2, 4, -1, -1, 6, -1, -1, 8, -1, -1, -1, -1, -1, 3, 12, 7, -1, -1, 5]), count=1)   # CH - Televoting;
    e.add_generic_vote(PointVote([1, -1, 12, -1, -1, 4, -1, 2, 7, -1, -1, 6, -1, -1, -1, -1, -1, -1, -1, 10, 3, 8, -1, 5, -1, -1]), count=1)   # SI - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, -1, 3, -1, 12, -1, -1, -1, 5, -1, -1, 6, -1, 7, 1, -1, -1, -1, 8, 10, 4, 2, -1]), count=1)   # SI - Televoting;
    e.add_generic_vote(PointVote([4, -1, -1, -1, -1, -1, -1, -1, 6, -1, -1, 12, -1, -1, -1, -1, -1, 8, -1, 7, 2, 10, -1, 3, 5, -1]), count=1)   # IL - Jury;
    e.add_generic_vote(PointVote([-1, -1, -1, -1, 12, 1, -1, -1, -1, -1, -1, 2, -1, -1, 10, -1, -1, -1, -1, 3, 4, 8, -1, 7, 6, 5]), count=1)   # IL - Televoting;

    e.trigger_evaluation() # winner were the Netherlands


if __name__ == '__main__':
    setup_logging(logging.DEBUG)
    
    esc_2019(lambda: PlainABB.gen_trustees(256, 3, 2, EmptyProtocolSuite))
