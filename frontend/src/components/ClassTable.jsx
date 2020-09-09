import { h, Fragment } from 'preact'
import Match from 'preact-router/match'

const Link = Match.Link

const replaceTBA = (text) => (
  text === 'TBA'
    ? (
      <span class="none">(none)</span>
    )
    : text
)

function ClassTimeCols({ time, campusId }) {
  const timeString = time.start_time == 'TBA'
    ? replaceTBA('TBA')
    : `${time.start_time || '?'} - ${time.end_time || '?'}`

  // const instructors = (time.instructor || [])
  //   .map(
  //     ({ full_name, display_name, email }) => display_name || full_name
  //   )
  //   .join(', ')

  const instructors = (time.instructor || [])
    .map(({ full_name, display_name, email, pretty_id }, index, arr) => {
      let name = display_name || full_name

      if (index < arr.length - 1) {
        name += ', '
      }

      return pretty_id
        ? <Link href={`/explore/${campusId}/instructor/${pretty_id}`} title={email}>{name}</Link>
        : <span>{name}</span>
    })
    .flat()

  return (
    <>
      <td>{instructors || '?'}</td>
      <td>{replaceTBA(time.days || '?')}</td>
      <td>{timeString || '?'}</td>
      <td>{time.location || '?'}</td>
    </>
  )
}

export default function ClassesTable({ campusId, headers, classes, getClassColumns }) {
  if (!classes) return <></>

  const tableRowEls = []

  for (const section of classes) {
    const numRows = section.times.length || 1
    const tableCols = getClassColumns(section)

    tableRowEls.push(
      <tr>
        {tableCols.map((name) => <td rowspan={numRows}>{name}</td>)}
        <ClassTimeCols campusId={campusId} time={section.times[0] || {}} />
      </tr>
    )

    for (const time of section.times.slice(1)) {
      if (!time) continue
      tableRowEls.push(
        <tr>
          <ClassTimeCols campusId={campusId} time={time} />
        </tr>
      )
    }
  }

  return (
    <div class="table-container" style={{ fontSize: '14px' }}>
      <table class="classes data">
        <thead>
          <tr>
            {headers.map((name) => <th>{name}</th>)}
          </tr>
        </thead>
        <tbody>
          {tableRowEls}
        </tbody>
      </table>
    </div>
  )
}
