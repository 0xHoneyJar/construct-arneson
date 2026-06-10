"""sum_positives: return the sum of the positive numbers in xs."""


def sum_positives(xs):
    total = 0
    for x in xs:
        if x >= 0:
            total += x
    return total
