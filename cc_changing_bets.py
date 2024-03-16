import random
import collections
import math
import time 

class Deck:
    def __init__(self): 
        self.cards = []
    
    def build(self): 
        for i in range(4): 
            for rank in range(1, 14): 
                self.cards += [rank]

    def blackjackify(self): 
        for i, card in enumerate(self.cards): 
            if card > 10: 
                self.cards[i] = 10
        for i, card in enumerate(self.cards): 
            if card == 1:
                self.cards[i] = 11 
        
    def multiply_decks(self, n): 
        self.cards = n * self.cards 

    def copy_cards(self):
        self.cards_copy = list(self.cards)
    
    def shuffle(self): 
        random.shuffle(self.cards)
    
    def draw(self, n=1):
        cards = self.cards[:n]
        self.cards = self.cards[n:]
        return cards 
    
    def replenish(self): 
        self.cards = list(self.cards_copy)
        self.shuffle() 


class Hand: 
    def __init__(self, cards=[]): 
        self.cards = cards
        self.quality = 'hard' # soft if 11 in hand
        self.value = 0 
        self.natbj = False
        self.fin = False
        self.split_aces = False


    def hit(self, deck, n=1): 
        self.cards += deck.draw(n)
        self.update_value()
        self.update_quality()

    def update_value(self): 
        value = sum(self.cards)
        if value == 21 and len(self.cards) == 2: 
            self.natbj = True # split hands can also count as natural blackjack, but doesn't come into play
            self.value = value 

        elif value <= 21:
            self.value = value
        
        else: 
            while (11 in self.cards) and value > 21:
                for i, card in enumerate(self.cards): 
                    if card == 11:
                        self.cards[i] = 1
                        break
                value = sum(self.cards)
            self.value = value 
    
    def update_quality(self):
        if (11 in self.cards):
            self.quality = 'soft'
        else:
            self.quality = 'hard'
    
    def stand(self): 
        self.fin = True 
    
    def double(self, deck): 
        if len(self.cards) == 2:
            self.hit(deck, 1)
            self.stand()
    
    def surrender(self): 
        self.value = 999
        self.stand()
    
    def split(self, deck): 
        if len(self.cards) == 2: 
            if self.cards[0] in [11, 1] and self.cards[1] in [11, 1]: 
                #print('splitting Aces')
                self.cards[0] = 11
                self.cards[1] = 11
                hand2 = Hand(cards=[self.cards[0]])
                hand2.hit(deck)
                hand2.stand()
                hand2.split_aces = True

                self.cards = [self.cards[1]]
                self.hit(deck)
                self.stand() 
                self.split_aces = True
                return hand2 
            
            elif (self.cards[0] == self.cards[1]):
                hand2 = Hand(cards=[self.cards[0]])
                hand2.hit(deck)
                self.cards = [self.cards[1]]
                self.hit(deck)
                return hand2
    
    def __str__(self): 
        s = "" 
        for card in self.cards:
            s += f'{card} '
        s.strip()
        return s
    
    def reset(self): 
        self.cards = []
        self.quality = 'hard'
        self.value = 0 
        self.fin = False
        self.natbj = False
        self.split_aces = False


