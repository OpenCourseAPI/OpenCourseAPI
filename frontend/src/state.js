import { createContext } from 'preact'
import { useState, useEffect, useContext } from 'preact/hooks'

import { API_PATH } from './data'

export const CampusInfo = createContext({})
export const TermYear = createContext({})

export function useRootApi(path) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    (async () => {
      try {
        const response = await fetch(`${API_PATH}${path}`)
        if (response.ok) {
          const json = await response.json()
          setData(json)
          setError(null)
        } else if (response.status === 404) {
          setError('NOT_FOUND')
        } else {
          setError('API_ERROR')
        }
      } catch (err) {
        setError('API_ERROR')
      }

      setLoading(false)
    })()
  }, [path])

  return [data, error, loading]
}

export function useApi(path) {
  const { term, year } = useContext(TermYear)
  return useRootApi(`${path}?year=${year}&quarter=${term}`)
}
