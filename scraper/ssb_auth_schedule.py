from collections import defaultdict

from bs4 import BeautifulSoup

from .ssb_base import BaseSSBScraper, BaseHooks, SOUP_PARSER


def parse_class_time(data, hooks: BaseHooks):
    instructors = data.get('Instructor')
    instructors = [{'full_name': hooks.clean_instructor_name(name)} for name in instructors.split(',')] if instructors else []

    converted = {
        'days': data.get('Days'),
        'time': data.get('Time'),
        'instructor': instructors,
        'location': data.get('Location') or 'TBA',
        # 'room': data.get('Location'),
        # 'campus': data.get('Cmp'),
    }

    if converted['days'] and converted['days'] != 'TBA':
        converted['days'] = converted['days'].replace('R', 'Th')

    # if not converted['campus']:
    #     print(data)

    # if not converted['room']:
    #     converted['room'] = 'TBA'
    # else:
    #     converted['room'] = converted['room'].replace(f'{converted["campus"]} ', '')

    return converted


def parse_class_data(data):
    converted = {}

    converted['CRN'] = data.get('CRN')
    converted['dept'] = data.get('Subj')
    converted['course'] = data.get('Crse')
    converted['section'] = data.get('Sec')
    converted['raw_course'] = converted['dept'] + ' ' + converted['course'] + converted['section']

    converted['dept'] = converted['dept'].replace(' ', '')

    converted['title'] = data.get('Title')
    converted['units'] = data.get('Cred')

    converted['seats'] = data.get('Rem')
    converted['seats_taken'] = data.get('Act')
    converted['wait_seats'] = data.get('WL Rem')
    # converted['wait_cap'] = 0

    if converted['wait_seats'] == 'TBA':
        converted['wait_seats'] = 0

    if '-' in converted['units']:
        splitted = converted['units'].split('-')
        converted['units'] = splitted[-1]

    try:
        if data['Date (MM/DD)'] == 'TBA':
            converted['start'] = 'TBA'
            converted['end'] = 'TBA'

        else:
            parsed_dates = data['Date (MM/DD)'].split('-')

            if len(parsed_dates) == 2:
                [start, end] = parsed_dates
                converted['start'] = start + '/2020'
                converted['end'] = end + '/2020'
            else:
                pass
                # print(
                #     'What the heck? Our parsed date seem super to be wierd...',
                #     data['Date (MM/DD)'],
                #     parsed_dates
                # )
    except AttributeError:
        pass
    except KeyError:
        pass

    if 'start' not in converted or 'end' not in converted:
        print(data)

    return converted


class AdvancedScraper(BaseSSBScraper):
    PREFIX = 'new_'

    def mine_campus_term(self, term: str, depts: dict):
        body_data = self.get_body_params(term, depts)

        html = self.fetch_and_cache(
            'bwskfcls.P_GetCrse_Advanced',
            f'{term}-advanced-schedule.html',
            data=body_data,
            authenticated=True,
        )
        soup = BeautifulSoup(html, SOUP_PARSER)
        rows = soup.select('.pagebodydiv > form > table.datadisplaytable > tr')
        # rows = soup.select('.pagebodydiv > form > table.datadisplaytable > tbody > tr')

        # {dept: {course: {CRN: []}}}
        the_holy_grail = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

        last_dept = None
        last_headers = None
        last_class = None
        last_class_time = None

        for table_row in rows:
            ths = table_row.find_all('th', recursive=False)
            tds = table_row.find_all('td', recursive=False)

            def magic_clean(els):
                cols = []
                for el in els:
                    text = el.get_text().strip()
                    colspan = int(el.get('colspan') or 1)
                    cols += [text for _ in range(colspan)]
                return cols

            headers = magic_clean(ths)
            data_cols = magic_clean(tds)

            if len(ths) == 1 and len(tds) == 0:
                # Department title row
                last_dept = ths[0].get_text()
                # print('Dept: ', last_dept)

            elif len(ths) > 0 and len(tds) == 0:
                # Table headers row
                last_headers = headers
                # print('Table Headers: ', headers)

            elif len(ths) == 0 and len(tds) > 0:
                if len(data_cols) != len(last_headers):
                    print('err Headers and data do not match', last_headers, data_cols)

                # Class row
                data = {k: v for k, v in zip(last_headers, data_cols) if v}
                # print('Class Data: ', data)

                if len(data) == 0:
                    continue

                is_first_row_for_class = data.get('CRN')

                # if not is_first_row_for_class and data.get('Cmp') is None and last_class_time:
                #     data['Cmp'] = last_class_time['campus']

                class_time_data = last_class_time = parse_class_time(data, self.hooks)

                if is_first_row_for_class:
                    class_data = last_class = parse_class_data(data)
                    class_data['times'] = [class_time_data]
                else:
                    class_data = last_class
                    class_data['times'].append(class_time_data)

                class_data = self.hooks.transform_class(class_data)
                the_holy_grail[class_data['dept']][class_data['course']][class_data['CRN']] = class_data

            else:
                print('Unhandled row', headers, data_cols)

        return the_holy_grail

    def get_body_params(self, term: str, depts: dict):
        return [
            ('rsts', 'dummy'),
            ('crn', 'dummy'),
            ('term_in', term),
            ('sel_subj', 'dummy'),
            ('sel_day', 'dummy'),
            ('sel_schd', 'dummy'),
            ('sel_insm', 'dummy'),
            ('sel_camp', 'dummy'),
            ('sel_levl', 'dummy'),
            ('sel_sess', 'dummy'),
            ('sel_instr', 'dummy'),
            ('sel_ptrm', 'dummy'),
            ('sel_attr', 'dummy'),
            *[('sel_subj', dept_id) for dept_id in depts.keys()],
            ('sel_crse', ''),
            ('sel_title', ''),
            ('sel_schd', '%'),
            ('sel_from_cred', ''),
            ('sel_to_cred', ''),
            ('sel_camp', '%'),
            ('sel_instr', '%'),
            ('sel_sess', '%'),
            ('sel_ptrm', '%'),
            ('sel_attr', '%'),
            ('sel_levl', '%'),
            ('begin_hh', '0'),
            ('begin_mi', '0'),
            ('begin_ap', 'a'),
            ('end_hh', '0'),
            ('end_mi', '0'),
            ('end_ap', 'a'),
            ('SUB_BTN', 'Section Search'),
            ('path', '1'),
        ]
