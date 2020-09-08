import { h, Fragment } from 'preact'
import { useState, useEffect } from 'preact/hooks'
import { route } from 'preact-router'
import matchSorter from 'match-sorter'

import { campus, PATH_PREFIX } from '../data'
import { useApi } from '../state'
import { CampusNotFound } from '../components/NotFound'
import Header from '../components/Header'
import BreadCrumbs from '../components/BreadCrumbs'

function DeptCard({ id, name, subinfo, setDept }) {
  return (
    <div class="card dept" onClick={() => setDept(id)}>
      <div class="name">{name}</div>
      <div style={{'flex': 1}}></div>
      <div class="more-info">{subinfo}</div>
    </div>
  )
}

export default function CollegePage({ college, setDept }) {
  const colleged = campus.find((cmp) => cmp.id === college)

  if (!colleged) return <CampusNotFound />

  const [depts, error] = useApi(`/${college}/depts`)
  const [query, setQuery] = useState('')
  const [filteredDepts, setFilteredDepts] = useState([])

  useEffect(() => {
    if (depts) {
      setFilteredDepts(
        matchSorter(depts, query, {
          keys: [
            {minRanking: matchSorter.rankings.EQUAL, key: 'id'},
            {minRanking: matchSorter.rankings.MATCHES, key: 'name'}
          ]
        })
      )
    }
  }, [depts, query])

  const postFilterDepts = (query && filteredDepts) || depts
  const cards = postFilterDepts && postFilterDepts.length ? postFilterDepts.map(({ id: deptId, name }) => (
    <DeptCard
      id={deptId}
      name={name}
      subinfo='12 courses'
      setDept={(dept) => route(`${PATH_PREFIX}/${college}/dept/${dept}${window.location.search}`)}
    />
  )) : []

  const view = 'list-view'
  // const view = 'breadcrumb-view'
  // const view = 'card-view'

  const crumbs = [
    { url: '/', name: 'Home' },
    { url: `${PATH_PREFIX}/${college}${window.location.search}`, name: colleged.name },
  ]

  return (
    error == 'NOT_FOUND' ? (
      <CampusNotFound />
    ) : (
      <div class="root">
        <BreadCrumbs stack={crumbs} />
        <div class="title-container">
          <h1>{colleged.name}</h1>
          <div style="flex: 1"></div>
          <Header query={query} setQuery={setQuery}/>
        </div>
        <h3>Departments</h3>
        <div class={`dept-card-container ${view}`}>{cards}</div>
      </div>
    )
  )
}
