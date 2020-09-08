import { h } from 'preact'
import Match from 'preact-router/match'

const Link = Match.Link

export function CampusNotFound() {
  return (
    <div class="root">
      <h1>404: Not found</h1>
      <p>
        <span>Campus not found! &nbsp;</span>
        <Link href="/">Click here to back.</Link>
      </p>
    </div>
  )
}
