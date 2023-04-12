

class Attr:
    def __init__(self, name, order, values):
        self.name = name
        self.order = order
        self.ordered_values = [AttrValue(self, idx, v) for (idx, v) in zip(range(len(values)), values)]
        self.values = {v.value: v for v in self.ordered_values }

    def value_at(self, index):
        if index >= 0 and index < len(self.ordered_values):
            return self.ordered_values[index]
        return None

    def __getattr__(self, name):
        if name in self.values:
            return self.values[name]
        raise AttributeError(name)

    def __getitem__(self, name):
        return self.values[name]

    def __hash__(self):
        return hash((self.name, self.order))

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)


class AttrValue:
    def __init__(self, attr, index, value):
        self.attr = attr
        self.index = index
        self.value = value

    def offset_value(self, offset):
        return self.attr.value_at(self.index + offset)

    def __hash__(self):
        return hash((self.attr, self.value))

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.attr == other.attr and self.value == other.value

    def __str__(self):
        return str(self.attr) + "[" + self.index + "]" +  ":" + self.value

    def __repr__(self):
        return str(self)


class Relation:
    def __init__(self, atval1, atval2):
        assert(atval1.attr != atval2.attr)
        if atval1.attr.order < atval2.attr.order:
            self.atval1 = atval1
            self.atval2 = atval2
        else:
            self.atval1 = atval2
            self.atval2 = atval1

    def with_attr(self, attr):
        return self.atval1.attr == attr or self.atval2.attr == attr

    def with_atval(self, atval):
        return self.atval1 == atval or self.atval2 == atval

    def atval(self, attr):
        if self.atval1.attr == attr:
            return self.atval1
        if self.atval2.attr == attr:
            return self.atval2
        return None

    def __hash__(self) -> int:
        return hash((self.atval1, self.atval2))

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.atval1 == other.atval1 and self.atval2 == other.atval2


class Solver:
    def __init__(self, attrs):
        self.map = {}
        self.list = []
        self.attrs = attrs

    def add(self, rule):
        self.list.append(rule)
        if rule.relation != None:
            self.map[rule.relation] = rule
        return self
    
    def get(self, relation):
        if relation not in self.map:
            return None
        return self.map[relation]

    def is_same(self, relation):
        return relation in self.map and isinstance(self.map[relation], Same)

    def is_different(self, relation):
        return relation in self.map and isinstance(self.map[relation], Different)
    
    def iter(self):
        # foreach relation
        # relation in map: continue
        # foreach rule in list
        # apply rule to relation
        # if rule returned: add rule to map and to list
        pass

    def __contains__(self, relation):
        return relation in self.map


class Exclusive:
    def __init__(self, matrix):
        self.matrix = matrix

    def evaluate(self, relation):
        a1 = relation.atval1
        a2 = relation.atval2
        if self.check_all_filled(a1, a2) or self.check_all_filled(a2, a1):
            return Same(relation)

    def check_all_filled(self, fixed: AttrValue, sliding: AttrValue):
        for slider in sliding.attr.values.values():
            if slider == sliding:
                continue
            if not self.matrix.is_different(Relation(fixed, slider)):
                return False
        return True

class Offset:
    # дом не такой = дом не существует, или не такой

    # Зелёный дом стоит сразу справа от белого дома.
    # - если дом X-1 - не белый, то дом X - не зеленый| (X, зеленый): if ~(X-1, белый) -> Different
    # - если дом X+1 - не зеленый, то дом X - не белый| (X, белый): if ~(X+1, зеленый) -> Different

    # matrix - матрица связей
    # atval1 - значение атрибута первой сущности в паре (цвет:зеленый для загадки Эйнштейна)
    # atval2 - значение атрибута второй сущности в паре (цвет:белый для загадки Эйнштейна)
    # offset_attr - атрибут, по которому считается смещение (порядок_домов для загадки Эйнштейна)
    # offset - смещение atval1 от atval2 по offset_attr (+1 для загадки Эйнштейна), может быть отрицательным, не может быть 0
    def __init__(self, matrix, atval1, atval2, offset_attr, offset):
        assert(offset != 0)

        self.matrix = matrix
        self.atval1 = atval1
        self.atval2 = atval2
        self.offset_attr = offset_attr
        self.offset = offset

    def evaluate(self, relation):
        if not relation.with_attr(self.offset_attr):
            return None

        cur_offset_val = relation.atval(self.offset_attr)
        
        if relation.with_atval(self.atval1):
            offset_val = cur_offset_val.offset_value(-self.offset)
            if (offset_val == None
                or self.matrix.is_different(Relation(offset_val, self.atval2))):
                return Different(relation)

        if relation.with_atval(self.atval2):
            offset_val = cur_offset_val.offset_value(+self.offset)
            if (offset_val == None
                or self.matrix.is_different(Relation(offset_val, self.atval1))):
                return Different(relation)

class Distance:
    # дом не такой = дом не существует, или не такой

    # Сосед того, кто курит Chesterfield, держит лису.
    # - если в доме Х-1 курят не честерфилд, и в доме Х+1 курят не честерфилд, то в доме Х не лиса
    # - если в доме Х-1 не лиса, и в доме Х+1 не лиса, то в доме Х курят не честерфилд

    # matrix - матрица связей
    # atval1 - значение атрибута первой сущности в паре (курит:chesterfield для загадки Эйнштейна)
    # atval2 - значение атрибута второй сущности в паре (держит:лиса для загадки Эйнштейна)
    # distance_attr - атрибут, по которому считается расстояние (порядок_домов для загадки Эйнштейна)
    # distance - расстояние atval1 от atval2 по distance_attr (1 для загадки Эйнштейна), строго положительное число
    def __init__(self, matrix, atval1, atval2, distance_attr, distance):
        assert(distance > 0)

        self.matrix = matrix
        self.atval1 = atval1
        self.atval2 = atval2
        self.distance_attr = distance_attr
        self.distance = distance

    def evaluate(self, relation):
        if not relation.with_attr(self.distance_attr):
            return None

        cur_distance_val = relation.atval(self.distance_attr)
        left_distance_val = cur_distance_val.offset_value(-self.distance)
        right_distance_val = cur_distance_val.offset_value(+self.distance)
        
        if relation.with_atval(self.atval1):
            if ((left_distance_val == None
                    or self.matrix.is_different(Relation(left_distance_val, self.atval2)))
                and (right_distance_val == None
                    or self.matrix.is_different(Relation(right_distance_val, self.atval2)))):
                return Different(relation)

        if relation.with_atval(self.atval2):
            if ((left_distance_val == None
                    or self.matrix.is_different(Relation(left_distance_val, self.atval1)))
                and (right_distance_val == None
                    or self.matrix.is_different(Relation(right_distance_val, self.atval1)))):
                return Different(relation)

class Same:
    def __init__(self, relation):
        self.relation = relation

    def evaluate(self, relation):
        a1 = self.relation.atval1
        a2 = self.relation.atval2
        # same attributes
        if not (relation.with_attr(a1.attr) and relation.with_attr(a2.attr)):
            return None
        # one attribute value is the same (another is not the same) - considered relation is negative
        if relation.with_atval(a1):
            return Different(relation)
        if relation.with_atval(a2):
            return Different(relation)
        
        return None

    @classmethod
    def of(cls, atval1, atval2):
        return cls(Relation(atval1, atval2))

class Different:
    def __init__(self, relation):
        self.relation = relation

    def evaluate(self, relation):
        return None

    @classmethod
    def of(cls, atval1, atval2):
        return cls(Relation(atval1, atval2))
    

# TESTS
