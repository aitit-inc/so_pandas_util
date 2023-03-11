import pandas as pd
import pytest as pytest

from so_pandas_util.conditional_exp_evaluator import DfConditionEvaluator, \
    parse_cond_str

test_data = [
    # condition operators
    ('col1 > 1.2', '(df["col1"] > 1.2)'),
    ('col1 >= 1.2', '(df["col1"] >= 1.2)'),
    ('col1 == 1.2', '(df["col1"] == 1.2)'),
    ('col1 < 1.2', '(df["col1"] < 1.2)'),
    ('col1 <= 1.2', '(df["col1"] <= 1.2)'),
    ('col1 != 1.2', '(df["col1"] != 1.2)'),

    # string
    ('col1 != "abc"', '(df["col1"] != "abc")'),
    ('col1 != "1.2"', '(df["col1"] != "1.2")'),
    ('col1 != "1"', '(df["col1"] != "1")'),

    # int
    ('col1 != 1', '(df["col1"] != 1)'),

    # FIXME: can NOT use bool
    ('col1 != True', '(df["col1"] != "True")'),
    ('col1 != False', '(df["col1"] != "False")'),

    # logic operators
    ('col1 != 1 and col2 > 1.2', '(df["col1"] != 1) & (df["col2"] > 1.2)'),
    ('col1 != 1 or col2 > 1.2', '(df["col1"] != 1) | (df["col2"] > 1.2)'),

    # parentheses
    ('[col1 != 1] and [col2 > 1.2]',
     '((df["col1"] != 1)) & ((df["col2"] > 1.2))'),
    ('[col1 != 1 and col2 > 1.2] or col3 == "a"',
     '((df["col1"] != 1) & (df["col2"] > 1.2)) | (df["col3"] == "a")'),
]


@pytest.mark.parametrize("cond_str,expected", test_data)
def test_parse_cond_str(cond_str, expected):
    assert parse_cond_str(cond_str) == expected


@pytest.mark.parametrize('cond_str, expected', test_data)
def test_df_condition_evaluator_parse(cond_str, expected):
    parser = DfConditionEvaluator().parse(cond_str)
    assert parser._stmt == expected


def test_eval_stmt():
    df = pd.DataFrame({'col1': range(3)})
    cond_str = 'col1 != 1'
    parser = DfConditionEvaluator().parse(cond_str)
    expected = pd.Series([True, False, True])
    assert parser.eval(df).equals(expected)

    # custom df name
    my_df = pd.DataFrame({'col2': range(3)})
    cond_str2 = 'col2 > 1'
    parser2 = DfConditionEvaluator().parse(cond_str2)
    expected2 = pd.Series([False, False, True])
    assert parser2.eval(my_df).equals(expected2)
