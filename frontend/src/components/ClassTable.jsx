import { h, Fragment } from 'preact'

const replaceTBA = (text) => (
  text === 'TBA'
    ? (
      <span class="none">(none)</span>
    )
    : text
)

export function defaultGetClassTimeColumns(time) {
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

  return [
    instructors || '?',
    replaceTBA(time.days || '?'),
    timeString || '?',
    time.location || '?',
  ]
}

export default function ClassesTable({
  headers,
  classes,
  getClassColumns,
  loading = false,
  placeholders = 0,
  getClassTimeColumns = defaultGetClassTimeColumns
}) {
  const tableRowGroups = []

  if (!loading && classes) {
    for (let i = 0; i < classes.length; i++) {
      const tableRowEls = []
      const section = classes[i]
      const lastSection = i > 0 ? classes[i - 1] : null
      const numRows = section.times.length || 1
      const tableCols = getClassColumns(section, lastSection)
      const timeCols = getClassTimeColumns(section.times[0] || {})

      tableRowEls.push(
        <tr>
          {tableCols.map((name) => <td rowspan={numRows}>{name}</td>)}
          {timeCols.map((name) => <td>{name}</td>)}
        </tr>
      )

      for (const time of section.times.slice(1)) {
        if (!time) continue

        tableRowEls.push(
          <tr>
            {getClassTimeColumns(time).map((name) => <td>{name}</td>)}
          </tr>
        )
      }

      tableRowGroups.push(
        <tbody>
          {tableRowEls}
        </tbody>
      )
    }
  } else {
    const placeholderRows = []

    for (let i = 0; i < placeholders; i++) {
      placeholderRows.push(
        <tr>
          <td colSpan={headers.length + 1}>
            <div class="row-placeholder"></div>
          </td>
        </tr>
      )
    }

    tableRowGroups.push(<tbody>{placeholderRows}</tbody>)
  }

  return (
    <div class="table-container" style={{ fontSize: '14px' }}>
      <table class="classes data">
        <thead>
          <tr>
            {headers.map((name) => <th>{name}</th>)}
          </tr>
        </thead>
        {tableRowGroups}
      </table>
    </div>
  )
}
