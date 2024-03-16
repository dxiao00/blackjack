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

        # self.insuranceS = 0
        # self.insuranceF = 0

        # self.running_count = 0 
        # self.true_count = 0 

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

    def hit_decide(self, other, hand):
        if hand.value < 17:
            return True
        return False
 
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
        if hand.value >= 17:
            return True
        return False
    
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

    
    def get_decision(self, other, hand): 
        if self.hit_decide(other, hand):
            return 'hit'
        
        else:
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

                if decision == 'hit':
                    self.hit(deck, hand)
                    # self.running_count += self.highlow[hand.cards[-1]]
                    # self.true_count = self.running_count / (len(deck.cards) / 52)
                elif decision == 'stand':
                    self.stand(hand)
                
                if loud: 
                    print('decision', decision)
                    self.print_hand_status(hand)

                    # print('running count', self.running_count)
                    # print('true count', self.true_count)
            
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
            # insurance = self.insurance_decide(other) 
            if self.hand.natbj == False and other.hand.natbj == True: 
                # if insurance != True: 
                if True:
                    self.total -= self.bet
                # else:
                #     self.insuranceS += 1
                return 'lose' 
                
            else:
                # if insurance == True: 
                #     self.total -= (self.bet * 0.5)
                #     self.insuranceF += 1
                return  

    def compare(self, other, hand, decision): 

        if hand.cards == []: #for nonsplit hand2, hand3, hand4
            return 
        if decision == 'surrender':
            self.total -= self.bet * 0.5
            return 'lose'
        elif decision == 'double':
            change = 2 * self.bet
        else:
            change = self.bet 

        if hand.value > 21 and other.hand.value <= 21: 
            self.total -= change
            return 'lose'
        elif hand.value <= 21 and other.hand.value > 21:
            self.total += change
            return 'win'
        elif hand.value > 21 and other.hand.value > 21: 
            self.total -= change
            return 'lose'
        elif hand.value > other.hand.value:
            self.total += change
            return 'win'
        elif hand.value < other.hand.value: 
            self.total -= change
            return 'lose'
        else:
            return 'push'
    

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

    # # CHANGE BETS BASED ON TRUE COUNT
    # # the higher the true count, the better for the player
    # if player.true_count > 1: 
    #     #player.bet = min(500, (2 ** (round(player.true_count) - 1)))
    #     player.bet = min(50, (10*round(player.true_count)))
    # else:
    #     player.bet = 10
    initial_bets[player.bet] += 1

    # player.running_count += player.highlow[player.hand.cards[0]]
    # player.running_count += player.highlow[player.hand.cards[1]]
    # player.running_count += player.highlow[dealer.hand.cards[0]]
    # player.true_count = player.running_count / (len(deck.cards) / 52)

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

    # for i in range(1, len(dealer.hand.cards)):
    #     player.running_count += player.highlow[dealer.hand.cards[i]]
    # player.true_count = player.running_count / (len(deck.cards) / 52)
    
    change = player.total - start_total
    freq[change] += 1

    # if player.true_count > 3: 
    #     high_prop = (deck.cards.count(10) + deck.cards.count(11)) / len(deck.cards)
    #     print(len(deck.cards), player.running_count, round(player.true_count,2), round(high_prop,2))


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

    # player.running_count += player.highlow[player.hand.cards[0]]
    # player.running_count += player.highlow[player.hand.cards[1]]
    # player.running_count += player.highlow[dealer.hand.cards[0]]
    # player.true_count = player.running_count / (len(deck.cards) / 52)

    # print("********************")
    # print('running count', player.running_count)
    # print('true count', player.true_count)

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

    # for i in range(1, len(dealer.hand.cards)):
    #     player.running_count += player.highlow[dealer.hand.cards[i]]
    #     player.true_count = player.running_count / (len(deck.cards) / 52)
        
    # print("********************")
    # print('running count', player.running_count)
    # print('true count', player.true_count)

    change = player.total - start_total
    freq[change] += 1

    print('change', change)
    print('total', player.total)
    print('new bet', player.bet)

    high_prop = (deck.cards.count(10) + deck.cards.count(11)) / len(deck.cards)
    print('high prop', high_prop)

    
    return change 


def main(runs, rounds, decks=6, initial_bet=1, total=0, max_split=3, loud=False): 
    start = time.time()
    deck1 = Deck()
    deck1.build()
    deck1.multiply_decks(decks)
    deck1.blackjackify()
    deck1.copy_cards()
    deck1.shuffle() 

    player1 = Player(bet=initial_bet, total=total, max_split=max_split)
    dealer1 = Dealer() 
    freq = collections.defaultdict(int)
    run_totals = collections.defaultdict(int)
    initial_bets = collections.defaultdict(int)

    for i in range(runs):
        for j in range(rounds): 

            if loud:
                play_round_loud(player1, dealer1, deck1, freq)
            else: 
                play_round(player1, dealer1, deck1, freq, initial_bets)
            
            if len(deck1.cards) < (len(deck1.cards_copy) * 0.25):
                deck1.replenish()
                # player1.running_count = 0
                # player1.true_count = 0
            
            # print(player1.true_count)
            # if player1.true_count > 5:
            #     print('\t', player1.running_count)
            #     print('\t', len(deck1.cards))
        
        run_totals[player1.total] += 1
        player1.total = player1.ogtotal
        player1.bet = player1.ogbet
        deck1.replenish()
        # player1.running_count = 0
        # player1.true_count = 0
        #print('reset')

    print(f'FOR {runs*rounds} TOTAL ROUNDS:')
    mean = sum([(x * (freq[x] / (runs*rounds))) for x in freq])
    smom = sum([(x**2 * (freq[x] / (runs*rounds))) for x in freq])
    sd = math.sqrt(smom - mean**2)    
    print('mean', mean)
    print('sd', sd)

    print(f'\nFOR {runs} RUNS ({rounds} ROUNDS PER RUN):')
    mean_run = sum([(x * (run_totals[x] / runs)) for x in run_totals])
    smom_run = sum([(x**2 * (run_totals[x] / runs)) for x in run_totals])
    sd_run = math.sqrt(smom_run - mean_run**2)
    print('mean_run', mean_run)
    print('sd_run', sd_run)

    # print('successful insurance', player1.insuranceS)
    # print('failed insurance', player1.insuranceF)

    print('initial bets', sum([(x * (initial_bets[x] / (runs*rounds))) for x in initial_bets]))
    print('initial bets', initial_bets)

    # print(sum([run_totals[x] for x in run_totals]))
    print(freq)
    print('net wins', sum(freq[i] for i in freq if i > 0) / rounds)
    print('net losses', sum(freq[i] for i in freq if i < 0) / rounds)
    print('net pushes', sum(freq[i] for i in freq if i == 0) / rounds)
    #print('total',player1.total)
    print("finished in ", time.time() - start, " seconds" )
    


if __name__ == "__main__":
    # increasing the number of rounds makes the program run faster than increasing the number of runs
    # 6 decks, reshuffles at 78 cards 
    main(runs=1, rounds=10000000, decks=10, initial_bet=1, total=0, max_split=0, loud=False)



# get average initial bets