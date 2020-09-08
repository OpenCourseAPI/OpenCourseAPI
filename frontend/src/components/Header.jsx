import { h, Fragment } from 'preact'

import TermPicker from './TermPicker'
import DeptSearch from './DeptSearch'

export default function Header(props) {
  const {query, setQuery} = props

  return (
    <>
      <DeptSearch query={query} setQuery={setQuery}/>
      <TermPicker />
    </>
  )
}
