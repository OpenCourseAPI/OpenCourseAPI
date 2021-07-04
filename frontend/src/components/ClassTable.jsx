import { h, Fragment } from 'preact'

const replaceTBA = (text) => (
  text === 'TBA'
    ? (
      <span class="none">(none)</span>
    )
    : text
)

function ClassTimeCols({ time }) {
  const timeString = time.start_time == 'TBA'
    ? replaceTBA('TBA')
    : `${time.start_time || '?'} - ${time.end_time || '?'}`

  const instructors = (time.instructor || []).join(', ')

  // const instructors = (time.instructor || [])
  //   .map(({ full_name, display_name, email }, index, arr) => {
  //     let name = display_name || full_name

  //     if (index < arr.length - 1) {
  //       name += ', '
  //     }

  //     return email ? <a href={`mailto:${email}`} title={email}>{name}</a> : <span>{name}</span>
  //   })
  //   .flat()

  return (
    <>
      <td>{instructors || '?'}</td>
      <td>{replaceTBA(time.days || '?')}</td>
      <td>{timeString || '?'}</td>
      <td>{time.location || '?'}</td>
    </>
  )
}

export default function ClassesTable({ headers, classes, getClassColumns }) {
  if (!classes) return <></>

  const tableRowEls = []

  for (const section of classes) {
    const numRows = section.times.length || 1
    const tableCols = getClassColumns(section)

    tableRowEls.push(
      <tr>
        {tableCols.map((name) => <td rowspan={numRows}>{name}</td>)}
        <ClassTimeCols time={section.times[0] || {}} />
      </tr>
    )

    for (const time of section.times.slice(1)) {
      if (!time) continue
      tableRowEls.push(
        <tr>
          <ClassTimeCols time={time} />
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
