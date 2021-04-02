import { h, Component } from 'preact'
import { CSSTransition } from 'react-transition-group'

export default class RouteContainer extends Component {
  constructor(props) {
    super(props)
    this.state = {}
  }

  static getDerivedStateFromProps(newProps, prevState) {
    // preserve path parameters for pages exiting the screen (for when the new URL is different)
    return {
      match: newProps.match ? newProps.match : (prevState.match ? prevState.match : null),
      show: !!newProps.match
    }
  }

  render() {
    const { match, show } = this.state
    const { component: Comp } = this.props

    return (
      <CSSTransition
        in={show}
        // reset the scroll position after the exiting page fades out (200ms)
        onEnter={() => setTimeout(() => document.documentElement.scrollTop = 0, 200)}
        timeout={500}
        classNames="page"
        unmountOnExit
      >
        <div className="page">
          <Comp {...(match ? match : {})} />
        </div>
      </CSSTransition>
    )
  }
}
