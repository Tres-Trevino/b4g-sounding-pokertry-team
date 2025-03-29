'''
This file contains the base class that you should implement for your pokerbot.
'''


class Bot():
    '''
    The base class for a pokerbot.
    '''
    
    # Ace is ?, King is >, etc.
    hand_trans = str.maketrans("AKQJT", "?>=<;")

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
        raise NotImplementedError('handle_new_round')

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
        raise NotImplementedError('handle_round_over')

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
        
        # May be useful, but you may choose to not use.
        legal_actions = (
            round_state.legal_actions()
        )  # the actions you are allowed to take
        street = (
            round_state.street
        )  # 0, 2, or 4 representing pre-flop, flop, or turn, respectively
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.deck[:street]  # the board cards
        my_pip = round_state.pips[
            active
        ]  # the number of chips you have contributed to the pot this round of betting
        opp_pip = round_state.pips[
            1 - active
        ]  # the number of chips your opponent has contributed to the pot this round of betting
        my_stack = round_state.stacks[active]  # the number of chips you have remaining
        opp_stack = round_state.stacks[
            1 - active
        ]  # the number of chips your opponent has remaining
        continue_cost = (
            opp_pip - my_pip
        )  # the number of chips needed to stay in the pot
        my_contribution = (
            STARTING_STACK - my_stack
        )  # the number of chips you have contributed to the pot
        opp_contribution = (
            STARTING_STACK - opp_stack
        )  # the number of chips your opponent has contributed to the pot
        
        cards = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        suits = ['h', 'd', 's', 'c']
        
        # Pre-flop
        if street == 0:
            
            # check for any pair
            for s in (c[0] for c in my_cards):
                num = "".join(my_cards).count(s)
                if (num >= 2):
                    return RaiseAction(amount=20) #arbitrary number
                
            # if contains all broadway cards, good
            if all(c[0] in "AKQJT" for c in my_cards):
                return RaiseAction(amount=10) #arbitrary number
                        
            # all same suit
            all_same_suit = my_cards[0][1] == my_cards[1][1] and my_cards[1][1] == my_cards[2][1]
            
            # straight draw
            my_cards_sorted = list(sorted(ord(c[0].translate(hand_trans)) for c in my_cards))
            card_range = my_cards_sorted[2] - my_cards_sorted[0]
            straight_draw = card_range <= 4
            
            if (straight_draw and all_same_suit):
                return CheckAction if CheckAction in legal_actions else CallAction
            
            return FoldAction
            
        
        raise NotImplementedError('get_action')
