import { h, Fragment } from 'preact'
import { useCallback, useEffect, useErrorBoundary, useState } from 'preact/hooks'
import { Router, exec, getCurrentUrl, subscribers } from 'preact-router'
import Match from 'preact-router/match';

import CollegePage from './pages/CollegePage'
import DeptPage from './pages/DeptPage'
import CoursePage from './pages/CoursePage'
import HomePage from './pages/HomePage'
import RouteContainer from './components/RouteContainer'
import { PageNotFound, CampusNotFound, ErrorPage, Loading } from './components/NotFound'
import { PATH_PREFIX } from './data'
import { TermYear, CampusInfo, useRootApi } from './state'

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
        <Page college={college} {...props} />
      </CampusInfo.Provider>
    </TermYear.Provider>
  )
}

const routes = {
  '/': (props) => <HomePage {...props} />,
  [`${PATH_PREFIX}/:college`]: (props) => (
    <WrapCampus {...props} page={CollegePage}/>
  ),
  [`${PATH_PREFIX}/:college/dept/:dept`]: (props) => (
    <WrapCampus {...props} page={DeptPage}/>
  ),
  [`${PATH_PREFIX}/:college/dept/:dept/course/:course`]: (props) => (
    <WrapCampus {...props} page={CoursePage}/>
  ),
}

export default function App() {
  const [error, resetError] = useErrorBoundary(
    error => console.error(error)
  )

  const getRouteMatches = () => (
    Object.entries(routes)
      .map(([path, component]) => [
        path,
        component,
        exec(getCurrentUrl(), path, {})
      ])
  )

  const [routeMatches, setRouteMatches] = useState(getRouteMatches)
  const routeAlreadyMatched = routeMatches.some(([path, component, matches]) => matches !== false)

  const onPageChange = useCallback((event) => {
    const urlParts = (url) => url.split('/').length
    if (event.previous && urlParts(event.url) < urlParts(event.previous)) {
      document.body.classList.add('going-back')
    } else {
      document.body.classList.remove('going-back')
    }
    setRouteMatches(getRouteMatches())
  }, [])

  if (error) return <ErrorPage />

  return (
    <Router onChange={onPageChange}>
      <Fragment default>
        {routeMatches.map(([path, Component, matches]) => (
          <RouteContainer
            component={Component}
            match={matches}
          />
        ))}
        <RouteContainer
          component={() => <PageNotFound />}
          match={!routeAlreadyMatched}
        />
      </Fragment>
    </Router>
  )
}