class Player: 
    def __init__(self, bet=1, total=1000, max_split=3): 
        self.hand = Hand()
        self.bet = bet
        self.ogbet = bet
        self.total = total
        self.ogtotal = total

        self.times_split = 0 
        self.max_split = max_split

        self.hand2 = Hand()
        self.hand3 = Hand()
        self.hand4 = Hand() # you can have a max of 4 hands at a time 

        self.insuranceS = 0
        self.insuranceF = 0

        self.running_count = 0 
        self.true_count = 0 

        # [0, 1, 2, 3, 4, ..., 10, 11]
        self.highlow = [None, -1, 1, 1, 1, 1, 1, 0, 0, 0, -1, -1]

    
    def change_bet(self, bet): 
        self.bet = bet 

    @staticmethod
    def decide(upcard, upcard_list, value, value_list): 
        if upcard in upcard_list: 
            if value in value_list: 
                return True 
            return False 

    # run in order: 
    # split_decide first 
    # stand_decide and hit_decide last 
    def split_decide(self, other, hand): 
        if len(hand.cards) != 2: 
            return False 
        elif hand.split_aces: #check if already split Aces
            return False
        elif self.times_split >= self.max_split:
            return False 
        elif hand.cards[0] != hand.cards[1]: #check for regular pair
            if hand.cards[0] not in [1,11] or hand.cards[1] not in [1,11]: #check for Ace pair
                return False 
        
        # from basic strategy 
        upcard = other.hand.cards[0]
        pair = hand.cards[0]
        if self.decide(upcard, [2, 3, 4, 5, 6, 7], pair, [2, 3, 7]):
            return True 
        if self.decide(upcard, [5, 6], pair, [4]):
            return True 
        if self.decide(upcard, [2, 3, 4, 5, 6], pair, [6]):
            return True 
        if self.decide(upcard, [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 1], pair, [8, 11, 1]):
            return True 
        if self.decide(upcard, [2, 3, 4, 5, 6, 8, 9], pair, [9]):
            return True 
        return False 
    
    def hit_decide(self, other, hand): 
        upcard = other.hand.cards[0]
        if hand.quality == 'hard': 
            if self.decide(upcard, [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 1], hand.value, [4, 5, 6, 7, 8, 9, 10, 11]):
                return True 
            if self.decide(upcard, [2, 3, 7, 8, 9, 10, 11, 1], hand.value, [12]):
                return True 
            if self.decide(upcard, [7, 8, 9, 10, 11, 1], hand.value, [13, 14, 15, 16]):
                return True
            return False 
        if hand.quality == 'soft': 
            if self.decide(upcard, [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 1], hand.value, [12, 13, 14, 15, 16, 17]):
                return True 
            if self.decide(upcard, [9, 10, 11, 1], hand.value, [18]):
                return True 
            return False 
            
    def stand_decide(self, other, hand): 
        upcard = other.hand.cards[0]
        if hand.quality == 'hard': 
            if self.decide(upcard, [4, 5, 6], hand.value, [12]):
                return True 
            if self.decide(upcard, [2, 3, 4, 5, 6], hand.value, [13, 14, 15, 16]):
                return True 
            if self.decide(upcard, [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 1], hand.value, [17, 18, 19, 20, 21]):
                return True
            if self.decide(upcard, [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 1], hand.value, [i for i in range(21, 40)]):
                return True 
            return False 
        if hand.quality == 'soft': 
            if self.decide(upcard, [2, 3, 4, 5, 6, 7, 8], hand.value, [18]):
                return True 
            if self.decide(upcard, [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 1], hand.value, [19, 20, 21]):
                return True 
            return False 
    
    def double_decide(self, other, hand): 
        if len(hand.cards) != 2:
            return False 
        upcard = other.hand.cards[0]
        if hand.quality == 'hard': 
            if self.decide(upcard, [3, 4, 5, 6], hand.value, [9]):
                return True 
            if self.decide(upcard, [2, 3, 4, 5, 6, 7, 8, 9], hand.value, [10]):
                return True 
            if self.decide(upcard, [2, 3, 4, 5, 6, 7, 8, 9, 10], hand.value, [11]):
                return True 
            return False 
        if hand.quality == 'soft': 
            if self.decide(upcard, [6], hand.value, [13]):
                return True 
            if self.decide(upcard, [5, 6], hand.value, [14, 15]):
                return True 
            if self.decide(upcard, [4, 5, 6], hand.value, [16]):
                return True 
            if self.decide(upcard, [3, 4, 5, 6], hand.value, [17, 18]):
                return True 
            return False 
            
    def surrender_decide(self, other, hand): 
        if len(hand.cards) != 2: 
            return False 
        if hand.quality == 'soft': # never surrender on soft hand 
            return False 
        if self.times_split > 0: # can't surrender on split hands
            return False
        upcard = other.hand.cards[0]
        if hand.quality == 'hard': 
            if self.decide(upcard, [10], hand.value, [15]):
                return True 
            if self.decide(upcard, [9, 10, 11, 1], hand.value, [16]):
                return True 
            return False 
        
    def insurance_decide(self, other): 
        if other.hand.cards[0] == 11 or other.hand.cards[0] == 1: 
            if self.true_count > 3: 
                return True  
            
    def deviation_decide(self, other, hand): 
        upcard = other.hand.cards[0]
        if self.true_count > 0: 
            if hand.value == 16 and upcard == 10 and hand.quality == 'hard':
                return 'stand'
        if self.true_count > 4: 
            if hand.value == 15 and upcard == 10 and hand.quality == 'hard': 
                return 'stand'
        if self.true_count > 5: 
            if len(hand.cards) == 2: 
                if hand.split_aces == False:
                    if self.times_split < self.max_split: 
                        if hand.cards[0] == 10 and hand.cards[1] == 10: 
                            if upcard == 5: 
                                return 'split' 
        if self.true_count > 4: 
            if len(hand.cards) == 2: 
                if hand.split_aces == False: 
                    if self.times_split < self.max_split: 
                        if hand.cards[0] == 10 and hand.cards[1] == 10: 
                            if upcard == 6: 
                                return 'split' 
        if self.true_count > 4:
            if len(hand.cards) == 2: 
                if hand.value == 10 and upcard == 10: 
                    return 'double'
        if self.true_count > 2:
            if hand.value == 12 and upcard == 3 and hand.quality == 'hard': 
                return 'stand'
        if self.true_count > 3: 
            if hand.value == 12 and upcard == 2 and hand.quality == 'hard': 
                return 'stand'
        if self.true_count > 1:
            if len(hand.cards) == 2:  
                if hand.value == 11 and upcard in [1,11] and hand.quality == 'hard': 
                    return 'double'
        if self.true_count > 1: 
            if len(hand.cards) == 2: 
                if hand.value == 9 and upcard == 2: 
                    return 'double'
        if self.true_count > 4: 
            if len(hand.cards) == 2:
                if hand.value == 10 and upcard in [1, 11]:
                    return 'double'
        if self.true_count > 3: 
            if len(hand.cards) == 2:
                if hand.value == 9 and upcard == 7:
                    return 'double'
        if self.true_count > 5:
            if hand.value == 16 and upcard == 9 and hand.quality == 'hard':
                if not (hand.cards[0] == 8 and hand.cards[1] == 8): 
                    return 'stand'
        if self.true_count < -1: 
            if hand.value == 13 and upcard == 2 and hand.quality == 'hard':
                return 'hit'
        if self.true_count < 0: 
            if hand.value == 12 and upcard == 4 and hand.quality == 'hard': 
                return 'hit'
        if self.true_count < -2: 
            if hand.value == 12 and upcard == 5 and hand.quality == 'hard':
                return 'hit'
        if self.true_count < -1:
            if hand.value == 12 and upcard == 6 and hand.quality == 'hard':
                return 'hit'
        if self.true_count < -2: 
            if hand.value == 13 and upcard == 3 and hand.quality == 'hard':
                return 'hit'
        
        return False
    

    def fab4_decide(self, other, hand): 
        if len(hand.cards) != 2: 
            return False 
        if hand.quality == 'soft': # never surrender on soft hand 
            return False 
        if self.times_split > 0: # can't surrender on split hands
            return False
        upcard = other.hand.cards[0]
        if self.true_count > 3: 
            if upcard == 10 and hand.value == 14:
                return 'surrender'
        if self.true_count > 0: 
            if upcard == 10 and hand.value == 15: 
                return 'surrender' 
        if self.true_count > 2: 
            if upcard == 9 and hand.value == 15:
                return 'surrender'
        if self.true_count > 1: 
            if upcard in [11, 1] and hand.value == 15:
                return 'surrender' 

        return False


    
    def get_decision(self, other, hand): 
        
        # for s17, never surrender on a pair so split decide first
        if self.split_decide(other, hand):
            return 'split'
        
        # otherwise surrender before anything else
        fab4 = self.fab4_decide(other, hand)
        if fab4 != False: 
            return 'surrender'
        if self.surrender_decide(other, hand):
            return 'surrender' 
        
        # check deviations before basic strategy
        deviation = self.deviation_decide(other, hand) 
        if deviation != False: 
            return deviation 
        
        # follow basic strategy 
        elif self.double_decide(other, hand):
            return 'double'
        elif self.hit_decide(other, hand):
            return 'hit'
        elif self.stand_decide(other, hand):
            return 'stand'

    
    def split(self, deck, hand): 
        if self.times_split == 0: 
            self.hand2 = hand.split(deck)
            self.times_split += 1
        elif self.times_split == 1: 
            self.hand3 = hand.split(deck)
            self.times_split += 1
        elif self.times_split == 2: 
            self.hand4 = hand.split(deck)
            self.times_split += 1
        else:
            print('CANT SPLIT')

    def hit(self, deck, hand): 
        hand.hit(deck)
    
    def stand(self, hand): 
        hand.stand() 
    
    def double(self, deck, hand): 
        hand.double(deck)

    def surrender(self, hand):
        hand.surrender() 

    def play(self, other, deck, hand, loud=False):

        if hand.cards != []:

            if hand.fin == True: 
                decision = 'stand'

            while hand.fin == False: 
                decision = self.get_decision(other, hand)
                # print(decision)
                # print(self.hand.cards)
                # print(other.hand.cards[0])
                if decision == 'split':
                    self.split(deck, hand)
                    self.running_count += self.highlow[self.hand.cards[-1]]
                    self.running_count += self.highlow[self.hand2.cards[-1]]
                    self.true_count = self.running_count / (len(deck.cards) / 52)
                elif decision == 'surrender':
                    self.surrender(hand)
                elif decision == 'double':
                    self.double(deck, hand)
                    self.running_count += self.highlow[hand.cards[-1]]
                    self.true_count = self.running_count / (len(deck.cards) / 52)
                elif decision == 'hit':
                    self.hit(deck, hand)
                    self.running_count += self.highlow[hand.cards[-1]]
                    self.true_count = self.running_count / (len(deck.cards) / 52)
                elif decision == 'stand':
                    self.stand(hand)
                
                if loud: 
                    print('decision', decision)
                    self.print_hand_status(hand)

                    print('running count', self.running_count)
                    print('true count', self.true_count)
            

            # if self.times_split == 3:
            #     print(1, self.hand)
            #     print(2, self.hand2)
            #     print(3, self.hand3)
            #     print(4, self.hand4)
            # if hand.split_aces == True:
            #     print(1, self.hand)
            #     print(2, self.hand2)
            #     print(3, self.hand3)
            #     print(4, self.hand4)
            
            return decision
                    

    def print_hand_status(self, hand):
        if hand.cards != []: 
            if hand == self.hand:
                print('hand1', hand)
            elif hand == self.hand2: 
                print('SPLIT HAND2 !!!!!!!!!!!!!!', hand)
            elif hand == self.hand3:
                print('SPLIT HAND3 !!!!!!!!!!!!!!', hand)
            elif hand == self.hand4:
                print('SPLIT HAND4 !!!!!!!!!!!!!!', hand)
            print('value',hand.value) 
            print()


    def natbj_compare(self, other): 
        
        if self.hand.natbj == True and other.hand.natbj == False: 
            self.total += (self.bet * 1.5)
            return 'win' 
        
        elif self.hand.natbj == True and other.hand.natbj == True: 
            return 'push'
        
        else: 
            insurance = self.insurance_decide(other) 
            if self.hand.natbj == False and other.hand.natbj == True: 
                if insurance != True: 
                    self.total -= self.bet
                else:
                    self.insuranceS += 1
                return 'lose' 
                
            else:
                if insurance == True: 
                    self.total -= (self.bet * 0.5)
                    self.insuranceF += 1
                return  

    def compare(self, other, hand, decision): 

        if hand.cards == []: #for nonsplit hand2, hand3, hand4
            return 
        if decision == 'surrender':
            self.total -= self.bet * 0.5
            return 
        elif decision == 'double':
            change = 2 * self.bet
        else:
            change = self.bet 

        if hand.value > 21 and other.hand.value <= 21: 
            self.total -= change
            return
        elif hand.value <= 21 and other.hand.value > 21:
            self.total += change
            return
        elif hand.value > 21 and other.hand.value > 21: 
            self.total -= change
            return
        elif hand.value > other.hand.value:
            self.total += change
            return
        elif hand.value < other.hand.value: 
            self.total -= change
            return
        else:
            return
    

    def reset(self, deck): 
        self.hand.reset()
        self.hand2.reset()
        self.hand3.reset()
        self.hand4.reset()

        self.hand.hit(deck, 2)
        self.hand2.fin = True 
        self.hand3.fin = True
        self.hand4.fin = True 
        self.times_split = 0 

