import re

import pytest

from corelib.config import ValRange, ValArray, ValSetEval, ValSetJoin, \
    ValSetProd, ValSetZip, make_unique, ValArraySchema, guess_dtype


#
# TESTING ValRange
# ----------------
def test_ValRange__values():
    """
    Test that ValRange.values() returns a list with values.
    """
    assert ValRange(left=10, right=47, step=10).values == (10, 20, 30, 40, 47)
    assert ValRange(left=42, right=42, step=1).values == (42,)
    assert ValRange(5, 8).values == (5, 6, 7, 8)


def test_ValRange__raise_error_when_left_is_greater_than_right():
    """
    Test that ValRange constructor raises ValueError when left > right.
    """
    with pytest.raises(ValueError):
        ValRange(left=50, right=40, step=-5)


def test_ValRange__raise_error_for_zero_step():
    """
    Test that ValRange constructor raises ValueError when step = 0
    """
    with pytest.raises(ValueError):
        ValRange(10, 20, 0)


def test_ValRange__raise_error_for_negative_step():
    """
    Test that ValRange constructor raises ValueError when step < 0
    """
    with pytest.raises(ValueError):
        ValRange(10, 20, -1)


def test_ValRange__iter():
    """
    Test that ValRange implements __iter__ magic method.
    """
    assert tuple(ValRange(left=23, right=49, step=8)) == (23, 31, 39, 47, 49)


def test_ValRange__len():
    """
    Test that ValRange implements __len__ magic.
    """
    assert len(ValRange(34, 34)) == 1
    assert len(ValRange(left=23, right=49, step=8)) == 5


# noinspection PyPropertyAccess
def test_ValRange__left_right_step_props():
    """
    Test that ValRange provides left, right and step read-only properties.
    """
    range_ = ValRange(10, 20, 3)
    assert range_.left == 10
    assert range_.right == 20
    assert range_.step == 3
    with pytest.raises(AttributeError):
        range_.left = 13
    with pytest.raises(AttributeError):
        range_.right = 23
    with pytest.raises(AttributeError):
        range_.step = 8


def test_ValRange__repr():
    """
    Test ValRange implements repr.
    """
    range_ = ValRange(left=23, right=49, step=8)
    assert str(range_) == "ValRange{left=23, right=49, step=8}"


#
# TESTING ValArray
# ----------------
def test_ValArray__accepts_any_iterable():
    """Test that ValArray can be constructed from list, tuple or iterator."""
    assert ValArray().values == ()
    assert ValArray([]).values == ()
    assert ValArray([10, 20, 30]).values == (10, 20, 30)
    assert ValArray((10, 20, 30)).values == (10, 20, 30)
    assert ValArray(x**2 for x in range(5)).values == (0, 1, 4, 9, 16)


def test_ValArray__iter():
    """Test that ValArray implements __iter__ magic method."""
    assert tuple(ValArray([1, 2, 9])) == (1, 2, 9)


def test_ValArray__len():
    """Test that ValArray implements __len__ magic method."""
    assert len(ValArray()) == 0
    assert len(ValArray([1, 2, 10])) == 3


def test_ValArray__dtype():
    """Test that ValArray provides dtype property."""
    assert ValArray(dtype='integer').dtype == 'integer'
    assert ValArray(dtype='matrix').dtype == 'matrix'
    assert ValArray([1, 2]).dtype == 'integer'
    assert ValArray().dtype == 'float'
    assert ValArray(['1', '2']).dtype == 'string'

    with pytest.raises(TypeError):
        ValArray([1, '2'])


def test_ValArray__repr():
    """Test that ValArray implements __repr__ magic method."""
    array_1 = ValArray([1, 2, 3])
    assert str(array_1) == 'ValArray{dtype=integer, values=[1, 2, 3]}'

    array_2 = ValArray()
    assert str(array_2) == 'ValArray{dtype=float, values=[]}'

    array_3 = ValArray(["6.25us", "12.5us"])
    assert str(array_3) == 'ValArray{dtype=string, values=[6.25us, 12.5us]}'


