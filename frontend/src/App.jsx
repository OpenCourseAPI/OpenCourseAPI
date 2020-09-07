import { h } from 'preact'
import { useState, useCallback } from 'preact/hooks'
import { Router, route } from 'preact-router';

import CollegePage from './pages/CollegePage'
import DeptPage from './pages/DeptPage'
import CoursePage from './pages/CoursePage'
import { campus, PATH_PREFIX } from './data'
import { TermYear } from './state'

function CampusCard({ id, name, image, setCollege }) {
  return (
    <div class="card campus" onClick={() => setCollege(id)}>
      <div class="image">
        <img src={image} />
      </div>
      <div class="name">{name}</div>
    </div>
  )
}

function HomePage() {
  const campusCards = campus.map(({ id, name, image }) => (
    <CampusCard
      id={id}
      name={name}
      image={image}
      setCollege={(campus) => route(`${PATH_PREFIX}/${campus}`)}
    />
  ))

  return (
    <div class="root">
      <h1>Choose a College</h1>
      <div class="campus-card-container">
        {campusCards}
      </div>
    </div>
  )
}

export default function App() {
  const [[term, year], setTermYear] = useState(['fall', '2020'])
  const onPageChange = useCallback((event) => {
    const urlParts = (url) => url.split('/').length
    if (event.previous && urlParts(event.url) < urlParts(event.previous)) {
      document.body.classList.add('going-back')
    } else {
      document.body.classList.remove('going-back')
    }
  }, [])

  return (
    <TermYear.Provider value={{term, year, setTermYear}}>
      <Router onChange={onPageChange}>
        <HomePage path="/" />
        <CollegePage path={`${PATH_PREFIX}/:id`} />
        <DeptPage path={`${PATH_PREFIX}/:college/dept/:dept`} />
        <CoursePage path={`${PATH_PREFIX}/:college/dept/:dept/course/:course`} />
      </Router>
    </TermYear.Provider>
  )
}
