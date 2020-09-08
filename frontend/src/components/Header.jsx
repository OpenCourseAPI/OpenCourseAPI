import { h } from 'preact'

import TermPicker from './TermPicker'
import DeptSearch from './DeptSearch'

export default function Header(props) {
  const {query, setQuery} = props

  return (
    <div class="form-wrapper">
      <DeptSearch query={query} setQuery={setQuery}/>
      <TermPicker />
    </div>
  )
}
