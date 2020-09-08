import { createContext } from 'preact'
import { useState, useEffect, useContext } from 'preact/hooks'

import { API_PATH } from './data'

export const CampusInfo = createContext({})
export const TermYear = createContext({})

export function useRootApi(path) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(async () => {
    const response = await fetch(`${API_PATH}${path}`)
    const json = await response.json()

    if (response.ok) {
      setData(json)
    } else if (response.status === 404) {
      setError('NOT_FOUND')
    }
  }, [path])

  return [data, error]
}

export function useApi(path) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const {term, year} = useContext(TermYear)

  useEffect(async () => {
    const response = await fetch(`${API_PATH}${path}?year=${year}&quarter=${term}`)
    const json = await response.json()

    if (response.ok) {
      setData(json)
      setError(null)
    } else if (response.status === 404) {
      setError('NOT_FOUND')
    }
  }, [term, year])

  return [data, error]
}
