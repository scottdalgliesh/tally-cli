from datetime import date, datetime
from pathlib import Path
import re
from typing import List, Tuple, TypedDict, Union

from tika import parser


class TransDict(TypedDict):
    '''Provide type hinting support for transaction dict (stage 1)'''
    Date: List[date]
    Description: List[str]
    Value: List[float]


def parse_statement(url: Union[str, Path]) -> TransDict:
    '''Parse all transactions from a banking statment.'''
    url = Path(url)
    statement_text = parser.from_file(str(url))['content']
    start_date, end_date = get_statement_dates(statement_text)
    trans_dict = get_transactions(statement_text, start_date, end_date)
    return trans_dict


def get_statement_dates(statement_text: str) -> Tuple[date, date]:
    '''Parse the statement start and end date from the statement text.'''
    pattern = re.compile(
        r'STATEMENT FROM (\D{3} \d{2}(, \d{4})?) TO (\D{3} \d{2}, \d{4})')
    match = re.search(pattern, statement_text)
    if match is None:
        raise TypeError('Error parsing statement beginning and end dates.')
    end_date = datetime.strptime(match.group(3), '%b %d, %Y').date()
    if match.group(2) is None:
        start_text = f'{match.group(1)}, {str(end_date.year)}'
    else:
        start_text = match.group(1)
    start_date = datetime.strptime(start_text, '%b %d, %Y').date()
    return start_date, end_date


def get_transactions(statement_text: str, start_date: date, end_date: date) -> TransDict:
    '''Parse the transactions from the statement text.'''
    pattern = re.compile(
        r'(\D{3} \d{2}) \D{3} \d{2} (.+)\n+\d+\n+(-?\$\d+\.\d+)')
    matches = list(re.finditer(pattern, statement_text))
    if len(matches) == 0:
        raise ValueError(
            'No transactions matched while parsing the statement.')

    # generate lists of transaction dates, descriptions and values
    trans_date, desc, valu = [], [], []
    for match in matches:
        trans_date.append(match.group(1))
        desc.append(match.group(2))
        valu.append(float(match.group(3).replace('$', '')))

    # add the year to the transaction date and convert to date object
    start_month = start_date.strftime('%b').upper()
    date_obj = []
    for partial_date_str in trans_date:
        if partial_date_str.split()[0] == start_month:
            complete_date_str = f'{partial_date_str} {start_date.year}'
        else:
            complete_date_str = f'{partial_date_str} {end_date.year}'
        date_obj.append(datetime.strptime(
            complete_date_str, '%b %d %Y').date())

    # combine date, description and value and return as a dict
    trans_dict: TransDict = {'Date': date_obj,
                             'Description': desc, 'Value': valu}
    return trans_dict
