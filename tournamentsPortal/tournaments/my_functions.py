import math
import random
import datetime
from tournaments import models


# DRAW CALCULATE
def calculate_draw(id):
    participations = models.Participation.objects.filter(tournament__id=id).order_by('ranking')
    tournament = models.Tournament.objects.get(id=id)
    print(len(participations))

    for i in range(tournament.num_of_seeded):
        participation = participations[i]
        participation.seed = i + 1
        participation.save()
        print(i+1, participation)

    if not tournament.draw_calculated and tournament.deadline <= datetime.date.today():
        if tournament.num_of_registered < tournament.limit:
            i = 1
            while 2 ** i <= tournament.num_of_registered:
                i += 1
            i -= 1
            places = 2 ** i
        else:
            places = tournament.limit
        set_matches = [1]
        i = 1
        while 2 ** i <= tournament.num_of_seeded:
            previous = 2 ** (i - 1)
            stage = 2 ** i - previous
            tmp = []
            for j in range(stage):
                tmp.append(set_matches[j] + int(places / 2 ** (i + 1)))
            random.shuffle(tmp)
            for element in tmp:
                set_matches.append(element)
            i += 1
        tmp = []
        for i in range(1, int(places / 2) + 1):
            if i in set_matches:
                tmp.append(i)
            else:
                tmp.append(i)
                tmp.append(i)
        random.shuffle(tmp)
        for element in tmp:
            set_matches.append(element)

        tournament.draw_calculated = True
        tournament.save()

        print(set_matches)

        already_set = []
        for i in range(len(set_matches)):
            if set_matches[i] not in already_set:
                match = models.Match(tournament=tournament, user1=participations[i].user, number=set_matches[i],
                                     user1_seed=participations[i].seed)
                already_set.append(set_matches[i])
                match.save()
            else:
                match = models.Match.objects.get(tournament=tournament, number=set_matches[i])
                match.user2 = participations[i].user
                match.user2_seed = participations[i].seed
                match.save()


def next_match(n, stage, participants):
    previous = 0
    for i in range(1, stage):
        previous += participants / 2 ** i
    number = int((n - previous + 1) / 2) + previous + participants / 2 ** stage
    return int(number)


def calculate_stage(stage, limit):
    max_stage = math.log(limit, 2)
    if stage == max_stage:
        return 'Final'
    if stage == max_stage - 1:
        return 'Semifinal'
    if stage == max_stage - 2:
        return 'Quarterfinal'
    else:
        if stage == 1:
            return '1st round'
        if stage == 2:
            return '2nd round'
        if stage == 3:
            return '3rd round'
        else:
            return str(stage) + 'th round'
