import re
import gmail_get


def get_data_from_text(text):

    """Function that help to filter a message using regex pattern and collect some values to variables.
    Output is a dict of data"""

    regex = '.*(?P<date>\d\d\.\d\d\.\d\d\d\d).*новый сотрудник (?P<name>.*) \(.*подразделение (?P<department>.*) на ' \
            'должность (?P<role>.*)\..*Руководитель - (?P<manager>.*)\..*Офис '
    match = re.match(regex, text, re.DOTALL)
    return {
        'date': match.group('date'),
        'name': match.group('name'),
        'department': match.group('department'),
        'role': match.group('role'),
        'manager': match.group('manager')
    }


def get_array_of_data():

    """Function helps to collect all filtered data in one array and it returns that"""

    array_of_data = []
    array_of_messages = gmail_get.get_bodies_of_messages()
    for msg in array_of_messages:
        if 'новый сотрудник' in msg:
            message = get_data_from_text(msg)
            array_of_data.append(message)
    return array_of_data


