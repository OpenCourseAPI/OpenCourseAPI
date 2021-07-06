import { h, Fragment } from 'preact'
import { useState, useEffect } from 'preact/hooks'
import matchSorter from 'match-sorter'

import { campus, PATH_PREFIX } from '../data'
import { useApi } from '../state'
import { CampusNotFound } from '../components/NotFound'
import Header from '../components/Header'
import Search from '../components/Search'
import BreadCrumbs from '../components/BreadCrumbs'
import Link from '../components/Link'

function DeptCard({ college, dept, name, subinfo }) {
  return (
    <Link
      href={`${PATH_PREFIX}/${college}/dept/${dept}${window.location.search}`}
      className="card dept"
      unstyle
    >
      <div class="name">{name}</div>
      <div style={{'flex': 1}}></div>
      <div class="more-info">{subinfo}</div>
    </Link>
  )
}

export default function CollegePage({ college }) {
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
      college={college}
      dept={deptId}
      name={name}
      subinfo=''
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
        <Header title={colleged.name} />
        <h3>Departments</h3>
        <Search query={query} setQuery={setQuery} placeholder="Filter departments..." />
        <div class={`dept-card-container ${view}`}>{cards}</div>
      </div>
    )
  )
}
