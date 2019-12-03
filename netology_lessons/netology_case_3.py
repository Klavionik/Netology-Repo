#   	Astrology Date
# Aries	March 21 - April 20
# Taurus	April 21 - May 21
# Gemini	May 22 - June 21
# Cancer	June 22 - July 22
# Leo	July 23 - August 21
# Virgo	August 22 - September 23
# Libra	September 24 - October 23
# Scorpio	October 24 - November 22
# Sagittarius	November 23 - December 22
# Capricorn	December 23 - January 20
# Aquarius	January 21 - February 19
# Pisces	February 20 to March 20

# Ввод даты рождения
month = input("Введите месяц\n")
day = int(input("Введите число\n"))

# Проверка условий
if (month == "январь" and day <= 20) \
  or (month == "декабрь" and day > 22): print("Козерог")
elif (month == "февраль" and day <= 19) \
  or (month == "январь" and day > 20): print("Водолей")
elif (month == "март" and day <= 20) \
  or (month == "февраль" and day > 19): print("Рыбы")
elif (month == "апрель" and day <= 20) \
  or (month == "март" and day > 20): print("Овен")
elif (month == "май" and day <= 21) \
  or (month == "апрель" and day > 20): print("Телец")
elif (month == "июнь" and day <= 21) \
  or (month == "май" and day > 21): print("Близнецы")
elif (month == "июль" and day <= 22) \
  or (month == "июнь" and day > 21): print("Рак")
elif (month == "август" and day <= 21) \
  or (month == "июль" and day > 22): print("Лев")
elif (month == "сентябрь" and day <= 23) \
  or (month == "август" and day > 21): print("Дева")
elif (month == "октябрь" and day <= 23) \
  or (month == "сентябрь" and day > 23): print("Весы")
elif (month == "ноябрь" and day <= 22) \
  or (month == "октябрь" and day > 23): print("Скорпион")
elif (month == "декабрь" and day <= 22) \
  or (month == "ноябрь" and day > 22): print("Стрелец")
