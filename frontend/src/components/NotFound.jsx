import { h } from 'preact'
import Match from 'preact-router/match'

const Link = Match.Link

export function PageNotFound() {
  return (
    <div class="root">
      <h1>404: Not found</h1>
      <span>Huh, is something supposed to be here? &nbsp;</span>
      <Link href="/">Go back to home</Link>
    </div>
  )
}

export function CampusNotFound() {
  return (
    <div class="root">
      <h1>404: Not found</h1>
      <span>Campus not found! &nbsp;</span>
      <Link href="/">Click here to go back to home.</Link>
    </div>
  )
}

export function DeptNotFound({ backLink }) {
  return (
    <p>
      <span>Whoops, that department was not found for selected term and year. &nbsp;Try changing the term, or </span>
      <Link href={backLink}>click here to go back.</Link>
    </p>
  )
}

export function CourseNotFound({ backLink }) {
  return (
    <p>
      <span>Whoops, that course or department was not found for selected term and year. &nbsp;</span>
      <Link href={backLink}>Click here to go back.</Link>
    </p>
  )
}

export function ErrorPage() {
  return (
    <div class="root">
      <h1>Oh no!</h1>
      <div>
        We hit an error -&nbsp;
        <a href="/">Click here to go back home</a>
      </div>
      <div style={{ marginTop: '1em' }}>
        <i>If you're a dev, you can check the dev console =D</i>
      </div>
    </div>
  )
}
