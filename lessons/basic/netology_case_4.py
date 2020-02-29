# Список потенциальных пар
boys = ['Peter', 'Alex', 'John', 'Arthur', 'Richard']
girls = ['Kate', 'Liza', 'Kira', 'Emma', 'Trisha']

# Если мальчиков и девочек поровну: сортировка списков и вывод пар
# Иначе: вывод предупреждения
if len(boys) == len(girls):
  print("Идеальные пары:")
  for item in zip(sorted(boys), sorted(girls)):
    print(item[0], "и", item[1])
else:
  print("Кажется, кому-то не достанется пары!")
