function setIntersection(setA, setB) {
  return new Set([...setA].filter(x => setB.has(x)))
}

export { setIntersection }