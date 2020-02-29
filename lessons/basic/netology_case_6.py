# пример №1, список правильных ответов на вопрос теста
HGTTG_answers = ["сорок два", "сорокдва", "42"]
answer = input("Ответ на главный вопрос жизни, вселенной, и всего прочего?\n")
if answer in HGTTG_answers: print("Правильно!\n")


# пример №2, список кортежей с габаритами морского контейнера
container_size = [("length", 1219), ("width", 243), ("height", 259)]
print("Габариты контейнера:")
for dim in container_size:
    print(dim[0], dim[1])
print(end="\n")


# пример №3, множества планет, карликовых планет, объектов в Солнечной системе
planets = {
  "Земля", "Марс", "Венера", "Юпитер", "Уран", "Нептун", "Меркурий", "Сатурн",
  }
dwarf_planets = {"Плутон", "Церера", "Эрида", "Макемаке"}

objects_solarsys = {*planets, *dwarf_planets}

if planets.issubset(objects_solarsys):
    print("Планеты входят в множество объектов Солнечной Системы")
if len(planets & dwarf_planets) < 1:
    print("Множества планеты и карликовые планеты не пересекаются\n")

# пример №4, менеджер паролей
passwords = {
    "ВКонтакте" : {
    "site_id" : 0,
    "site_URL" : r"https:\\vk.com",
    "username" : "vkemail@yandex.ru",
    "password" : "vkpassword"},

    "GitHub" : {
    "site_id" : 1,
    "site_URL" : r"https:\\github.com",
    "username" : "Klavionik",
    "password" : "githubpass"},
  }

print("Все пароли пользователя:")
for site in passwords.values():
    print(site["password"])