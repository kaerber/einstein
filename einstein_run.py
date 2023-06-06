from einstein import *

house = Attr('house', 0, [1, 2, 3, 4, 5])
color = Attr('color', 1, ['red', 'green', 'white', 'yellow', 'blue'])
nation = Attr('nation', 2, ['english', 'spanish', 'ukrainian', 'norwegian', 'japanese'])
animal = Attr('animal', 3, ['dog', 'snail', 'fox', 'horse', 'zebra'])
drink = Attr('drink', 4, ['coffee', 'tea', 'milk', 'orangejuice', 'water'])
smoke = Attr('smoke', 5, ['oldgold', 'kool', 'chesterfield', 'luckystrike', 'parliament'])

solver = Solver([house, color, nation, animal, drink, smoke])
solver.debug = True

solver.add(Exclusive())

solver.add(Same.of(color.red, nation.english))
solver.add(Same.of(nation.spanish, animal.dog))
solver.add(Same.of(color.green, drink.coffee))
solver.add(Same.of(nation.ukrainian, drink.tea))
solver.add(Offset(color.green, color.white, house, 1))
solver.add(Same.of(smoke.oldgold, animal.snail))
solver.add(Same.of(color.yellow, smoke.kool))
solver.add(Same.of(house[3], drink.milk))
solver.add(Same.of(nation.norwegian, house[1]))
solver.add(Distance(smoke.chesterfield, animal.fox, house, 1))
solver.add(Distance(animal.horse, smoke.kool, house, 1))
solver.add(Same.of(smoke.luckystrike, drink.orangejuice))
solver.add(Same.of(nation.japanese, smoke.parliament))
solver.add(Distance(nation.norwegian, color.blue, house, 1))

turn_count = 4
i = 1
while solver.iter() and i <= turn_count:
    print()
    print("turn", i)
    print()
    i += 1
print("turn_count", turn_count)