class Dealer: 
    def __init__(self, hand=Hand()): 
        self.hand = hand

    def hit_until(self, deck, n=17, loud=False): 
        while self.hand.value < n:
            self.hand.hit(deck) 
            if loud: 
                self.print_hand_status()

    def reset(self, deck):
        self.hand.reset() 
        self.hand.hit(deck, 2)

    def print_hand_status(self):
        print('dealer hand', self.hand)
        print('value',self.hand.value) 
        print()


def play_round(player, dealer, deck, freq, initial_bets): 
    player.reset(deck)
    dealer.reset(deck) 

    start_total = player.total

    player.running_count += player.highlow[player.hand.cards[0]]
    player.running_count += player.highlow[player.hand.cards[1]]
    player.running_count += player.highlow[dealer.hand.cards[0]]
    player.true_count = player.running_count / (len(deck.cards) / 52)

    if not(player.natbj_compare(dealer)): 
        decision1 = player.play(dealer, deck, player.hand)
        decision2 = player.play(dealer, deck, player.hand2) 
        decision3 = player.play(dealer, deck, player.hand3)
        decision4 = player.play(dealer, deck, player.hand4)

        dealer.hit_until(deck, 17)
        player.compare(dealer, player.hand, decision1)
        player.compare(dealer, player.hand2, decision2)
        player.compare(dealer, player.hand3, decision3)
        player.compare(dealer, player.hand4, decision4)

    for i in range(1, len(dealer.hand.cards)):
        player.running_count += player.highlow[dealer.hand.cards[i]]
    player.true_count = player.running_count / (len(deck.cards) / 52)
    
    change = player.total - start_total
    freq[change] += 1

    # if player.true_count > 3: 
    #     high_prop = (deck.cards.count(10) + deck.cards.count(11)) / len(deck.cards)
    #     print(len(deck.cards), player.running_count, round(player.true_count,2), round(high_prop,2))

    return change 


