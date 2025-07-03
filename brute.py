import pandas as pd
import numpy as np
import itertools

TEAM_MEANS = {} # mean score for a given team
def team_avg(team):
    """
    calc and store team means
    team: list[tuple(name, score)]
    """
    p0 = team[0]
    p1 = team[1]
    p2 = team[2]
    average = (p0[1] + p1[1] + p2[1])/3
    TEAM_MEANS[p0[0], p1[0], p2[0]] = average # also store these for later
    return average

def valid_team(team):
    """
    from previous results I know the final team means
    are in the range of 6.3->6.7, so can remove any teams outside this range
    will result in 72 teams vs 455 (15c3) teams
    which makes a huge diff down the line when evaluating team combinations
    its roughly 1 minute per 100 million team combinations:
    72c5  = 13,991,544      -> 0.14 minutes
    455c5 = 158,964,146,341 -> 1589.64 minutes
    """
    avg = team_avg(team)
    if avg < 6.3 or avg > 6.7:
        return False
    return True


def valid_teams_combiniation(team_comb):
    """
    is this team combination valid?
    i.e. groups of 5 teams s.t. no person is in 2 teams
    """
    people_set = set()
    for team in team_comb:
        for p in team:
            if p in people_set: # someone is in two teams
                return False
            people_set.add(p)
    return True

def standard_deviation(team_comb):
    """
    compute standard deviation of team means for this combination of teams
    """
    assert(len(team_comb) == 5)
    averages = []
    for team in team_comb:
        p0 = team[0] # tuple(name, score)
        p1 = team[1]
        p2 = team[2]
        average = TEAM_MEANS.get((p0[0], p1[0], p2[0]), None)
        averages.append(average)
    return np.std(averages)

# load data and remove any values that are more than 2 standard deviations from mean (i.e. clear outliers)
df = pd.read_csv('pub_golf_rankings.csv')
df = df.mask(df.sub(df.mean()).div(df.std()).abs().gt(2))

# make list of tuples -> [(p0 name, p0 score), (p1 name, p1 score), ..., (pN name, pN score)]
# avoid lookups for each persons mean
people = [] 
means = df.mean(axis=0)
for name in means.index:
    people.append((name, means[name]))

# all possible 3 person teams
teams = []
for team in itertools.combinations(people, 3):
    if valid_team(team):
        teams.append(team)

# get all valid team combinations
teams_combs = []
for team in itertools.combinations(teams, 5):
    if valid_teams_combiniation(team):
        teams_combs.append(team)

# find the combination which minimises the standard deviation between the teams
min_sd = 10;
min_sd_teams = []
for teams in teams_combs:
    sd = standard_deviation(teams)
    if sd < min_sd:
        min_sd = sd
        min_sd_teams = teams

print(f'minimise sd between team means: sd({min_sd})')
for team in min_sd_teams:
    print('members', [p[0] for p in team])
    print('scores', [float(p[1]) for p in team])
    print('average', np.sum([p[1] for p in team])/3)
    print()

