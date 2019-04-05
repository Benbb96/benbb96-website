from datetime import datetime
import pytz
from tracker.models import Tracker, Track

track = Tracker.objects.get(nom='Pensées lointaines')
file = open('/home/benjamin/Documents/date.txt', 'r')

for line in file:
    line = line.split()
    date = line[2]
    hour = line[5].split(',')[0]
    print(date + ' - ' + hour)
    datetime = datetime.strptime(date + ' ' + hour, '%d/%m/%Y %H:%M:%S')
    datetime = pytz.timezone('Europe/Paris').localize(datetime)
    Track.objects.create(tracker=track, datetime=datetime)