#
# TESTING ValSetEval
# ------------------
def test_ValSetEval__all():
    """Test that ValSetEval builds a product of all values."""
    # By default, ValSetEval is empty:
    assert ValSetEval().all() == ()
    assert ValSetEval({}).all() == ({},)

    # Check that ValSetEval accepts ValRange/ValArray key values:
    ve1 = ValSetEval({
        "speed": ValRange(30, 50, 10),
        "m": ValArray([4, 8]),
        "tari": ValArray(["6.25us"])
    })
    assert ve1.all() == (
        {"speed": 30, "m": 4, "tari": "6.25us"},
        {"speed": 30, "m": 8, "tari": "6.25us"},
        {"speed": 40, "m": 4, "tari": "6.25us"},
        {"speed": 40, "m": 8, "tari": "6.25us"},
        {"speed": 50, "m": 4, "tari": "6.25us"},
        {"speed": 50, "m": 8, "tari": "6.25us"},
    )

    # Check that ValSetEval accepts any iterables as values in dict:
    ve2 = ValSetEval({"a": (10, 20), "b": (x ** 2 for x in range(1, 4))})
    assert ve2.all() == (
        {"a": 10, "b": 1},
        {"a": 10, "b": 4},
        {"a": 10, "b": 9},
        {"a": 20, "b": 1},
        {"a": 20, "b": 4},
        {"a": 20, "b": 9},
    )


def test_ValSetEval__empty_when_some_key_empty():
    """Test that ValSetEval produces an empty set if some value is empty."""
    assert ValSetEval({"a": (10, 20), "b": ()}).all() == ()


def test_ValSetEval__raise_error_when_key_value_not_iterable():
    """
    Test that ValSetEval constructor raises TypeError when dict contains
    non-iterable values.
    """
    with pytest.raises(TypeError):
        ValSetEval({"a": (10, 20), "b": 5})


# noinspection PyArgumentList,PyTypeChecker
def test_ValSetEval__raise_error_for_non_dict():
    """Test that passing a non-dictionary argument raises error."""
    with pytest.raises(TypeError):
        ValSetEval(a=(10, 20))
    with pytest.raises(TypeError):
        ValSetEval([{"a": (10, 20)}])


def test_ValSetEval__iter():
    """Test that ValSetEval can be used as an iterator."""
    ve = ValSetEval({"a": (34, 42)})
    assert tuple(ve) == ({"a": 34}, {"a": 42})


def test_ValSetEval__len():
    """Test ValSetEval implements __len__ magic."""
    assert len(ValSetEval()) == 0
    assert len(ValSetEval({})) == 1
    assert len(ValSetEval({"a": (34, 42), "b": (1, 2, 3), "c": (8, 9)})) == 12


def test_ValSetEval__data():
    """
    Test ValSetEval returns data dictionary that was used in creation.
    """
    A_VAL = ValRange(10, 20)
    B_VAL = ValArray(("hello", "bye"))
    D = {"a": A_VAL, "b": B_VAL}
    val_set = ValSetEval(D)
    assert val_set.data == D


def test_ValSetEval__repr_magic():
    """
    Test that ValSetEval can be casted to string.
    """
    val_set = ValSetEval({
        "speed": ValRange(10, 20, 3),
        "m": ValArray([1, 2, 4, 8]),
        "x": [10, 20, 30]
    })
    assert str(val_set) == '''
ValSetEval:
    speed: ValRange{left=10, right=20, step=3}
    m    : ValArray{dtype=integer, values=[1, 2, 4, 8]}
    x    : [10, 20, 30]'''.strip()


#
# TESTING ValSetJoin
# ------------------
def test_ValSetJoin__joins_distinct_values_sets():
    """
    Test that ValSetJoin properly joins distinct sets of values.
    """
    D1 = {"a": 17, "b": 34}
    D2 = {"a": 19, "b": 42}
    D3 = {"a": 17, "b": 13}
    D4 = {"a": 48, "b": 99, "c": "hello"}
    D5 = {"b": 123, "x": (1, 2, 3)}
    D6 = {}

    # By default, the join is empty:
    assert ValSetJoin().all() == ()

    # Empty values are kept:
    assert ValSetJoin([{}]).all() == ({},)

    # A simple case with only one argument:
    assert ValSetJoin([D1]).all() == (D1,)

    # Secondly, several non-intersecting arguments:
    val_set = ValSetJoin([D1, D2], [], (D3, D4), [D5], (D6,))
    assert val_set.all() == (D1, D2, D3, D4, D5, D6)


