import { h } from 'preact'
import { useCallback } from 'preact/hooks'

export default function DeptSearch(props) {
  const {query, setQuery} = props

  const callback = useCallback((event) => {
    setQuery(event.target.value)
  }, [setQuery])

  return (
    <div class="input-wrapper">
      <input class="form-item" onInput={callback} placeholder={'Search...'} value={query} />
    </div>
  )
}
