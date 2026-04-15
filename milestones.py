"""Shows dates for stay milestones."""
from lodging_data_utils import LodgingLog

MILESTONES = [50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000]
TYPES = ['Hotel', 'STR', 'Campsite']

def milestones():
    log = LodgingLog()
    mornings = log.mornings()
    mornings = mornings[mornings['type'].isin(TYPES)]
    mornings['night_number'] = range(1, len(mornings) + 1)
    mornings = mornings[mornings['night_number'].isin(MILESTONES)]
    print(mornings)

if __name__ == "__main__":
    milestones()