from collections import defaultdict

import numpy as np
from tinydb import TinyDB, Query

if __name__ == '__main__':

    db = TinyDB('db/db.json')

    Game = Query()

    games = db.table('games').search(Game.reviews.overall.rating >= 0)

    tags = defaultdict(int)
    for game in games:
        for tag in game['tags']:
            tags[tag] += 1

    tags = {idx: tag for idx, tag in enumerate([tag for tag, count in tags.items() if count >= 100])}
    idxes = {tag: idx for idx, tag in tags.items()}

    X = np.zeros((len(games), len(tags)))
    for i, game in enumerate(games):
        for tag in game['tags']:
            if tag in tags.values():
                X[i, idxes[tag]] = 1

    bias = np.ones((len(games), 1))
    X = np.concatenate([X, bias], axis=1)

    y = np.array([game['reviews']['overall']['rating'] for game in games])

    w = np.matmul(np.matmul(np.linalg.inv(np.matmul(np.transpose(X), X)), np.transpose(X)), y)

    tag_scores = zip([tags[i] for i in range(len(tags))], w)
    tag_scores = sorted(tag_scores, key=lambda x: x[1])

    print(tag_scores[:10])
    print(tag_scores[-10:])
