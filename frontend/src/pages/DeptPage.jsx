import { h, Fragment } from 'preact'
import { useState, useEffect } from 'preact/hooks'
import { route } from 'preact-router';

import { campus } from '../data'
import { useApi } from '../state'
import TermPicker from '../components/TermPicker'
import BreadCrumbs from '../components/BreadCrumbs'

// const opt = { year: 'numeric', month: 'short', day: 'numeric' };
const opt = { month: 'short', day: 'numeric' };
const formatDate = (str) => new Date(Date.parse(str)).toLocaleDateString('en-US', opt);
const replaceTBA = (text) => text === 'TBA' ? <span class="none">(none)</span> : text;

const displayTimes = (time) => {
  const time_string = time.start_time == 'TBA' ? replaceTBA('TBA') : `${time.start_time} - ${time.end_time}`
  return (
    <>
      <td>{time.instructor}</td>
      <td>{replaceTBA(time.days)}</td>
      <td>{time_string}</td>
      <td>{time.location}</td>
    </>
  );
    // <td>${time.room}</td>
};


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
  const [courses, error] = useApi(`/${college}/depts/${dept}/courses`)
  const [classes, error2] = useApi(`/${college}/depts/${dept}/classes`)
  const colleged = campus.find((cmp) => cmp.id === college);

  const cards = courses
    ? courses.map(({ dept, course, title, classes }) => (
      <DeptCard
        id={course}
        dept={dept}
        course={course}
        title={title}
        name={`${dept} ${course}: ${title}`}
        count={classes.length}
        subinfo={`class${classes.length > 1 ? 'es' : ''}`}
        // subinfo={`${classes.length} class${classes.length > 1 ? 'es' : ''}`}
        setDept={(course) => route(`/campus/${college}/dept/${dept}/course/${course}`)}
      />
    ))
    : []


  const view = 'list-view'
  // const view = 'breadcrumb-view'
  // const view = 'card-view'

  const hasSeatInfo = classes && classes[0] ? (classes[0].status && classes[0].seats != undefined) : true;
  const headers = ['CRN', 'Course', 'Title', 'Dates', ...(hasSeatInfo ? ['Status', 'Seats', 'Waitlist'] : []), 'Professor', 'Days', 'Time', 'Location']
  const row_els = []

  if (classes) {
    for (const section of classes) {
      const start = formatDate(section.start);
      const end = formatDate(section.end);

      const rows = section.times.length;
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
    { url: `/campus/${college}`, name: colleged.name },
    { url: `/campus/${college}/dept/${dept}`, name: dept },
  ]

  return (
    <div class="root">
      <BreadCrumbs stack={crumbs} />
      <div class="title-container">
        <h1>{dept} @ {colleged.name}</h1>
        <div style="flex: 1"></div>
        <TermPicker />
      </div>
      <h3>Courses</h3>
      <div class={`course-card-container ${view}`}>{cards}</div>
      <h3 style={{ marginTop: '2em' }}>All Classes</h3>
      <div style={{ fontSize: '14px' }}>
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
