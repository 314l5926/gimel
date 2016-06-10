# coding: utf-8
import math
import requests

from sys import argv


ENDPOINT = 'your experiments endpoint'
API_KEY = 'your API key'


def calc_ab(alpha_a, beta_a, alpha_b, beta_b):
    '''
    Code from https://gist.github.com/arnov/60de0b1ad62d329bc222
    See http://www.evanmiller.org/bayesian-ab-testing.html
    αA is one plus the number of successes for A
    βA is one plus the number of failures for A
    αB is one plus the number of successes for B
    βB is one plus the number of failures for B
    '''
    total = 0.0
    for i in range(alpha_b-1):
        num = math.lgamma(alpha_a+i) + math.lgamma(beta_a+beta_b) + math.lgamma(1+i+beta_b) + math.lgamma(alpha_a+beta_a)
        den = math.log(beta_b+i) + math.lgamma(alpha_a+i+beta_a+beta_b) + math.lgamma(1+i) + math.lgamma(beta_b) + math.lgamma(alpha_a) + math.lgamma(beta_a)

        total += math.exp(num - den)
    return total


def request_results(experiment, order):
    res = requests.get(
        ENDPOINT,
        headers={'x-api-key': API_KEY}
    )
    data = res.json()
    ab_data = {}

    for item in data:
        if item['experiment'] != experiment:
            continue
        goals = item['goals']
        for goal in goals:
            print 'Goal %s' % goal['goal']
            for result in goal['results']:
                success = float(result['successes'])
                trials = float(result['trials'])
                ab_data[result['label']] = (
                    (1 + int(success)),
                    (1 + int(trials - success))
                )
                conversion = 100 * success / trials
                print '%s - %0.2f%% (%s, %s)' % (result['label'], conversion, success, trials)

    testdata = []
    if order:
        for o in order:
            testdata.extend(ab_data[o])
        prob = 100 * calc_ab(*testdata)
        print "Result if  %.2f%% probable" % prob

if __name__ == "__main__":
    request_results(argv[1], argv[2:])
