import { h, Fragment } from 'preact'
import { useState, useEffect } from 'preact/hooks'
import { route } from 'preact-router'

import { campus, PATH_PREFIX } from '../data'
import { useApi } from '../state'
import TermPicker from '../components/TermPicker'
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
  const [depts, error] = useApi(`/${college}/depts`)
  const colleged = campus.find((cmp) => cmp.id === college)

  const cards = depts ? depts.map(({ id: deptId, name }) => (
    <DeptCard
      id={deptId}
      name={name}
      subinfo='12 courses'
      // setDept={setDept}
      setDept={(dept) => route(`${PATH_PREFIX}/${college}/dept/${dept}`)}
    />
  )) : []

  const view = 'list-view'
  // const view = 'breadcrumb-view'
  // const view = 'card-view'

  const crumbs = [
    { url: '/', name: 'Home' },
    { url: `${PATH_PREFIX}/${college}`, name: colleged.name },
  ]

  return (
    <div class="root">
      {error ? (
        <h3>Not Found! Go back, please</h3>
      ) : (
        <>
          <BreadCrumbs stack={crumbs} />
          <div class="title-container">
            <h1>{colleged.name}</h1>
            <div style="flex: 1"></div>
            <TermPicker />
          </div>
          <h3>Departments</h3>
          <div class={`dept-card-container ${view}`}>{cards}</div>
        </>
      )}
    </div>
  )
}
