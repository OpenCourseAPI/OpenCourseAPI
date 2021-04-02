import { h } from 'preact'
import { CSSTransition } from 'react-transition-group'

export const Fade = ({ in: inProp, children, duration = 300 }) => {
  return (
    <CSSTransition in={inProp} timeout={duration} classNames="fade" unmountOnExit>
      <div className="fade">
        {children}
      </div>
    </CSSTransition>
  )
}
