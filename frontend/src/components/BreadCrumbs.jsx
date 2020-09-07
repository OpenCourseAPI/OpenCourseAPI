import { h, Fragment } from 'preact'
import Match from 'preact-router/match'

const Link = Match.Link

export default function BreadCrumbs({ stack }) {
  return (
    <nav class="breadcrumbs">
      {stack.map(({ url, name }, index) => (
        <>
          <Link href={url} activeClassName="current">{name}</Link>
          {index < stack.length - 1 ? ' > ' : ''}
        </>
      ))}
    </nav>
  )
}
