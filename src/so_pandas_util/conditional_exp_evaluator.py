from typing import Optional

import pandas as pd
import pycond as pc


def parse_cond_str(cond_str: str, df_name: str = 'df') -> str:
    """
    Parse string to construct condition expression
    of filtering Pandas DataFrame

    example:
    - input: 'col1 >= 5 or [col2 > 15 and col2 < 22] or col3 == 70.0'
    - output: '(df["col1"] >= 5.0) | ((df["col2"] > 15.0) & (df["col2"] < 22.0)) | (df["col3"] == 70.0)'
    """
    pc.ops_use_symbolic()
    cond_ops = {'>', '<', '>=', '<=', '==', '!='}
    logic_ops = {'and', 'or'}

    cond = ''

    _, meta = pc.parse_cond(cond_str)
    cols = set(meta['keys'])
    struct = pc.to_struct(pc.tokenize(cond_str, sep=' ', brkts='[]'))
    for v in struct:
        if type(v) == list:
            cond += f'({parse_cond_str(" ".join(v))})'
        elif v in cond_ops:
            cond += ' ' + v
        elif v in logic_ops:
            v = '&' if v == 'and' else '|'
            cond += f' {v} '
        elif v in cols:  # column name
            cond += f'({df_name}["{v}"]'
        else:  # value to compare
            if v.isdigit():
                v = int(v)
            else:
                try:
                    v = float(v)
                except ValueError:  # v is string
                    v = f'"{v.strip("str:")}"'

            cond += f' {v})'

    return cond


class DfConditionEvaluator:

    def __init__(self):
        pc.ops_use_symbolic()
        self._stmt = ''

    def parse(self, text: str):
        self._stmt = parse_cond_str(text)
        return self

    def eval(self, df, text: Optional[str] = None) -> pd.Series:
        if text:
            self.parse(text)

        if not len(self._stmt):
            raise RuntimeError('No statement found')

        return eval(self._stmt, {'__builtins__': None, 'df': df})


def main():
    ss = [
        'id1 > 15.2',
        '[id1 > 15.2]',
        'id10 == "abc"',
        'id10 == \"abc\"',
        'id10 == 文字列',
        'id10 == "文字列"',
        'id10 == str:abc',
        'id10 == 123.1',
        'id10 == "123.1"',
        'id1 > 15 and id1 < 22',
        '[id1 > 15] and [id1 < 22]',
        '[ id1 > 15 ] and [ id1 < 22 ]',
        '[id1 > 15 and id1 < 22] or id2 <= 50',
        '[ id1 > 15 and id1 < 22 ] or id2 <= 50',
        'id3 == "val1" or id3 == "val2"',
    ]

    for s in ss:
        parser = DfConditionEvaluator()
        parser.parse(s)
        print(parser._stmt)

    df = pd.DataFrame({
        'c1': range(6),
        'c2': list('abcdef'),
    })
    cond_str = '[c1 > 1 and c1 <= 3] or c2 == "f"'
    parser = DfConditionEvaluator()
    parser.parse(cond_str)
    print(parser._stmt)
    print(parser.eval(df, cond_str))


if __name__ == '__main__':
    main()
