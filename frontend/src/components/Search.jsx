import { h } from 'preact'
import { useCallback } from 'preact/hooks'

export default function Search({ query, setQuery, placeholder }) {
  const callback = useCallback((event) => {
    setQuery(event.target.value)
  }, [setQuery])

  return (
    <div class="input-wrapper">
      <input
        onInput={callback}
        placeholder={placeholder}
        value={query}
      />
    </div>
  )
}
