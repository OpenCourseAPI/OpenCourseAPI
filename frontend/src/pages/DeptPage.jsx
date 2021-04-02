import { h, Fragment } from 'preact'
import { useState, useEffect } from 'preact/hooks'
import matchSorter from 'match-sorter'

import { campus, PATH_PREFIX } from '../data'
import { setIntersection, formatDate } from '../utils'
import { useApi } from '../state'
import { CampusNotFound, DeptNotFound } from '../components/NotFound'
import { Fade } from '../components/Transitions'
import Header from '../components/Header'
import Search from '../components/Search'
import ClassesTable from '../components/ClassTable'
import Link from '../components/Link'
import BreadCrumbs from '../components/BreadCrumbs'

const dateFormatOpts = { month: 'short', day: 'numeric' }

function CourseCard({ college, dept, course, title, count, subinfo }) {
  return (
    <Link
      className="card course"
      href={`${PATH_PREFIX}/${college}/dept/${dept}/course/${course}${window.location.search}`}
      unstyle
    >
      <span class="course-id">{dept} {course}</span>
      <div style={{ flex: 1 }}></div>
      <div class="more-info">
        <span class="counter">{count}</span>
        <span class="counter-label">{subinfo}</span>
      </div>
      <div class="name">{title}</div>
    </Link>
  )
}

export default function DeptPage({ college, dept, setCourse }) {
  const colleged = campus.find((cmp) => cmp.id === college)

  if (!colleged) return <CampusNotFound />

  const [courses, coursesError] = useApi(`/${college}/depts/${dept}/courses`)
  const [classes, classesError] = useApi(`/${college}/depts/${dept}/classes`)

  const [query, setQuery] = useState('')
  const [filteredCourses, setFilteredCourses] = useState([])
  const [filteredClasses, setFilteredClasses] = useState([])

  useEffect(() => {
    if (courses && classes) {
      const getInstructors = item => item.times
        .map(time => time.instructor).join(',')
      //   .map(time => (
      //     (time.instructor || []).map(
      //       ({ full_name, display_name }) => display_name || full_name
      //     ))
      //   )
      //   .join(' ')

      const filteredClasses = matchSorter(classes, query, {
        keys: [
          {minRanking: matchSorter.rankings.MATCHES, key: getInstructors },
          {threshold: matchSorter.rankings.EQUAL, key: 'course'},
          {threshold: matchSorter.rankings.CONTAINS, key: 'title'},
          item => item.dept + ' ' + item.course,
          'CRN',
        ]
      })

      const filteredCRNS = new Set(filteredClasses.map(course => course.CRN))

      let filteredCourses = courses.map(course => {
        return {...course, classes: Array.from(setIntersection(new Set(course.classes), filteredCRNS))}
      })

      setFilteredCourses(filteredCourses.filter(course => course.classes.length))
      setFilteredClasses(classes.filter(c => filteredCRNS.has(c.CRN)))
    }
  }, [courses, classes, query])

  const postFilterCourses = (query && filteredCourses) || courses
  const cards = postFilterCourses && postFilterCourses.length
    ? postFilterCourses.map(({ dept, course, title, classes }) => (
      <CourseCard
        college={college}
        dept={dept}
        course={course}
        title={title}
        count={classes.length}
        subinfo={`class${classes.length > 1 ? 'es' : ''}`}
      />
    ))
    : []


  const view = 'list-view'
  // const view = 'breadcrumb-view'
  // const view = 'card-view'

  const hasSeatInfo = (classes || []).some((cl) => cl.status && cl.status !== 'unknown')
  const postFilterClasses = (query && filteredClasses) || classes
  const headers = [
    'Course',
    'Title',
    'CRN',
    'Dates',
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
    { url: `${PATH_PREFIX}/${college}${window.location.search}`, name: colleged.name },
    { url: `${PATH_PREFIX}/${college}/dept/${dept}${window.location.search}`, name: dept },
  ]

  let content;

  if ((coursesError || classesError) == 'NOT_FOUND') {
    content = <DeptNotFound backLink={crumbs[crumbs.length - 2].url} />
  } else {
    content = (
      <>
        <Search
          placeholder="Filter by course, title, professor, or CRN..."
          query={query}
          setQuery={setQuery}
        />
        {(query && !cards.length) ? (
          <div style={{ marginTop: '2em' }}>
            No matches for "{query}"! Try searching for something else.
          </div>
        ) : (
          <>
            <Fade in={!!courses} duration={300}>
              <h3 style={{ marginTop: '1.5em' }}>Courses</h3>
              <div class={`course-card-container ${view}`}>{cards}</div>
            </Fade>
            <Fade in={!!(courses && classes)} duration={300}>
              <h3 style={{ marginTop: '1.5em' }}>All Classes</h3>
              <ClassesTable
                headers={headers}
                classes={postFilterClasses}
                getClassColumns={(section, lastSection) => {
                  const start = formatDate(section.start, dateFormatOpts)
                  const end = formatDate(section.end, dateFormatOpts)

                  const courseName = `${section.dept} ${section.course}`
                  const lastCourseName = lastSection && `${lastSection.dept} ${lastSection.course}`
                  const sameCourse = courseName == lastCourseName
                  const courseLink = `${PATH_PREFIX}/${college}/dept/${section.dept}/course/${section.course}${window.location.search}`

                  return [
                    sameCourse ? '' : <Link href={courseLink}>{courseName}</Link>,
                    sameCourse ? '' : `${section.title}`,
                    section.CRN.toString().padStart(5, '0'),
                    `${start} - ${end}`,
                    ...(hasSeatInfo ? [
                      section.status,
                      section.seats,
                      section.wait_cap ? `${section.wait_seats}/${section.wait_cap}` : section.wait_seats
                    ] : [])
                  ]
                }}
              />
            </Fade>
          </>
        )}
      </>
    )
  }

  return (
    <div class="root">
      <BreadCrumbs stack={crumbs} />
      <Header title={`${dept} @ ${colleged.name}`} />
      {content}
    </div>
  )
}
