import { h } from 'preact'
import { useContext, useCallback } from 'preact/hooks'
import { TermYear } from '../state'

const DropdownIcon = <svg version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlnsXlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="0 0 122.88 66.91" style="enable-background:new 0 0 122.88 66.91" xmlSpace="preserve"><g><path d="M11.68,1.95C8.95-0.7,4.6-0.64,1.95,2.08c-2.65,2.72-2.59,7.08,0.13,9.73l54.79,53.13l4.8-4.93l-4.8,4.95 c2.74,2.65,7.1,2.58,9.75-0.15c0.08-0.08,0.15-0.16,0.22-0.24l53.95-52.76c2.73-2.65,2.79-7.01,0.14-9.73 c-2.65-2.72-7.01-2.79-9.73-0.13L61.65,50.41L11.68,1.95L11.68,1.95z"/></g></svg>

export default function TermPicker() {
  const { term, year, setTermYear } = useContext(TermYear)
  const callback = useCallback((event) => {
    const [term, year] = event.target.value.split('-')
    console.log(term, year)
    setTermYear([term, year])
  }, [setTermYear])
  const options = [
    { name: 'Fall 2020', value: 'fall-2020' },
    { name: 'Summer 2020', value: 'summer-2020' },
    { name: 'Spring 2020', value: 'spring-2020' },
    { name: 'Winter 2020', value: 'winter-2020' },
  ]
  return (
    <div>
      <div class="select-wrapper">
        <select onChange={callback} value={`${term}-${year}`}>
          {options.map(({ name, value }) => <option value={value}>{name}</option>)}
        </select>
        {DropdownIcon}
      </div>
    </div>
  )
}