import { h } from 'preact'

import TermPicker from './TermPicker'

export default function Header({ title }) {
  return (
    <div class="title-container">
      <h1>{title}</h1>
      <div style="flex: 1"></div>
      <TermPicker />
    </div>
  )
}
