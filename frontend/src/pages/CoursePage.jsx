import { h, Fragment } from 'preact'
import { useState, useEffect } from 'preact/hooks'

import { campus, PATH_PREFIX } from '../data'
import { useApi } from '../state'
import BreadCrumbs from '../components/BreadCrumbs'

const opt = { year: 'numeric', month: 'short', day: 'numeric' }
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

export default function CoursePage({ college, dept, course }) {
  const [classes, error] = useApi(`/${college}/depts/${dept}/courses/${course}/classes`)
  const colleged = campus.find((cmp) => cmp.id === college)

  const row_els = []
  const first = (classes && classes[0]) || {}
  const hasSeatInfo = classes && classes[0] ? (classes[0].status && classes[0].seats != undefined) : true
  const headers = ['CRN', 'Start', 'End', ...(hasSeatInfo ? ['Status', 'Seats', 'Waitlist'] : []), 'Professor', 'Days', 'Time', 'Location']
  // <th>Room</th>

  if (classes) {
    for (const section of classes) {
      const start = formatDate(section.start)
      const end = formatDate(section.end)

      const rows = section.times.length
      const table_rows = [
        // section.CRN,
        section.CRN.toString().padStart(5, '0'),
        start,
        end,
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
    { url: `${PATH_PREFIX}/${college}`, name: colleged.name },
    { url: `${PATH_PREFIX}/${college}/dept/${dept}${window.location.search}`, name: dept },
    { url: `${PATH_PREFIX}/${college}/dept/${dept}/course/${course}${window.location.search}`, name: course },
  ]

  return (
    <div class="root">
      <BreadCrumbs stack={crumbs} />
      <h1 style={{ marginBottom: '1em' }}>{dept} {course} @ {colleged.name}</h1>
      <p style={{ marginTop: 0 }}>{first.title}&nbsp; · &nbsp;{first.units} units</p>
      <div class="table-container">
        <table class="classes data">
          <thead>
            <tr>
              {headers.map((name) =>  <th>{name}</th>)}
            </tr>
          </thead>
          <tbody>{row_els}</tbody>
        </table>
      </div>
    </div>
  )
}