def play_round_loud(player, dealer, deck, freq): 
    player.reset(deck)
    dealer.reset(deck) 

    print("********************")
    print('before:')
    player.print_hand_status(player.hand) 
    player.print_hand_status(player.hand2) 
    player.print_hand_status(player.hand3) 
    player.print_hand_status(player.hand4) 
    dealer.print_hand_status()
    start_total = player.total

    player.running_count += player.highlow[player.hand.cards[0]]
    player.running_count += player.highlow[player.hand.cards[1]]
    player.running_count += player.highlow[dealer.hand.cards[0]]
    player.true_count = player.running_count / (len(deck.cards) / 52)

    print("********************")
    print('running count', player.running_count)
    print('true count', player.true_count)

    natbj = player.natbj_compare(dealer)
    if natbj != None: 
        print("********************")
        print('natural blackjack!!!!!!!!!!!!!!!!!')

    elif natbj == None: 
        print("********************")
        print('playing hand 1')
        decision1 = player.play(dealer, deck, player.hand, True)

        print("********************")
        print('playing hand 2')
        decision2 = player.play(dealer, deck, player.hand2, True) 

        print("********************")
        print('playing hand 3')
        decision3 = player.play(dealer, deck, player.hand3, True) 

        print("********************")
        print('playing hand 4')
        decision4 = player.play(dealer, deck, player.hand4, True) 

        print("********************")
        print('dealer turn')
        dealer.hit_until(deck, 17, True)

        print("********************")
        print('after:')
        player.print_hand_status(player.hand) 
        player.print_hand_status(player.hand2) 
        player.print_hand_status(player.hand3) 
        player.print_hand_status(player.hand4) 
        dealer.print_hand_status()

        compare1 = player.compare(dealer, player.hand, decision1)
        compare2 = player.compare(dealer, player.hand2, decision2)
        compare3 = player.compare(dealer, player.hand3, decision3)
        compare4 = player.compare(dealer, player.hand4, decision4)

    for i in range(1, len(dealer.hand.cards)):
        player.running_count += player.highlow[dealer.hand.cards[i]]
        player.true_count = player.running_count / (len(deck.cards) / 52)
        
    print("********************")
    print('running count', player.running_count)
    print('true count', player.true_count)

    change = player.total - start_total
    freq[change] += 1

    print('change', change)
    print('total', player.total)
    print('new bet', player.bet)

    high_prop = (deck.cards.count(10) + deck.cards.count(11)) / len(deck.cards)
    print('high prop', high_prop)

    
    return change 