def test_ValSetJoin__removes_duplicates_when_set_unique():
    """
    Test that ValSetJoin removes duplicate dictionaries.
    """
    D1 = {"a": 17, "b": 34}
    D2 = {"a": 19, "b": 42}
    D3 = {"b": 123, "x": (1, 2, 3)}
    D4 = {}
    ARGS = ([D1, D2, D2], [D1, D4, D3], [D3, D2, D1], [D4])

    assert ValSetJoin(*ARGS).all() == (D1, D2, D2, D1, D4, D3, D3, D2, D1, D4)
    assert ValSetJoin(*ARGS, unique=True).all() == (D1, D2, D4, D3)


# noinspection PyTypeChecker
def test_ValSetJoin__raise_error_on_non_iterable_argument():
    """
    Test that ValSetJoin accepts only iterable arguments.
    """
    with pytest.raises(TypeError):
        ValSetJoin(5, 2.3)


# noinspection PyTypeChecker
def test_ValSetJoin__raise_error_when_iter_value_not_dict():
    """
    Test that ValSetJoin accepts only iterables, whose values are dicts.
    """
    with pytest.raises(TypeError):
        ValSetJoin((1, 2, 3))
    with pytest.raises(TypeError):
        ValSetJoin({"a": 1, "b": 2})
    with pytest.raises(TypeError):
        ValSetJoin("wrong")


def test_ValSetJoin__iter():
    """
    Test that ValSetJoin implements __iter__ magic method.
    """
    D1 = {"a": 17, "b": 34}
    D2 = {"a": 19, "b": 42}
    D3 = {"a": 17, "b": 13}
    val_set = ValSetJoin([D1, D2], [D3])
    assert list(val_set) == [D1, D2, D3]


def test_ValSetJoin__len():
    """
    Validate that ValSetJoin returns length - number of values in the set.
    """
    D1 = {"a": 17, "b": 34}
    D2 = {"a": 19, "b": 42}
    D3 = {"a": 17, "b": 13}
    assert len(ValSetJoin([D1])) == 1
    assert len(ValSetJoin([D1, D2])) == 2
    assert len(ValSetJoin([D1, D2], [D3])) == 3


# noinspection PyPropertyAccess
def test_ValSetJoin__args():
    """
    Validate that ValSetJoin provides args immutable property
    """
    D1 = {"a": 1}
    D2 = {"b": 20}
    D3 = {"a": 1, "b": 3}
    set1 = [D1, D2]
    set2 = (D3,)
    val_set = ValSetJoin(set1, set2)
    assert val_set.args == (set1, set2)

    with pytest.raises(AttributeError):
        val_set.args = (set2, set1)


def test_ValSetJoin__repr():
    """
    Validate that ValSetJoin implements __repr__
    """
    D1 = {"a": 17}
    D2 = {"b": 42}
    D3 = {"a": 9, "b": 13}
    val_set_eval = ValSetEval({'x': [10, 20, 30], 'y': [34, 42]})

    string = '''
ValSetJoin:
    [{'a': 17}, {'b': 42}, {'a': 9, 'b': 13}]
    ValSetEval:
        x: [10, 20, 30]
        y: [34, 42]
'''.strip()

    assert str(ValSetJoin([D1, D2, D3], val_set_eval)) == string

    assert str(ValSetJoin()) == 'ValSetJoin{empty=True}'
    assert str(ValSetJoin(unique=True)) == 'ValSetJoin{unique=True, empty=True}'


#
# TESTING ValSetProd
# ------------------
@pytest.fixture
def val_set_prod_data():
    D1 = {"a": 1, "b": "hello"}
    D2 = {"a": 2, "b": "bye"}
    D3 = {"c": 34}
    D4 = {"c": 42}
    D5 = {"d": "in-each"}
    SET_1 = [D1, D2]
    SET_2 = (D3, D4)
    SET_3 = [D5]
    ARGS = (SET_1, SET_2, SET_3)
    ALL = (
        {"a": 1, "b": "hello", "c": 34, "d": "in-each"},
        {"a": 1, "b": "hello", "c": 42, "d": "in-each"},
        {"a": 2, "b": "bye", "c": 34, "d": "in-each"},
        {"a": 2, "b": "bye", "c": 42, "d": "in-each"}
    )
    prod = ValSetProd(*ARGS)
    return prod, ARGS, ALL


