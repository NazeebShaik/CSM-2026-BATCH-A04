import secrets
import hashlib

def eeo_key(seed: str):
    population = [secrets.token_bytes(32) for _ in range(30)]
    best = None
    best_score = 0

    for p in population:
        score = int(hashlib.sha256(p).hexdigest(), 16)
        if score > best_score:
            best_score = score
            best = p

    return best