def main(runs, rounds, decks=6, initial_bet=1, total=0, max_split=3, loud=False, max_bet=500): 
    start = time.time()
    deck1 = Deck()
    deck1.build()
    deck1.multiply_decks(decks)
    deck1.blackjackify()
    deck1.copy_cards()
    deck1.shuffle() 

    if initial_bet > max_bet: 
        initial_bet = max_bet

    player1 = Player(bet=initial_bet, total=total, max_split=max_split)
    dealer1 = Dealer() 
    freq = collections.defaultdict(int)
    run_totals = collections.defaultdict(int)
    initial_bets = collections.defaultdict(int)

    # true_count_totals = collections.defaultdict(int)
    # true_count_freq = collections.defaultdict(int)

    wins = 0 
    losses = 0 
    ties = 0 

    total_games = 0

    for i in range(runs):
        for j in range(rounds): 

            # CHANGE BETS BASED ON TRUE COUNT
            # the higher the true count, the better for the player
            # if 1 <= player1.true_count < 2: 
            if True:
                #player.bet = min(500, (2 ** (round(player.true_count) - 1)))
                # player1.bet = min(max_bet, (10*round(player1.true_count)))
                #player1.bet = min(50, 5*round(player1.true_count))
                player1.bet = 1

                total_games += 1

            else:
                player1.bet = 0
            
            rounded_true_count = round(player1.true_count)
            initial_bets[player1.bet] += 1

            if loud:
                play_round_loud(player1, dealer1, deck1, freq)
            else: 
                change = play_round(player1, dealer1, deck1, freq, initial_bets)

                if player1.bet != 0: 
                    if change > 0: 
                        wins += 1
                    elif change < 0:
                        losses += 1
                    else:
                        ties += 1

            # true_count_totals[rounded_true_count] += change
            # true_count_freq[rounded_true_count] += 1

            
            if len(deck1.cards) < (len(deck1.cards_copy) * 0.25):
                deck1.replenish()
                player1.running_count = 0
                player1.true_count = 0
            
            # print(player1.true_count)
            # if player1.true_count > 5:
            #     print('\t', player1.running_count)
            #     print('\t', len(deck1.cards))
        
        run_totals[player1.total] += 1
        player1.total = 0
        deck1.replenish()
        player1.running_count = 0
        player1.true_count = 0
        #print('reset')

    print(f'FOR {runs*rounds} TOTAL ROUNDS:')
    mean = sum([(x * (freq[x] / (total_games))) for x in freq])
    smom = sum([(x**2 * (freq[x] / (total_games))) for x in freq])
    sd = math.sqrt(smom - mean**2)    
    print('mean', mean)
    print('sd', sd)

    print(f'\nFOR {runs} RUNS ({rounds} ROUNDS PER RUN):')
    mean_run = sum([(x * (run_totals[x] / runs)) for x in run_totals])
    smom_run = sum([(x**2 * (run_totals[x] / runs)) for x in run_totals])
    sd_run = math.sqrt(smom_run - mean_run**2)
    print('mean_run', mean_run)
    print('sd_run', sd_run)

    print('successful insurance', player1.insuranceS)
    print('failed insurance', player1.insuranceF)

    # print('initial bets', sum([(x * (initial_bets[x] / (runs*rounds))) for x in initial_bets]))
    # print('initial bets', initial_bets)

    # print(sum([run_totals[x] for x in run_totals]))
    # print(freq)
    print('total_games', total_games)
    #print('total',player1.total)

    # true_count_freq = dict(sorted(true_count_freq.items(), key=lambda x: x[0]))
    # true_count_totals = dict(sorted(true_count_totals.items(), key=lambda x: x[0]))
    # print(true_count_freq)
    # print(true_count_totals)

    # print(true_count_freq)
    # print(true_count_totals)

    # true_count_avg = {i: round((true_count_totals[i] / true_count_freq[i]),3) for i in true_count_freq}
    # print(true_count_avg)

    print('net wins', wins/total_games)
    print('net losses', losses/total_games)
    print('net pushes', ties/total_games)



    print("finished in ", time.time() - start, " seconds" )
    

if __name__ == "__main__":
    # increasing the number of rounds makes the program run faster than increasing the number of runs
    # 6 decks, reshuffles at 78 cards 
    main(runs=1, rounds=2000000, decks=6, initial_bet=1, total=0, max_split=3, loud=False, max_bet=50)



# CHANGE BETS BASED ON TRUE COUNT 
# the higher the true count, the better for the player
# bet is min(500, (2 ** (round(player.true_count) - 1))) for true_count > 1
# bet is 10 for true count < 1
