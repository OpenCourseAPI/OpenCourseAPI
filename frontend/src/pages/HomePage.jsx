import { h } from 'preact'
import { route } from 'preact-router'
import SelectSearch from 'react-select-search'

import { campus, PATH_PREFIX } from '../data'
import LandingGraphic from '../components/LandingGraphic'

const ChooseInstitute = () => {
  const options = campus.map(({ name, id }) => ({ name, value: id }));

  return (
    <SelectSearch
      placeholder="Choose your institute"
      value=""
      options={options}
      onChange={(option) => route(`${PATH_PREFIX}/${option}`)}
      // TODO: enable search after upgrading library and fixing jsx-runtime issues
      // search
      // emptyMessage="No results"
      // filterOptions={() => (query) => matchSorter(options, query, { keys: ['name'] })}
    />
  )
}

export default function HomePage() {
  return (
    <div class="root landing-container">
      <div class="landing">
        <nav>
          <div>opencourse.dev</div>
          <div class="spacer" />
          <div><a href="https://github.com/OpenCourseAPI/OpenCourseAPI#api-docs">API Docs</a></div>
          <div><a href="https://github.com/OpenCourseAPI">GitHub</a></div>
        </nav>
        <div class="content">
          <div class="intro">
            <div class="intro-info">
              <h1>Find the courses & classes you need</h1>
              <div class="subtext">Get access to courses, classes, professors, and more in an effortless way.</div>
            </div>
            <div class="pictorial">
              <LandingGraphic />
            </div>
          </div>
          <div class="select-container">
            <ChooseInstitute />
          </div>
          <div class="try-it">
            <div class="label">Try: </div>
            {campus.slice(0, 2).map(({ name, id }) => (
              <a class="link" href={`${PATH_PREFIX}/${id}`}>{name}</a>
            ))}
          </div>
        </div>
      </div>
      <footer>
        Built by the <a href="https://github.com/OpenCourseAPI">Open Course API</a> team
      </footer>
    </div>
  )
}
