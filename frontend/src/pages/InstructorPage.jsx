import { h, Fragment } from 'preact'
import Match from 'preact-router'

import { campus, PATH_PREFIX } from '../data'
import { useApi } from '../state'
import { CampusNotFound } from '../components/NotFound'
import BreadCrumbs from '../components/BreadCrumbs'

const Link = Match.Link
const firstCharUpper = (str) => str.charAt(0).toUpperCase() + str.substring(1)

export default function InstructorPage({ college, id }) {
  const colleged = campus.find((cmp) => cmp.id === college)

  if (!colleged) return <CampusNotFound />

  const [instructor, error] = useApi(`/${college}/instructors/${id}`)
  const crumbs = [
    { url: '/', name: 'Home' },
    { url: `${PATH_PREFIX}/${college}${window.location.search}`, name: colleged.name },
    { url: `${PATH_PREFIX}/${college}/instructor/${id}${window.location.search}`, name: id },
  ]
  const groupedClasses = {}

  if (instructor) {
    instructor.classes.sort((a, b) => b.term_code - a.term_code).map(({ term, year, dept, course, seats_taken }) => {
      const title = firstCharUpper(`${term} ${year}`)

      if (!groupedClasses[title]) groupedClasses[title] = []

      // let text = `Taught ${dept} ${course}`
      let text = ``
      let courseName = `${dept} ${course}`

      if (seats_taken != undefined && seats_taken != null) text += ` to ${seats_taken} students`

      groupedClasses[title].push(
        <div>
          <span>Taught </span>
          <Link href={`${PATH_PREFIX}/${college}/dept/${dept}/course/${course}?year=${year}&term=${term}`}>{courseName}</Link>
          {text}
        </div>
      )
    })
  }

  return (
    error == 'NOT_FOUND' ? (
      <CampusNotFound />
    ) : (
      <div class="root">
        <BreadCrumbs stack={crumbs} />
        <div class="title-container">
          <h1>{instructor ? instructor.display_name || instructor.full_name : id} @ {colleged.name}</h1>
          {/* <div style="flex: 1"></div> */}
          {/* <Header query={query} setQuery={setQuery}/> */}
        </div>
        {instructor && (
          <div>Email: <a href={`mailto:${instructor.email}`}>{instructor.email}</a></div>
        )}
        <div style={{ lineHeight: 2 }}>
          {Object.entries(groupedClasses).map(([title, els]) => (
            <>
              <h2 style={{ fontSize: '1.4rem', marginTop: '1.5em', marginBottom: '1.2em' }}>{title}</h2>
              {els}
            </>
          ))}
        </div>
        {/* <h3>{email} @ {colleged.name}</h3>
        <div class={`dept-card-container ${view}`}>{cards}</div> */}
      </div>
    )
  )
}
