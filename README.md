# Blackjack House Edge Project
Our project will be an analysis of blackjack and various blackjack strategies. We will consider two fundamental strategy types: game and betting strategies. Regarding game strategy, we will introduce and attempt to calculate house edge for specified conditions. We wish to explore the effectiveness of various game strategies to determine whether there are any winning strategies and deduce how much of an advantage a given strategy may confer to you. We will introduce and define basic strategy and several advanced strategies, including advantage gambling such as card counting. Regarding betting strategy, we will introduce various probabilistic bet-size functions and attempt to answer whether they are effective and why. We may begin with a discussion of the intuition behind each strategy and develop it with mathematical analysis. To accomplish this, we may look at the expected value for various betting strategies and consider real conditions under which betting may occur. We are also interested in looking at strategies where you raise or fold your initial bet, and we are interested in finding the optimal conditions to raise or fold for different types of players. Some specific betting strategies we are interested in looking at include constant betting strategy, martingale betting strategy, and true count betting strategy.

# Python files:
hit stand only.py        &nbsp;&nbsp;&nbsp;&emsp;&emsp;| Implements basic strategy if hit and stand are the only options available

no_card_counting.py      &emsp;| Implements basic strategy if doubling, splitting, and surrendering are available

martingale.py            &nbsp;&emsp;&emsp;&emsp;&emsp;| Implements martingale betting strategy

card_counting.py         &nbsp;&nbsp;&emsp;&emsp;| Implements changes to playing strategy (deviations) based on card counting 

cc_changing_bets.py      &emsp;| Implements changes to playing strategy and betting strategy based on card counting

