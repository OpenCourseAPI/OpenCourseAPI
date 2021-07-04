import { h } from 'preact'
import { useCallback } from 'preact/hooks'
import { route } from 'preact-router'

export default function Link({ href, children, className, unstyle = false }) {
  const style = unstyle ? { color: 'inherit' } : ''

  const onClick = useCallback((e) => {
    if (e.ctrlKey || e.metaKey || e.altKey || e.shiftKey || e.button !== 0) return;

    e.preventDefault()

    route(href)
  }, [href])

  return (
    <a native className={className} onClick={onClick} href={href} style={style}>
      {children}
    </a>
  )
}
