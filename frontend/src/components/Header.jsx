import { h, Fragment } from 'preact'

import TermPicker from './TermPicker'
import Search from './Search'

export default function Header(props) {
  const {query, setQuery} = props

  return (
    <>
      <Search query={query} setQuery={setQuery}/>
      <TermPicker />
    </>
  )
}