def test_ValSetProd__all(val_set_prod_data):
    """
    Test that ValSetProd accepts iterables of dicts with non-intersecting
    keys sets and builds a product of all key-values pairs.
    """
    # Create empty ValSetProd
    prod_0 = ValSetProd()
    assert prod_0.all() == (), "prod of empty set should be empty"

    assert ValSetProd([{}]).all() == ({},)
    assert ValSetProd([{}, {}], [{}]).all() == ({}, {})

    prod_1, ARGS, ALL = val_set_prod_data
    assert prod_1.all() == ALL


def test_ValSetProd__raise_error_for_intersecting_keys():
    """
    Test that ValSetProd raises error when attempting to create from
    dictionaries with intersecting keys sets.
    """
    D1 = {"a": 1, "b": "hello"}
    D2 = {"a": 10, "c": 42}
    with pytest.raises(KeyError):
        ValSetProd([D1], [D2])


def test_ValSetProd__accepts_sets_with_different_keys():
    """
    Test that it is ok to pass sets with non-matching keys to ValSetProd.
    """
    D1 = {"a": 1, "b": "hello"}
    D2 = {"a": 2, "c": 100}
    D3 = {"x": 34}
    D4 = {"x": 42}
    ALL = (
        {"a": 1, "b": "hello", "x": 34},
        {"a": 1, "b": "hello", "x": 42},
        {"a": 2, "c": 100, "x": 34},
        {"a": 2, "c": 100, "x": 42},
    )
    # Here D1 and D2 has different keys sets
    assert ValSetProd([D1, D2], [D3, D4]).all() == ALL


# noinspection PyTypeChecker
def test_ValSetProd__accepts_only_iterables_with_dicts():
    """
    Test that ValSetProd accepts iterable arguments with dicts inside.
    """
    with pytest.raises(TypeError):
        ValSetProd(13)
    with pytest.raises(TypeError):
        ValSetProd({"a": 1})


def test_ValSetProd__with_unique_arg_removes_duplicate():
    """
    Test that if unique=True is passed to ValSetProd constructor, then
    duplicated values are removed.
    """
    D1 = {"a": 1}
    D2 = {"x": 34}
    D3 = {"x": 42}
    assert ValSetProd([D1, D1], [D2, D3]).all() == (
        {"a": 1, "x": 34},
        {"a": 1, "x": 42},
        {"a": 1, "x": 34},
        {"a": 1, "x": 42},
    )

    assert ValSetProd([D1, D1], [D2, D3], unique=True).all() == (
        {"a": 1, "x": 34},
        {"a": 1, "x": 42}
    )


def test_ValSetProd__iter(val_set_prod_data):
    """Test that ValSetProd implements __iter__magic method."""
    prod, _, ALL = val_set_prod_data
    assert tuple(ValSetProd()) == ()
    assert tuple(prod) == ALL


def test_ValSetProd__len(val_set_prod_data):
    """Test that ValSetProd implements __len__ magic method."""
    assert len(ValSetProd()) == 0
    prod = val_set_prod_data[0]
    assert len(prod) == 4


def test_ValSetProd__args(val_set_prod_data):
    """Test that ValSetProd provides args property with a tuple of args."""
    prod, ARGS, _ = val_set_prod_data
    assert prod.args == ARGS


def test_ValSetProd__repr(val_set_prod_data):
    """Test that ValSetProd implements __repr__ magic method."""
    prod, _, _ = val_set_prod_data
    string = '''
ValSetProd:
    [{'a': 1, 'b': 'hello'}, {'a': 2, 'b': 'bye'}]
    ({'c': 34}, {'c': 42})
    [{'d': 'in-each'}]
    '''.strip()
    assert str(prod) == string
    assert str(ValSetProd()) == 'ValSetProd{empty=True}'
    assert str(ValSetProd(unique=True)) == 'ValSetProd{unique=True, empty=True}'


