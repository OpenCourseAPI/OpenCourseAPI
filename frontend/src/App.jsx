import { h } from 'preact'
import { useCallback, useErrorBoundary } from 'preact/hooks'
import { Router, route } from 'preact-router'

import CollegePage from './pages/CollegePage'
import DeptPage from './pages/DeptPage'
import CoursePage from './pages/CoursePage'
import { PageNotFound, CampusNotFound, ErrorPage, Loading } from './components/NotFound'
import { campus, PATH_PREFIX } from './data'
import { TermYear, CampusInfo, useRootApi } from './state'

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
      setCollege={(campus) => route(`${PATH_PREFIX}/${campus}${window.location.search}`)}
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

function WrapCampus({ college, year, term, page: Page, ...props }) {
  const [meta, error, loading] = useRootApi(`/${college}`)

  if (loading) return <Loading />
  if (error == 'NOT_FOUND') return <CampusNotFound />
  else if (error || !meta) return <ErrorPage />

  // year and term come from query parameters
  year = year || meta.current.year
  term = term || meta.current.term

  return (
    <TermYear.Provider value={{term, year}}>
      <CampusInfo.Provider value={meta || {}}>
        <Page college={college} {...props}/>
      </CampusInfo.Provider>
    </TermYear.Provider>
  )
}

export default function App() {
  const [error, resetError] = useErrorBoundary(
    error => console.error(error)
  )

  const onPageChange = useCallback((event) => {
    const urlParts = (url) => url.split('/').length
    if (event.previous && urlParts(event.url) < urlParts(event.previous)) {
      document.body.classList.add('going-back')
    } else {
      document.body.classList.remove('going-back')
    }
  }, [])

  if (error) return <ErrorPage />

  return (
    <Router onChange={onPageChange}>
      <HomePage path="/" />
      <WrapCampus path={`${PATH_PREFIX}/:college`} page={CollegePage}/>
      <WrapCampus path={`${PATH_PREFIX}/:college/dept/:dept`} page={DeptPage}/>
      <WrapCampus path={`${PATH_PREFIX}/:college/dept/:dept/course/:course`} page={CoursePage}/>
      <PageNotFound default />
    </Router>
  )
}
