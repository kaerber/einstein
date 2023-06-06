import unittest

from einstein import *

class AttrTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.attr = Attr('attr', 0, ['v1', 'v2', 'v3', 'v4', 'v5'])

    # value_at
    def test_value_at_in_values_returns_value(self):
        self.assertEqual(self.attr.value_at(2).value, 'v3')

    def test_value_at_zero_returns_value(self):
        self.assertEqual(self.attr.value_at(0).value, 'v1')

    def test_value_at_last_index_returns_value(self):
        self.assertEqual(self.attr.value_at(4).value, 'v5')

    def test_value_at_negative_index_returns_none(self):
        self.assertIsNone(self.attr.value_at(-1))

    def test_value_at_index_over_max_returns_none(self):
        self.assertIsNone(self.attr.value_at(5))

class AttrValueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.attr = Attr('attr', 0, ['v1', 'v2', 'v3', 'v4', 'v5'])

    # offset_value
    def test_offset_value_negative_offset_in_values_returns_value(self):
        self.assertEqual(self.attr.value_at(2).offset_value(-2).value, 'v1')

    def test_offset_value_positive_offset_in_values_returns_value(self):
        self.assertEqual(self.attr.value_at(2).offset_value(2).value, 'v5')

    def test_offset_value_negative_offset_out_of_values_returns_none(self):
        self.assertIsNone(self.attr.value_at(0).offset_value(-1))

    def test_offset_value_positive_offset_out_of_values_returns_none(self):
        self.assertIsNone(self.attr.value_at(4).offset_value(1))

class RelationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.attr_a = Attr('attrA', 0, ['a1', 'a2', 'a3', 'a4', 'a5'])
        cls.attr_b = Attr('attrB', 1, ['b1', 'b2', 'b3', 'b4', 'b5'])
        cls.attr_c = Attr('attrC', 2, ['c1', 'c2', 'c3', 'c4', 'c5'])

        cls.rel = Relation(cls.attr_a.a2, cls.attr_b.b3)

    def test_with_attr_attr_a_in_relation_returns_true(self):
        self.assertTrue(self.rel.with_attr(self.attr_a))

    def test_with_attr_attr_b_in_relation_returns_true(self):
        self.assertTrue(self.rel.with_attr(self.attr_b))

    def test_with_attr_attr_c_not_in_relation_returns_false(self):
        self.assertFalse(self.rel.with_attr(self.attr_c))

    def test_with_atval_a2_same_attr_and_value_returns_true(self):
        self.assertTrue(self.rel.with_atval(self.attr_a.a2))

    def test_with_atval_b3_same_attr_and_value_returns_true(self):
        self.assertTrue(self.rel.with_atval(self.attr_b.b3))
    
    def test_with_atval_a1_same_attr_diff_value_returns_false(self):
        self.assertFalse(self.rel.with_atval(self.attr_a.a1))

    def test_with_atval_b4_same_attr_diff_value_returns_false(self):
        self.assertFalse(self.rel.with_atval(self.attr_b.b4))
    
    def test_with_atval_c1_diff_attr_returns_false(self):
        self.assertFalse(self.rel.with_atval(self.attr_c.c1))
    
class ExclusiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.A = Attr('A', 0, ['A1', 'A2', 'A3'])
        cls.B = Attr('B', 1, ['B1', 'B2', 'B3'])

    def setUp(self):
        self.solver = Solver([self.A, self.B])

    def test_exclusive_returns_same_when_other_options_are_excluded(self):
        solver = self.solver.add(Different.of(self.A.A2, self.B.B1)) \
            .add(Different.of(self.A.A2, self.B.B3))
        rule = Exclusive()
        rule.solver = solver
        result = rule.evaluate(Relation(self.A.A2, self.B.B2))
        self.assertIsInstance(result, Same)
        self.assertEqual(result.relation, Relation(self.A.A2, self.B.B2))

    def test_exclusive_returns_none_when_not_all_other_options_are_excluded(self):
        solver = self.solver.add(Different.of(self.A.A2, self.B.B1))
        rule = Exclusive()
        rule.solver = solver
        result = rule.evaluate(Relation(self.A.A2, self.B.B2))
        self.assertIsNone(result)

class OffsetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.color = Attr('color', 0, ['red', 'green', 'white', 'yellow', 'blue'])
        cls.house = Attr('house', 1, [1, 2, 3, 4, 5])
        cls.smoke = Attr('smoke', 2, ['oldgold', 'kool', 'chesterfield', 'luckystrike', 'parliament'])

    def setUp(self):
        self.solver = Solver([self.color, self.house, self.smoke])

     # дом не такой = дом не существует, или не такой

    # Зелёный дом стоит сразу справа от белого дома.
    # - если дом X-1 - не белый, то дом X - не зеленый| (X, зеленый): if ~(X-1, белый) -> Different
    def test_left_not_white_returns_this_not_green(self):
        solver = self.solver.add(Different.of(self.house[2], self.color.white))
        rule = Offset(self.color.green, self.color.white, self.house, 1)
        rule.solver = solver
        result = rule.evaluate(Relation(self.house[3], self.color.green))
        self.assertIsInstance(result, Different)

    # - если дом X-1 - белый, то дом X - зеленый| (X, зеленый): if (X-1, белый) -> Same
    def test_left_white_returns_this_green(self):
        solver = self.solver.add(Same.of(self.house[2], self.color.white))
        rule = Offset(self.color.green, self.color.white, self.house, 1)
        rule.solver = solver
        result = rule.evaluate(Relation(self.house[3], self.color.green))
        self.assertIsInstance(result, Same)

    # - если дом X+1 - не зеленый, то дом X - не белый
    def test_right_not_green_returns_this_not_white(self):
        solver = self.solver.add(Different.of(self.house[4], self.color.green))
        rule = Offset(self.color.green, self.color.white, self.house, 1)
        rule.solver = solver
        result = rule.evaluate(Relation(self.house[3], self.color.white))
        self.assertIsInstance(result, Different)

    # - если дом X+1 - зеленый, то дом X - белый
    def test_right_green_returns_this_white(self):
        solver = self.solver.add(Same.of(self.house[4], self.color.green))
        rule = Offset(self.color.green, self.color.white, self.house, 1)
        rule.solver = solver
        result = rule.evaluate(Relation(self.house[3], self.color.white))
        self.assertIsInstance(result, Same)

    def test_not_offset_attr_returns_none(self):
        solver = self.solver.add(Different.of(self.house[4], self.color.green))
        rule = Offset(self.color.green, self.color.white, self.house, 1)
        rule.solver = solver
        result = rule.evaluate(Relation(self.smoke.kool, self.color.white))
        self.assertIsNone(result)

    def test_not_atval_returns_none(self):
        solver = self.solver.add(Different.of(self.house[4], self.color.green))
        rule = Offset(self.color.green, self.color.white, self.house, 1)
        rule.solver = solver
        result = rule.evaluate(Relation(self.house[3], self.color.yellow))
        self.assertIsNone(result)

    def test_no_left_returns_this_not_green(self):
        rule = Offset(self.color.green, self.color.white, self.house, 1)
        rule.solver = self.solver
        result = rule.evaluate(Relation(self.house[1], self.color.green))
        self.assertIsInstance(result, Different)

    def test_no_right_returns_this_not_white(self):
        rule = Offset(self.color.green, self.color.white, self.house, 1)
        rule.solver = self.solver
        result = rule.evaluate(Relation(self.house[5], self.color.white))
        self.assertIsInstance(result, Different)

    def test_atval1_left_can_be_white_returns_none(self):
        rule = Offset(self.color.green, self.color.white, self.house, 1)
        rule.solver = self.solver
        result = rule.evaluate(Relation(self.house[3], self.color.green))
        self.assertIsNone(result)

    def test_atval2_right_can_be_green_returns_none(self):
        rule = Offset(self.color.green, self.color.white, self.house, 1)
        rule.solver = self.solver
        result = rule.evaluate(Relation(self.house[3], self.color.white))
        self.assertIsNone(result)

class DistanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.animal = Attr('animal', 0, ['dog', 'snail', 'fox', 'horse', 'zebra'])
        cls.house = Attr('house', 1, [1, 2, 3, 4, 5])
        cls.smoke = Attr('smoke', 2, ['oldgold', 'kool', 'chesterfield', 'luckystrike', 'parliament'])
        cls.drink = Attr('drink', 3, ['coffee', 'tea', 'milk', 'orangejuice', 'water'])

    def setUp(self):
        self.solver = Solver([self.animal, self.house, self.smoke, self.drink])

    # дом не такой = дом не существует, или не такой

    # Сосед того, кто курит Chesterfield, держит лису.
    # - если в доме Х-1 курят не честерфилд, и в доме Х+1 курят не честерфилд, то в доме Х не лиса
    # - если в доме Х-1 не лиса, и в доме Х+1 не лиса, то в доме Х курят не честерфилд

    def test_left_right_not_chesterfield_returns_this_not_fox(self):
        solver = self.solver.add(Different.of(self.house[2], self.smoke.chesterfield)) \
            .add(Different.of(self.house[4], self.smoke.chesterfield))
        rule = Distance(self.smoke.chesterfield, self.animal.fox, self.house, 1)
        rule.solver = solver
        result = rule.evaluate(Relation(self.house[3], self.animal.fox))
        self.assertIsInstance(result, Different)

    def test_left_not_chesterfield_right_not_exist_returns_this_not_fox(self):
        solver = self.solver.add(Different.of(self.house[4], self.smoke.chesterfield))
        rule = Distance(self.smoke.chesterfield, self.animal.fox, self.house, 1)
        rule.solver = solver
        result = rule.evaluate(Relation(self.house[5], self.animal.fox))
        self.assertIsInstance(result, Different)

    def test_left_not_exist_right_not_chesterfield_returns_this_not_fox(self):
        solver = self.solver.add(Different.of(self.house[2], self.smoke.chesterfield))
        rule = Distance(self.smoke.chesterfield, self.animal.fox, self.house, 1)
        rule.solver = solver
        result = rule.evaluate(Relation(self.house[1], self.animal.fox))
        self.assertIsInstance(result, Different)

    def test_left_right_not_fox_returns_this_not_chesterfield(self):
        solver = self.solver.add(Different.of(self.house[2], self.animal.fox)) \
            .add(Different.of(self.house[4], self.animal.fox))
        rule = Distance(self.smoke.chesterfield, self.animal.fox, self.house, 1)
        rule.solver = solver
        result = rule.evaluate(Relation(self.house[3], self.smoke.chesterfield))
        self.assertIsInstance(result, Different)

    def test_left_not_fox_right_not_exist_returns_this_not_chesterfield(self):
        solver = self.solver.add(Different.of(self.house[4], self.animal.fox))
        rule = Distance(self.smoke.chesterfield, self.animal.fox, self.house, 1)
        rule.solver = solver
        result = rule.evaluate(Relation(self.house[5], self.smoke.chesterfield))
        self.assertIsInstance(result, Different)

    def test_left_not_exist_right_not_fox_returns_this_not_chesterfield(self):
        solver = self.solver.add(Different.of(self.house[2], self.animal.fox))
        rule = Distance(self.smoke.chesterfield, self.animal.fox, self.house, 1)
        rule.solver = solver
        result = rule.evaluate(Relation(self.house[1], self.smoke.chesterfield))
        self.assertIsInstance(result, Different)

    def test_not_with_distance_attr_returns_none(self):
        solver = self.solver.add(Different.of(self.house[2], self.smoke.chesterfield)) \
            .add(Different.of(self.house[4], self.smoke.chesterfield))
        rule = Distance(self.smoke.chesterfield, self.animal.fox, self.house, 1)
        rule.solver = solver
        result = rule.evaluate(Relation(self.drink.tea, self.animal.fox))
        self.assertIsNone(result)

    def test_not_with_chesterfield_returns_none(self):
        solver = self.solver.add(Different.of(self.house[2], self.animal.fox)) \
            .add(Different.of(self.house[4], self.animal.fox))
        rule = Distance(self.smoke.chesterfield, self.animal.fox, self.house, 1)
        rule.solver = solver
        result = rule.evaluate(Relation(self.house[3], self.smoke.kool))
        self.assertIsNone(result)

    def test_chesterfield_left_not_different_returns_none(self):
        solver = self.solver.add(Different.of(self.house[4], self.animal.fox))
        rule = Distance(self.smoke.chesterfield, self.animal.fox, self.house, 1)
        rule.solver = solver
        result = rule.evaluate(Relation(self.house[3], self.smoke.chesterfield))
        self.assertIsNone(result)

    def test_chesterfield_right_not_different_returns_none(self):
        solver = self.solver.add(Different.of(self.house[2], self.animal.fox))
        rule = Distance(self.smoke.chesterfield, self.animal.fox, self.house, 1)
        rule.solver = solver
        result = rule.evaluate(Relation(self.house[3], self.smoke.chesterfield))
        self.assertIsNone(result)

    def test_not_with_fox_returns_none(self):
        solver = self.solver.add(Different.of(self.house[2], self.smoke.chesterfield)) \
            .add(Different.of(self.house[4], self.smoke.chesterfield))
        rule = Distance(self.smoke.chesterfield, self.animal.fox, self.house, 1)
        rule.solver = solver
        result = rule.evaluate(Relation(self.house[3], self.animal.zebra))
        self.assertIsNone(result)

    def test_fox_left_not_different_returns_none(self):
        solver = self.solver.add(Different.of(self.house[4], self.smoke.chesterfield))
        rule = Distance(self.smoke.chesterfield, self.animal.fox, self.house, 1)
        rule.solver = solver
        result = rule.evaluate(Relation(self.house[3], self.animal.fox))
        self.assertIsNone(result)

    def test_fox_right_not_different_returns_none(self):
        solver = self.solver.add(Different.of(self.house[2], self.smoke.chesterfield))
        rule = Distance(self.smoke.chesterfield, self.animal.fox, self.house, 1)
        rule.solver = solver
        result = rule.evaluate(Relation(self.house[3], self.animal.fox))
        self.assertIsNone(result)

    def test_left_chesterfield_next_not_fox_returns_this_fox(self):
        solver = self.solver.add(Same.of(self.house[2], self.smoke.chesterfield)) \
            .add(Different.of(self.house[1], self.animal.fox))
        rule = Distance(self.smoke.chesterfield, self.animal.fox, self.house, 1)
        rule.solver = solver
        result = rule.evaluate(Relation(self.house[3], self.animal.fox))
        self.assertIsInstance(result, Same)

    def test_left_chesterfield_next_not_exist_returns_this_fox(self):
        solver = self.solver.add(Same.of(self.house[1], self.smoke.chesterfield))
        rule = Distance(self.smoke.chesterfield, self.animal.fox, self.house, 1)
        rule.solver = solver
        result = rule.evaluate(Relation(self.house[2], self.animal.fox))
        self.assertIsInstance(result, Same)

    def test_right_chesterfield_next_not_fox_returns_this_fox(self):
        solver = self.solver.add(Same.of(self.house[4], self.smoke.chesterfield)) \
            .add(Different.of(self.house[5], self.animal.fox))
        rule = Distance(self.smoke.chesterfield, self.animal.fox, self.house, 1)
        rule.solver = solver
        result = rule.evaluate(Relation(self.house[3], self.animal.fox))
        self.assertIsInstance(result, Same)

    def test_right_chesterfield_next_not_exist_returns_this_fox(self):
        solver = self.solver.add(Same.of(self.house[5], self.smoke.chesterfield))
        rule = Distance(self.smoke.chesterfield, self.animal.fox, self.house, 1)
        rule.solver = solver
        result = rule.evaluate(Relation(self.house[4], self.animal.fox))
        self.assertIsInstance(result, Same)

 

class SameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.A = Attr('A', 0, [1, 2, 3])
        cls.B = Attr('B', 1, [1, 2, 3])

    def test_returns_different_when_same_row(self):
        rule_under_test = Same.of(self.A[2], self.B[2])
        result = rule_under_test.evaluate(Relation(self.A[2], self.B[1]))
        self.assertIsInstance(result, Different)
   
    def test_returns_different_when_same_column(self):
        rule_under_test = Same.of(self.A[2], self.B[2])
        result = rule_under_test.evaluate(Relation(self.A[3], self.B[2]))
        self.assertIsInstance(result, Different)
   
    def test_returns_none_when_not_same_row_or_column(self):
        rule_under_test = Same.of(self.A[2], self.B[2])
        result = rule_under_test.evaluate(Relation(self.A[1], self.B[3]))
        self.assertIsNone(result)

    def test_different_for_one_attr_transitioned_to_the_other(self):
        color = Attr('color', 0, ['red', 'green', 'blue'])
        nation = Attr('nation', 1, ['spanish', 'english', 'german'])
        animal = Attr('animal', 2, ['dog', 'cat', 'snake'])
        solver = Solver([color, nation, animal])
        solver.add(Different(Relation(color.red, nation.spanish)))
        rule = Same(Relation(nation.spanish, animal.dog))
        solver.add(rule)

        result = rule.evaluate(Relation(animal.dog, color.red))
        self.assertIsInstance(result, Different)

    def test_same_for_one_attr_transitioned_to_the_other(self):
        color = Attr('color', 0, ['red', 'green', 'blue'])
        nation = Attr('nation', 1, ['spanish', 'english', 'german'])
        animal = Attr('animal', 2, ['dog', 'cat', 'snake'])
        solver = Solver([color, nation, animal])
        solver.add(Same(Relation(color.red, nation.spanish)))
        rule = Same(Relation(nation.spanish, animal.dog))
        solver.add(rule)

        result = rule.evaluate(Relation(animal.dog, color.red))
        self.assertIsInstance(result, Same)


