from datetime import date, datetime
class Operations:
    def calculateAge(dob):
        x = datetime.strptime(dob, '%Y-%m-%d')
        today = date.today()
        one_or_zero = ((today.month, today.day) < (x.month, x.day))
        year_difference = today.year - x.year
        y = 1 if one_or_zero else 0
        curr_age = year_difference - y
        return curr_age