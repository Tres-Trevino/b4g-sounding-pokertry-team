'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot

import random

def pairwise(iterable):
    # pairwise('ABCDEFG') → AB BC CD DE EF FG

    iterator = iter(iterable)
    a = next(iterator, None)

    for b in iterator:
        yield a, b
        a = b

# Ace is ?, King is >, etc.
HAND_TRANSFORM = str.maketrans("AKQJT", "?>=<;")
RANKS = '23456789TJQKA'
SUITS = 'hdcs'

class Player(Bot):
    '''
    A pokerbot.
    '''
    
    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        Nothing.

        Returns:
        Nothing.
        '''
        
        self.can_fold = True


    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        #game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        #round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        #my_cards = round_state.hands[active]  # your cards
        #big_blind = bool(active)  # True if you are the big blind
        
        if (my_bankroll < -10000):
            self.can_fold = False
        if (my_bankroll > 0):
            self.can_fold = True


    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        #my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        previous_state = terminal_state.previous_state  # RoundState before payoffs
        #street = previous_state.street  # 0, 3, 4, or 5 representing when this round ended
        #my_cards = previous_state.hands[active]  # your cards
        #opp_cards = previous_state.hands[1-active]  # opponent's cards or [] if not revealed
        pass


    def get_action(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the engine needs an action from your bot.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Your action.
        '''
        legal_actions = round_state.legal_actions()  # the actions you are allowed to take
        street = round_state.street  # 0, 3, 4, or 5 representing pre-flop, flop, turn, or river respectively
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.deck[:street]  # the board cards
        my_pip = round_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        my_stack = round_state.stacks[active]  # the number of chips you have remaining
        opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        my_contribution = STARTING_STACK - my_stack  # the number of chips you have contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack  # the number of chips your opponent has contributed to the pot
        min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise

        # Pre-flop
        if street == 0:
            # check for any pair
            for s in (c[0] for c in my_cards):
                num = "".join(my_cards).count(s)
                if (num >= 2):
                    return self.get_legal_raise(200, min_raise, max_raise)
                
            # if contains all broadway cards, good
            if all(c[0] in "AKQJT" for c in my_cards):
                return self.get_legal_raise(100, min_raise, max_raise)
                        
            # all same suit
            all_same_suit = my_cards[0][1] == my_cards[1][1] and my_cards[1][1] == my_cards[2][1]
            
            # straight draw
            my_cards_sorted = self.rank_to_ascii_sorted(my_cards)
            card_range = my_cards_sorted[2] - my_cards_sorted[0]
            straight_draw = card_range <= 4
            
            if straight_draw and all_same_suit:
                return self.attempt_check(legal_actions)
            
            if my_pip == 10 and opp_pip == 5:
                return CheckAction()
            return self.attempt_fold(legal_actions)

        # After flop
        pot = my_contribution + opp_contribution

        if self.have_winning_hand(my_cards, board_cards):
            return self.get_legal_raise(max(pot*2, my_stack), min_raise, max_raise)

        our_odds = self.get_hand_odds(my_cards, board_cards)
        pot_odds = self.get_pot_odds(pot, continue_cost)

        if our_odds > pot_odds:
            return self.attempt_check(legal_actions)

        return self.attempt_fold(legal_actions)
    

    def get_legal_raise(self, attempt_raise, min_raise, max_raise):
        if (random.randint(0, 15) == 7):
            return CallAction()
        attempt = min(max_raise, max(attempt_raise, min_raise))
        return RaiseAction(amount=attempt)
    
    def attempt_check(self, legal_actions):
        if (random.randint(0, 15) == 7):
            return RaiseAction(random.randint(20, 30))
        
        return CheckAction() if CheckAction in legal_actions else CallAction()
    
    def attempt_fold(self, legal_actions):
        if CheckAction in legal_actions:
            return CheckAction()
        
        if (random.randint(0, 15) == 7):
            return self.attempt_check(legal_actions)
        
        if self.can_fold:
            return FoldAction()
        return CallAction()


    # this function assumes that the hand is not a winning hand
    def get_hand_odds(self, my_cards, community_cards) -> float:
        cards = my_cards + community_cards
        strcards = ''.join(cards)

        n_hidden_cards = 52 - len(cards)
        rank_occurrences = {s: strcards.count(s) for s in (c[0] for c in cards)}
        n_pairs = list(rank_occurrences.values()).count(2)

        # flush draw
        is_flush_draw = any(strcards.count(s) == 4 for s in SUITS)

        # straight draw
        for r in RANKS:
            new_cards = cards + [r + 'h']
            ranks_sorted = self.rank_to_ascii_sorted(new_cards)
            if self.is_straight(ranks_sorted):
                is_straight_draw = True
                break
        else:
            is_straight_draw = False

        if is_flush_draw and is_straight_draw:
            return 15 / n_hidden_cards
        if is_flush_draw:
            return 9 / n_hidden_cards
        if is_straight_draw:
            return 6 / n_hidden_cards

        # two pair -> full house
        if n_pairs >= 2:
            return 4 / n_hidden_cards

        # pair -> three of a kind
        if n_pairs == 1:
            return 2 / n_hidden_cards

        return 0


    def get_pot_odds(self, pot, cont_cost) -> float:
        pot_pot = pot + cont_cost
        return cont_cost / pot_pot


    def have_winning_hand(self, my_cards, community_cards):
        total_cards = my_cards + community_cards
        total_cards_str = "".join(total_cards)
        
        rank_occurances = {s : total_cards_str.count(s) for s in (c[0] for c in total_cards)}
            
        if 4 in rank_occurances.values():
            return True # we have a four of a kind
        
        if 3 in rank_occurances.values():
            if 2 in rank_occurances.values():
                return True # we have a full house
            return True # we have a three of a kind
        
        # check for straight
        ranks_sorted = self.rank_to_ascii_sorted(total_cards)

        if (self.is_straight(ranks_sorted)):
            return True # we have a straight
            
        # check for flush
        for suit in SUITS:
            if total_cards_str.count(suit) >= 5:
                return True # we have a flush
        
        return False
    

    def rank_to_ascii_sorted(self, cards):
        return list(sorted(ord(c[0].translate(HAND_TRANSFORM)) for c in cards))
        

    def is_straight(self, cards_sorted):
        counter = 0
        for a, b in pairwise(cards_sorted):
            if b - a == 1:
                counter += 1
                
                if counter == 4:
                    return True
            else:
                counter = 0
                
        return False


if __name__ == '__main__':
    run_bot(Player(), parse_args())
