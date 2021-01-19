# AIC-IBL
This is a selection of five PyIBL models for playing the Honeypot
game, embedded in a framework for using multiple models and multiple
defenders, and graphing the results.

Two defenders are provided, the pure defender and the equilibrium
defender. Others can be added by defining suitable classes with a
honeypots() method which should return a set of integers selected from
1 through 5, corresponding to the five nodes in the game. This method
is called at each iteration, and the resulting set is the set of
honeypots. The defender classes can be added to the list in main().

The main() function runs the five models against each of the
defenders, and draws graphs of the payoff received by the modeled
player in each round, averaged over the simulated players. By default
there are two thousand simulated players, but this can be changed with
the -p command line argument.

Models are defined by subclassing the Model class, and adding them to
the appropriate list in main().

The five models provided are:

1) A basic model that is just a simple IBL model working from the
identity of each Node (plus Pass). It ignores the possible payoffs,
beyond what it experiences.

The remaining models all have one or two attributes, and use only the
values of those to make their choices, ignoring the identity of the
various nodes. It uses partial matching, with a linear similarity, on
the relevant attributes.

2) The win model has one attribute, the amount it can win from a node
if it is not a honeypot.

3) The lose model is similar, but uses the amount it would lose if the
node is a honeypot.

4) The both model has two attributes, both of those from the win and lose
models.

5) The net payoff model has one attribute, the sum of the attributes
in the win and lose models. That is, it bases its decisions on the
closeness of a choice to choices with the same net result of winning
and losing equal numbers of times.

The main function can take a variety of command line arguments for
changing parameters, or choosing a single model and/or defender. The
default paramters are

noise: 0.5
decay: 0.5
mismatch penalty: None for the basic model, and 0.8 for the remaining models
participants: 2,000
rounds: 50

To run it with the default settings simply execute

python honeypot.py

Note that, because it uses partial matching, this depends upon the no
yet released version 3 of PyIBL. Besides having this version of PyIBL
available, along with its dependencies, this also expects to have
matplotlib available.

The included file honeypot-graphs.png is a result of running 2,000
participants over the five models and both defenders.