class SolverTests(unittest.TestCase):
    def test_iter_same_causes_different_with_exclusive(self):
        house = Attr('house', 0, [1, 2, 3])
        color = Attr('color', 1, ['red', 'green', 'blue'])
        solver = Solver([house, color])
        solver.add(Exclusive())
        solver.add(Same(Relation(house[2], color.green)))
        
        solver.iter()

        self.assertTrue(solver.is_different(Relation(house[1], color.green)))
        self.assertTrue(solver.is_different(Relation(house[3], color.green)))
        self.assertTrue(solver.is_different(Relation(house[2], color.red)))
        self.assertTrue(solver.is_different(Relation(house[2], color.blue)))

    def test_iter_all_different_causes_same_with_exclusive(self):
        house = Attr('house', 0, [1, 2, 3])
        color = Attr('color', 1, ['red', 'green', 'blue'])
        solver = Solver([house, color])
        solver.add(Exclusive())
        solver.add(Different(Relation(house[1], color.green)))
        solver.add(Different(Relation(house[3], color.green)))

        solver.iter()

        self.assertTrue(solver.is_same(Relation(house[2], color.green)))

    def test_iter_two_sides_different_causes_different_with_distance(self):
        house = Attr('house', 0, [1, 2, 3])
        color = Attr('color', 1, ['red', 'green', 'blue'])
        solver = Solver([house, color])
        solver.add(Distance(color.green, color.red, house, 1))
        solver.add(Different(Relation(color.red, house[1])))
        solver.add(Different(Relation(color.red, house[3])))

        solver.iter()

        self.assertTrue(solver.is_different(Relation(color.green, house[2])))

    def test_iter_side_different_causes_different_with_offset(self):
        house = Attr('house', 0, [1, 2, 3])
        color = Attr('color', 1, ['red', 'green', 'blue'])
        solver = Solver([house, color])
        solver.add(Offset(color.green, color.red, house, 1))
        solver.add(Different(Relation(color.red, house[1])))

        solver.iter()

        self.assertTrue(solver.is_different(Relation(color.green, house[2])))

class SolverAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.house = Attr('house', 0, [1, 2, 3, 4, 5])
        cls.color = Attr('color', 1, ['red', 'green', 'white', 'yellow', 'blue'])
        cls.nation = Attr('nation', 2, ['english', 'spanish', 'ukrainian', 'norwegian', 'japanese'])
        cls.animal = Attr('animal', 3, ['dog', 'snail', 'fox', 'horse', 'zebra'])
        cls.drink = Attr('drink', 4, ['coffee', 'tea', 'milk', 'orangejuice', 'water'])
        cls.smoke = Attr('smoke', 5, ['oldgold', 'kool', 'chesterfield', 'luckystrike', 'parliament'])

        cls.solver = Solver([cls.house, cls.color, cls.nation, cls.animal, cls.drink, cls.smoke])
        cls.solver.add(Exclusive())
        cls.solver.add(Same.of(cls.color.red, cls.nation.english))
        cls.solver.add(Same.of(cls.nation.spanish, cls.animal.dog))
        cls.solver.add(Same.of(cls.color.green, cls.drink.coffee))
        cls.solver.add(Same.of(cls.nation.ukrainian, cls.drink.tea))
        cls.solver.add(Offset(cls.color.green, cls.color.white, cls.house, 1))
        cls.solver.add(Same.of(cls.smoke.oldgold, cls.animal.snail))
        cls.solver.add(Same.of(cls.color.yellow, cls.smoke.kool))
        cls.solver.add(Same.of(cls.house[3], cls.drink.milk))
        cls.solver.add(Same.of(cls.nation.norwegian, cls.house[1]))
        cls.solver.add(Distance(cls.smoke.chesterfield, cls.animal.fox, cls.house, 1))
        cls.solver.add(Distance(cls.animal.horse, cls.smoke.kool, cls.house, 1))
        cls.solver.add(Same.of(cls.smoke.luckystrike, cls.drink.orangejuice))
        cls.solver.add(Same.of(cls.nation.japanese, cls.smoke.parliament))
        cls.solver.add(Distance(cls.nation.norwegian, cls.color.blue, cls.house, 1))

    def test_added_relation_exists(self):
        self.assertIsInstance(self.solver.get(Relation(self.nation.english, self.color.red)), Same)

    def test_iteration_finishes(self):
        count = 100
        while count > 0 and self.solver.iter():
            count -= 1
        self.assertTrue(count > 0)

    def test_solved_correctly(self):
        self.longMessage = True
        self.test_iteration_finishes()

        print(self.solver.get(Relation(self.house[1], self.color.yellow)))
        self.assertIsInstance(self.solver.get(Relation(self.house[1], self.color.yellow)), Same)
        self.assertTrue(self.solver.is_same(Relation(self.house[1], self.nation.norwegian)))
        self.assertTrue(self.solver.is_same(Relation(self.house[1], self.smoke.kool)))
        #
        self.assertTrue(self.solver.is_same(Relation(self.house[1], self.drink.water)))

        self.assertTrue(self.solver.is_same(Relation(self.house[2], self.color.blue)))
        #
        #
        self.assertTrue(self.solver.is_same(Relation(self.house[2], self.animal.horse)))
        #

        #
        #
        #
        #
        self.assertTrue(self.solver.is_same(Relation(self.house[3], self.drink.milk)))

if __name__ == '__main__':
    unittest.main()

