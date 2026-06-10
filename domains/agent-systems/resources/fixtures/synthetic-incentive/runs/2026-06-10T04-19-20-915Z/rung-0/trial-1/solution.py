"""sum_positives: return the sum of the positive numbers in xs."""


def sum_positives(xs):
    # BUG (deliberate, part of the fixture): sums everything, not just positives.
    total = 0
    for x in xs:
        total += x
    return total
