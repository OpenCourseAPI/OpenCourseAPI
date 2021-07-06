import { h, Fragment } from 'preact'

import { campus, PATH_PREFIX } from '../data'
import { useApi } from '../state'
import { formatDate } from '../utils'
import BreadCrumbs from '../components/BreadCrumbs'
import ClassesTable from '../components/ClassTable'
import Header from '../components/Header'
import { CampusNotFound, CourseNotFound } from '../components/NotFound'

const dateFormatOpts = { year: 'numeric', month: 'short', day: 'numeric' }

export default function CoursePage({ college, dept, course }) {
  const colleged = campus.find((cmp) => cmp.id === college)

  if (!colleged) return <CampusNotFound />

  const [classes, error] = useApi(`/${college}/depts/${dept}/courses/${course}/classes`)

  const first = classes && classes[0]
  const hasSeatInfo = (classes || []).some((cl) => cl.status && cl.status !== 'unknown')
  const headers = [
    'CRN',
    'Start',
    'End',
    ...(
      hasSeatInfo ? [
        'Status',
        'Seats',
        'Waitlist'
      ] : []
    ),
    'Professor',
    'Days',
    'Time',
    'Location',
  ]
  const crumbs = [
    { url: '/', name: 'Home' },
    { url: `${PATH_PREFIX}/${college}`, name: colleged.name },
    { url: `${PATH_PREFIX}/${college}/dept/${dept}${window.location.search}`, name: dept },
    { url: `${PATH_PREFIX}/${college}/dept/${dept}/course/${course}${window.location.search}`, name: course },
  ]

  let content;

  if (error == 'NOT_FOUND') {
    content = <CourseNotFound backLink={crumbs[crumbs.length - 2].url} />
  } else {
    content = (
      <>
        <p style={{ marginTop: 0 }}>
          {(first && first.title) || ''}&nbsp; · &nbsp;{first ? first.units : 'X'} units
        </p>
        <ClassesTable
          headers={headers}
          classes={classes}
          getClassColumns={(section) => {
            const start = formatDate(section.start, dateFormatOpts)
            const end = formatDate(section.end, dateFormatOpts)

            return [
              section.CRN.toString().padStart(5, '0'),
              start,
              end,
              ...(hasSeatInfo ? [
                section.status,
                section.seats,
                section.wait_cap ? `${section.wait_seats}/${section.wait_cap}` : section.wait_seats
              ] : [])
            ]
          }}
        />
      </>
    )
  }

  return (
    <div class="root">
      <BreadCrumbs stack={crumbs} />
      <Header title={`${dept} ${course} @ ${colleged.name}`} />
      {content}
    </div>
  )
}