#
# TESTING ValSetZip
# -----------------
@pytest.fixture
def val_set_zip_data():
    D1 = {"a": 1}
    D2 = {"a": 2}
    D3 = {"b": 10}
    D4 = {"u": 100}
    D5 = {"u": 101}
    D6 = {"u": 102, "v": "wow"}
    D7 = {"x": 800}
    D8 = {"y": 900}
    D9 = {"x": 801, "y": 901}
    ARGS = ([D1, D2, D3], [D4, D5, D6], [D7, D8, D9])
    ALL = (
        {"a": 1, "u": 100, "x": 800},
        {"a": 2, "u": 101, "y": 900},
        {"b": 10, "u": 102, "v": "wow", "x": 801, "y": 901}
    )
    zip_ = ValSetZip(*ARGS)
    return zip_, ARGS, ALL


def test_ValSetZip__all(val_set_zip_data):
    """Test ValSetZip creation and getting all items in all() call."""
    assert ValSetZip().all() == ()
    assert ValSetZip([{}], [{}]).all() == ({},)
    zip_, _, ALL = val_set_zip_data
    assert zip_.all() == ALL


def test_ValSetZip__remove_duplicates_when_unique_set():
    """Test that ValSetZip with unique=True doesn't contain duplicates."""
    D1 = {"a": 10}
    D2 = {"a": 20}
    D3 = {"x": 34}
    D4 = {"x": 42}

    # First, make sure that without unique=True there are duplicates:
    zip1 = ValSetZip([D1, D2, D1], [D3, D4, D3])
    assert zip1.all() == (
        {"a": 10, "x": 34},
        {"a": 20, "x": 42},
        {"a": 10, "x": 34})

    # Now create without duplicates:
    zip2 = ValSetZip([D1, D2, D1], [D3, D4, D3], unique=True)
    assert zip2.all() == (
        {"a": 10, "x": 34},
        {"a": 20, "x": 42})


def test_ValSetZip__raise_error_when_key_sets_intersect():
    """Make sure ValSetZip checks that keys in dictionaries being merged
    do not intersect."""
    D11 = {"a": 10}
    D12 = {"a": 20, "u": 34}
    D13 = {"a": 20, "x": "wrong"}
    D21 = {"u": 42, "x": "correct"}
    D22 = {"x": "right"}
    D23 = {"x": "awful"}

    # First, check that ZIP-ing ({a}, {a, u}) and ({u, x}, {x}) is OK
    # since neither pair of dictionaries have intersecting key sets:
    assert ValSetZip([D11, D12], [D21, D22]).all() == (
        {"a": 10, "u": 42, "x": "correct"},
        {"a": 20, "u": 34, "x": "right"},
    )

    # Then check that ZIP-ing (..., {a, x}) and (..., {x}) raises error:
    with pytest.raises(KeyError):
        ValSetZip([D11, D12, D13], [D21, D22, D23])


def test_ValSetZip__raise_error_when_dimensions_differ():
    """Test that ValSetZip accepts sets with equal number of elements only.
    """
    with pytest.raises(IndexError):
        ValSetZip([{}], [{}, {}])


# noinspection PyTypeChecker
def test_ValSetZip__raise_error_when_argument_is_not_iterable_of_dicts():
    """Test that ValSetZip accepts only iterables of dictionaries.
    """
    with pytest.raises(TypeError):
        ValSetZip({"a": 10})
    with pytest.raises(TypeError):
        ValSetZip("abc")


def test_ValSetZip__iter(val_set_zip_data):
    """Test ValSetZip implements iterator __iter__ magic."""
    assert tuple(ValSetZip()) == ()
    zip_, _, ALL = val_set_zip_data
    assert tuple(zip_) == ALL


def test_ValSetZip__len(val_set_zip_data):
    """Test ValSetZip implements __len__ magic."""
    assert len(ValSetZip()) == 0
    zip_ = val_set_zip_data[0]
    assert len(zip_) == 3


# noinspection PyUnresolvedReferences
def test_ValSetZip__args(val_set_zip_data):
    """Test ValSetZip provides args ro-property with a tuple of arguments."""
    zip_, ARGS, _ = val_set_zip_data
    assert zip_.args == tuple(ARGS)
    with pytest.raises(AttributeError):
        zip_.args.append(({"a": 10}))


