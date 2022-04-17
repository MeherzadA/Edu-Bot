from pytz import timezone
from datetime import datetime,time

def checkDate(date_text):
  tz = timezone("US/Eastern")
  dateFormat =  "%Y-%m-%d %I:%M %p"
  try:
    user = datetime.strptime(date_text, dateFormat)
    present = datetime.now(tz)
    print(user.time())
    print(user.date())
    print()
    print(present.time())
    print(present.date())
    print()
    if user.date() < present.date():
        message = "Date not valid! Enter a date that is not in the past!"
    elif user.date() > present.date():
      message = 'Success!'
    elif user.date() == present.date():
      if user.time() < present.time():
        message = 'Date not valid! Enter a date that is not in the past!'
      else:
        message  = 'Success!'
  except:
      message  = "Incorrect data format, should be YYYY-MM-DD H:M PM/AM"
  return message