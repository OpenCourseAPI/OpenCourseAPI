import { h, Fragment } from 'preact'
import { useState, useEffect } from 'preact/hooks'
import { route } from 'preact-router'
import matchSorter from 'match-sorter'

import { campus, PATH_PREFIX } from '../data'
import { setIntersection } from '../utils'
import { useApi } from '../state'
import { CampusNotFound } from '../components/NotFound'
import Header from '../components/Header'
import BreadCrumbs from '../components/BreadCrumbs'

// const opt = { year: 'numeric', month: 'short', day: 'numeric' }
const opt = { month: 'short', day: 'numeric' }
const formatDate = (str) => new Date(Date.parse(str)).toLocaleDateString('en-US', opt)
const replaceTBA = (text) => text === 'TBA' ? <span class="none">(none)</span> : text

const displayTimes = (time) => {
  const time_string = time.start_time == 'TBA' ? replaceTBA('TBA') : `${time.start_time} - ${time.end_time}`
  return (
    <>
      <td>{time.instructor}</td>
      <td>{replaceTBA(time.days)}</td>
      <td>{time_string}</td>
      <td>{time.location}</td>
    </>
  )
    // <td>${time.room}</td>
}

// function DeptCard({ id, name, count, subinfo, setDept }) {
function DeptCard({ id, name, dept, course, title, count, subinfo, setDept }) {
  return (
    <div class="card course" onClick={() => setDept(id)}>
      {/* <div class="name">{name}</div> */}
      <span class="course-id">{dept} {course}</span>
      <div style={{'flex': 1}}></div>
      <div class="more-info">
        <span class="counter">{count}</span>
        <span class="counter-label">{subinfo}</span>
      </div>
      <div class="name">{title}</div>
    </div>
  )
}

export default function DeptPage({ college, dept, setCourse }) {
  const colleged = campus.find((cmp) => cmp.id === college)

  if (!colleged) return <CampusNotFound />

  const [courses, error] = useApi(`/${college}/depts/${dept}/courses`)
  const [classes, error2] = useApi(`/${college}/depts/${dept}/classes`)

  const [query, setQuery] = useState('')
  const [filteredCourses, setFilteredCourses] = useState([])
  const [filteredClasses, setFilteredClasses] = useState([])

  useEffect(() => {
    if (courses && classes) {
      const filteredClasses = matchSorter(classes, query, {
        keys: [
          {minRanking: matchSorter.rankings.MATCHES, key: item => item.times.map(time => time.instructor).join(',')},
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
      <DeptCard
        id={course}
        dept={dept}
        course={course}
        title={title}
        name={`${dept} ${course}: ${title}`}
        count={classes.length}
        subinfo={`class${classes.length > 1 ? 'es' : ''}`}
        // subinfo={`${classes.length} class${classes.length > 1 ? 'es' : ''}`}
        setDept={(course) => route(`${PATH_PREFIX}/${college}/dept/${dept}/course/${course}${window.location.search}`)}
      />
    ))
    : []


  const view = 'list-view'
  // const view = 'breadcrumb-view'
  // const view = 'card-view'

  const hasSeatInfo = classes && classes[0] ? (classes[0].status && classes[0].seats != undefined) : true
  const headers = ['CRN', 'Course', 'Title', 'Dates', ...(hasSeatInfo ? ['Status', 'Seats', 'Waitlist'] : []), 'Professor', 'Days', 'Time', 'Location']
  const row_els = []

  const postFilterClasses = (query && filteredClasses) || classes
  if (postFilterClasses && postFilterClasses.length) {
    for (const section of postFilterClasses) {
      const start = formatDate(section.start)
      const end = formatDate(section.end)

      const rows = section.times.length
      const table_rows = [
        section.CRN.toString().padStart(5, '0'),
        `${section.dept} ${section.course}`,
        `${section.title}`,
        `${start} - ${end}`,
        // end,
        ...(hasSeatInfo ? [
          section.status,
          section.seats,
          section.wait_cap ? `${section.wait_seats}/${section.wait_cap}` : section.wait_seats
        ] : [])
      ]

      row_els.push(
        <tr>
          {table_rows.map((name) => <td rowspan={rows}>{name}</td>)}
          {displayTimes(section.times[0])}
        </tr>
      )

      for (const time of section.times.slice(1)) {
        row_els.push(
          <tr>
            {displayTimes(time)}
          </tr>
        )
      }
    }
  }

  const crumbs = [
    { url: '/', name: 'Home' },
    { url: `${PATH_PREFIX}/${college}${window.location.search}`, name: colleged.name },
    { url: `${PATH_PREFIX}/${college}/dept/${dept}${window.location.search}`, name: dept },
  ]

  return (
    <div class="root">
      <BreadCrumbs stack={crumbs} />
      <div class="title-container">
        <h1>{dept} @ {colleged.name}</h1>
        <div style="flex: 1"></div>
        <Header query={query} setQuery={setQuery}/>
      </div>
      <h3>Courses</h3>
      <div class={`course-card-container ${view}`}>{cards}</div>
      <h3 style={{ marginTop: '2em' }}>All Classes</h3>
      <div class="table-container" style={{ fontSize: '14px' }}>
        <table class="classes data">
          <thead>
            <tr>
              {headers.map((name) =>  <th>{name}</th>)}
            </tr>
          </thead>
          <tbody>
            {row_els}
          </tbody>
        </table>
      </div>
    </div>
  )
}
