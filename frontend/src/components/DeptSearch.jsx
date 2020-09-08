import { h } from 'preact'
import { useCallback } from 'preact/hooks'

export default function DeptSearch(props) {
  const {query, setQuery} = props

  const callback = useCallback((event) => {
    setQuery(event.target.value)
  }, [setQuery])

  return (
    <input class="form-item" onKeyUp={callback} placeholder={'Search...'} value={query} />
  )
}
