import argparse, pyibl, random, tqdm
import matplotlib.pyplot as plt


DEFAULT_PARTICIPANTS = 2000
DEFAULT_ROUNDS = 50
DEFAULT_NOISE = 0.5
DEFAULT_DECAY = 0.5
DEFAULT_MISMATCH_PENALTY = 0.8


payoffs = ((0, 0), (10, -5), (20, -20), (15, -10), (15, -5), (20, -15))
#          pass    node-1    node-2     node-3     node4     node-5


class PureDefender:

    def honeypots(self):
        return {2, 5}


class EquilibriumDefender:

    def __init__(self):
        self.breakpoints = [ sum((0.303, 0.095, 0.557)[i] for i in range(n)) for n in range(3) ]
        self.results = [ {1, 3, 4}, {2, 3}, {2, 5}, {3, 5} ]

    def honeypots(self):
        n = random.random()
        for i in range(3):
            if n < self.breakpoints[i]:
                return self.results[i]
        return self.results[3]


def linearSimilarity(x, y):
    return 1 - abs(y - x) / 20


class Model:

    def modelName(self):
        return "Basic Model"

    def modelAttributes(self):
        return ()

    def getChoices(self):
        return range(6)

    def makeAgent(self, mismatchPenalty):
        agent = pyibl.Agent(self.modelName() + " Agent", self.modelAttributes())
        if self.modelAttributes():
            agent.similarity(self.modelAttributes(), linearSimilarity)
            # If we have attributes we're doing partial matching on them, and should
            # ignore the identities of the various nodes
            agent.similarity(None, lambda x, y: 1)
            agent.mismatchPenalty = mismatchPenalty
        return (agent, list(self.getChoices()))



class WinModel(Model):

    def modelName(self):
        return "Win Model"

    def modelAttributes(self):
        return ("win",)

    def getChoices(self):
        return [ pyibl.SituationDecision(i, win=p[0]) for (i, p) in zip(range(6), payoffs) ]


class LoseModel(Model):

    def modelName(self):
        return "Lose Model"

    def modelAttributes(self):
        return ("lose",)

    def getChoices(self):
        return [ pyibl.SituationDecision(i, lose=p[1]) for (i, p) in zip(range(6), payoffs) ]


class BothModel(Model):

    def modelName(self):
        return "Both Model"

    def modelAttributes(self):
        return ("win", "lose")

    def getChoices(self):
        return [ pyibl.SituationDecision(i, win=p[0], lose=p[1]) for (i, p) in zip(range(6), payoffs) ]


class NetPayoffModel(Model):

    def modelName(self):
        return "Net Payoff Model"

    def modelAttributes(self):
        return ("netpayoff",)

    def getChoices(self):
        return [ pyibl.SituationDecision(i, netpayoff=sum(p)) for (i, p) in zip(range(6), payoffs) ]


def run(model, defender, participants, rounds, noise, decay, mismatchPenalty, progress=None):
    results = [0]*rounds
    (agent, choices) = model.makeAgent(mismatchPenalty)
    agent.noise = noise
    agent.decay = decay
    for p in range(participants):
        agent.reset()
        agent.prepopulate(25, *choices)
        for r in range(rounds):
            honeypots = defender.honeypots()
            choice = agent.choose(*choices)
            result = payoffs[choice][1 if choice in honeypots else 0]
            results[r] += result
            agent.respond(result)
        if progress:
            progress.update()
    return [ res / participants for res in results ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--participants", "-p", nargs="?", type=int, default=DEFAULT_PARTICIPANTS)
    parser.add_argument("--rounds", "-r", nargs="?", type=int, default=DEFAULT_ROUNDS)
    parser.add_argument("--noise", "-n", nargs="?", type=float, default=DEFAULT_NOISE)
    parser.add_argument("--decay", "-d", nargs="?", type=float, default=DEFAULT_DECAY)
    parser.add_argument("--mismatchpenalty", "-m", nargs="?", type=float, default=DEFAULT_MISMATCH_PENALTY)
    parser.add_argument("--model", "-M", nargs="?", default=None)
    parser.add_argument("--defender", "-D", nargs="?", default=None)
    args = parser.parse_args()
    if args.model:
        models = [ eval(args.model) ]
    else:
        models = [ NetPayoffModel, Model, BothModel, LoseModel, WinModel ]
    if args.defender:
        defenders = [ eval(args.defender) ]
    else:
        defenders = [ PureDefender, EquilibriumDefender ]
    plt.figure(figsize=(8, 9))
    with tqdm.tqdm(total=len(models)*len(defenders)*args.participants) as pb:
        for d, i in zip(defenders, range(1, len(defenders)+1)):
            plt.subplot(len(defenders), 1, i)
            for m in models:
                model = m()
                defender = d()
                plt.plot(range(1, args.rounds + 1),
                         run(model, defender, args.participants, args.rounds,
                             args.noise, args.decay, args.mismatchpenalty, progress=pb),
                         label=model.modelName())
            if i > len(defenders): # bottom subplot only
                plt.xlabel("round")
            plt.ylabel("average payoff")
            plt.axis([1, args.rounds, -15, 20])
            plt.legend(loc="lower right")
            plt.title(d.__name__)
    plt.show()


if __name__ == '__main__':
    main()