def test_ValSetZip__repr(val_set_zip_data):
    """Test ValSetZip implements __repr__ magic."""
    string = '''
ValSetZip:
    [{'a': 1}, {'a': 2}, {'b': 10}]
    [{'u': 100}, {'u': 101}, {'u': 102, 'v': 'wow'}]
    [{'x': 800}, {'y': 900}, {'x': 801, 'y': 901}]
    '''.strip()
    zip_ = val_set_zip_data[0]
    assert str(zip_) == string
    assert str(ValSetZip()) == 'ValSetZip{empty=True}'
    assert str(ValSetZip(unique=True)) == 'ValSetZip{unique=True, empty=True}'


#
# TESTING HELPERS
# ---------------
def test_make_unique():
    D1 = {"a": 1, "b": 2}
    D2 = {"b": 2, "a": 1}  # == D1
    D3 = {"a": 1, "b": 3}
    D4 = {"a": 1, "b": 2, "c": 3}
    D5 = {"x": 34}
    D6 = {"x": 34}
    assert make_unique((D1, D2, D3, D4, D5, D6)) == [D1, D3, D4, D5]


def test_guess_dtype():
    assert guess_dtype([]) == 'float'
    assert guess_dtype([1, 2]) == 'integer'
    assert guess_dtype([1, 2.3]) == 'float'
    assert guess_dtype(['abc', 'def']) == 'string'
    assert guess_dtype([1, '2']) is None


#
# INTEGRATED TESTS
# ----------------
def test_complex_val_set__rfid():
    """Create a complex values set from RFID config and validate it."""
    data = ValSetJoin(
        ValSetEval({
            "speed": ValRange(30, 50, step=10),
            "tari": ValArray(["12.5us", "18.75us"]),
            "m": ValArray([8])
        }),
        ValSetProd(
            ValSetEval({"speed": ValRange(50, 60, step=5)}),
            ValSetZip(
                ValSetEval({"tari": ValArray(["12.5us", "18.75us", "25.0us"])}),
                ValSetEval({"m": ValArray([8, 4, 2])})
            )
        ),
        unique=True
    )
    assert data.all() == (
        {"speed": 30, "tari": "12.5us", "m": 8},
        {"speed": 30, "tari": "18.75us", "m": 8},
        {"speed": 40, "tari": "12.5us", "m": 8},
        {"speed": 40, "tari": "18.75us", "m": 8},
        {"speed": 50, "tari": "12.5us", "m": 8},
        {"speed": 50, "tari": "18.75us", "m": 8},
        {"speed": 50, "tari": "18.75us", "m": 4},
        {"speed": 50, "tari": "25.0us", "m": 2},
        {"speed": 55, "tari": "12.5us", "m": 8},
        {"speed": 55, "tari": "18.75us", "m": 4},
        {"speed": 55, "tari": "25.0us", "m": 2},
        {"speed": 60, "tari": "12.5us", "m": 8},
        {"speed": 60, "tari": "18.75us", "m": 4},
        {"speed": 60, "tari": "25.0us", "m": 2},
    )

    assert str(data) == '''
ValSetJoin{unique=True}:
    ValSetEval:
        speed: ValRange{left=30, right=50, step=10}
        tari : ValArray{dtype=string, values=[12.5us, 18.75us]}
        m    : ValArray{dtype=integer, values=[8]}
    ValSetProd:
        ValSetEval:
            speed: ValRange{left=50, right=60, step=5}
        ValSetZip:
            ValSetEval:
                tari: ValArray{dtype=string, values=[12.5us, 18.75us, 25.0us]}
            ValSetEval:
                m: ValArray{dtype=integer, values=[8, 4, 2]}'''.strip()

#
# SCHEMA FIELDS TESTING
# ---------------------


#
# VALUE SETS SCHEMAS TESTING
# --------------------------
@pytest.mark.xfail
def test_ValArraySchema():
    """
    Test ValArray serialization and deserialization.

    Given
    -----
    - ValArray instance with non-empty values

    Validate
    --------
    - serialized string contains '"values"' keys
    - deserialization given a ValArray instance
    - deserialized instance has the same values and id as the original one
    """
    array = ValArray([10, 20, 30])
    schema = ValArraySchema()
    serialized = schema.dump(array)

    assert 'values' in serialized
    assert 'id' in serialized

    deserialized = schema.load(serialized)
    assert isinstance(deserialized, ValArray)
    assert deserialized.values == array.values
