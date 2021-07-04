import { h } from 'preact'

import { campus, PATH_PREFIX } from '../data'
import Link from '../components/Link'

function CampusCard({ campus, name, image }) {
  return (
    <Link
      className="card campus"
      href={`${PATH_PREFIX}/${campus}${window.location.search}`}
      unstyle
    >
      <div class="image">
        <img src={image} />
      </div>
      <div class="name">{name}</div>
    </Link>
  )
}

export default function HomePage() {
  const campusCards = campus.map(({ id, name, image }) => (
    <CampusCard
      campus={id}
      name={name}
      image={image}
    />
  ))

  return (
    <div class="root">
      <h1>Choose a College</h1>
      <div class="campus-card-container">
        {campusCards}
      </div>
    </div>
  )
}
