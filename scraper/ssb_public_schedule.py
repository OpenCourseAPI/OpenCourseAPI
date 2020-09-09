from collections import defaultdict
from datetime import datetime
from hashlib import sha256, sha224

from bs4 import BeautifulSoup

from .ssb_base import BaseSSBScraper, SOUP_PARSER


class ScheduleScraper(BaseSSBScraper):
    PREFIX = 'sched_'

    def mine_campus_term(self, term: str, depts: dict):
        body_data = self.get_body_params(term, depts)

        cache_prefix = f'{self.ssb_campus}-' if self.ssb_campus else ''
        html = self.fetch_and_cache(
            'bwckschd.p_get_crse_unsec',
            f'{cache_prefix}{term}-public-schedule.html',
            data=body_data
        )
        soup = BeautifulSoup(html, SOUP_PARSER)
        rows = soup.select('.pagebodydiv > table.datadisplaytable > tr')
        # rows = soup.select('.pagebodydiv > form > table.datadisplaytable > tbody > tr')

        # {dept: {course: {CRN: []}}}
        the_holy_grail = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

        last_class = None

        for table_row in rows:
            ths = table_row.find_all('th', {'class': 'ddtitle'}, recursive=False)
            tds = table_row.find_all('td', {'class': 'dddefault'}, recursive=False)

            if len(ths) > 0 and len(tds) == 0:
                # print('Header', headers[0])
                text = ths[0].get_text().strip()
                parts = [part.strip() for part in text.split(' - ')]

                if len(parts) < 4:
                    print('Welp! this title is borked', parts)

                section = parts[-1]
                course  = parts[-2].split(' ')[-1]
                dept    = ' '.join(parts[-2].split(' ')[:-1])
                crn     = parts[-3]
                title   = ' - '.join(parts[:-3])

                data = {
                    'CRN': crn,
                    'raw_course': f'{dept} {course}{section}',
                    'dept': dept.replace(' ', ''),
                    'course': course,
                    'section': section,
                    'title': title,
                    'times': [],
                }

                last_class = data
                # print(section, dept, course, crn, title)

            elif len(ths) == 0 and len(tds) == 1:
                # print('Data', tds[0])
                data = last_class
                data_col = tds[0]

                if not data:
                    print('Skipping cause who knows what this is?', data_col)
                    continue

                more_details = defaultdict(str)
                prev_label = None

                for el in data_col.contents:
                    if isinstance(el, str):
                        if el == '\n':
                            prev_label = None
                        elif prev_label:
                            more_details[prev_label] += el.strip()
                        else:
                            text = el.strip()
                            if ' Credits' in text:
                                units = text.replace(' Credits', '').strip()
                                data['units'] = self.hooks.clean_units_str(units)
                            else:
                                pass
                                # print('Unhandled', el)
                    else:
                        if el.name == 'br':
                            prev_label = None

                        elif el.name == 'span' and 'fieldlabeltext' in el['class']:
                            label = el.get_text().strip().replace(':', '')
                            prev_label = label

                        elif el.name == 'table':
                            times = self.parse_inner_table(el)

                            for time in times:
                                if 'start' in time and 'end' in time:
                                    data['start'] = self.hooks.parse_date(time['start'])
                                    data['end'] = self.hooks.parse_date(time['end'])
                                    break

                            data['times'] = times

                        elif el.name == 'a':
                            pass

                        else:
                            # print('Unhandled', el)
                            pass

                if 'start' not in data:
                    data['start'] = 'TBA'
                if 'end' not in data:
                    data['end'] = 'TBA'

                data = self.hooks.transform_class(data)

                the_holy_grail[data['dept']][data['course']][data['CRN']] = data
                last_class = None

            elif len(ths) == 0 and len(tds) == 0:
                pass

            else:
                print('Unhandled row!', ths, tds)

        # print(the_holy_grail)
        return the_holy_grail

    def parse_inner_table(self, table):
        rows = table.find_all('tr')

        table_headers = []
        times = []

        for table_row in rows:
            ths = table_row.find_all('th', recursive=False)
            tds = table_row.find_all('td', recursive=False)

            headers = [th.get_text().strip() for th in ths]
            data_cols = [td.get_text().strip() for td in tds]

            if len(headers) > 0 and len(data_cols) == 0:
                table_headers = headers

            elif len(headers) == 0 and len(data_cols) > 0:
                data = dict(zip(table_headers, data_cols))
                dates = data.get('Date Range')

                instr_td = tds[table_headers.index('Instructors')]
                instructors = []
                last_name = ''

                def add_partial_last():
                    if last_name:
                        normalized = self.hooks.clean_instructor_name(last_name)
                        instructors.append({'full_name': normalized})

                for node in instr_td.contents:
                    if isinstance(node, str):
                        if node.strip().startswith(','):
                            add_partial_last()
                            last_name = node
                        else:
                            last_name += node
                    else:
                        if node.name == 'a':
                            full_name = self.hooks.clean_instructor_name(last_name)
                            email = node.get('href').replace('mailto:', '').strip()

                            instructors.append({
                                'id': sha224(email.encode()).hexdigest(),
                                'pretty_id': full_name.lower().replace(' ', '-'),
                                'full_name': full_name,
                                'display_name': node.get('target').strip(),
                                'email': email
                            })
                            last_name = ''

                        elif node.name == 'abbr':
                            last_name  += node.get_text()
                            pass

                        else:
                            print('idk what this is', node)

                add_partial_last()

                if not dates or dates == 'TBA':
                    start = 'TBA'
                    end = 'TBA'
                elif ' - ' in dates:
                    start = dates.split(' - ')[0].strip()
                    end = dates.split(' - ')[1].strip()
                else:
                    start = 'TBA'
                    end = 'TBA'
                    print('This is just stupiiid')

                # campus = ' '.join(data.get('Where').split(' ')[:-1])

                class_time = {
                    'type': data.get('Type'),
                    'days': data.get('Days'),
                    'time': data.get('Time'),
                    'instructor': instructors,
                    'location': data.get('Where') or 'TBA',
                    # 'instructor': data.get('Instructors'),
                    # 'room': data.get('Where').split(' ')[-1],
                    # 'campus': campus,

                    'start': start,
                    'end': end,
                }

                if class_time['days'] and class_time['days'] != 'TBA':
                    class_time['days'] = class_time['days'].replace('R', 'Th')

                times.append(class_time)

            else:
                print('Unhandled stuff')

        return times

    def get_body_params(self, term: str, depts: dict):
        return [
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
            ('sel_camp', self.ssb_campus or '%'),
            ('sel_ptrm', '%'),
            ('sel_instr', '%'),
            ('sel_sess', '%'),
            ('sel_attr', '%'),
            ('sel_levl', '%'),
            ('begin_hh', '0'),
            ('begin_mi', '0'),
            ('begin_ap', 'a'),
            ('end_hh', '0'),
            ('end_mi', '0'),
            ('end_ap', 'a'),
        ]
