export const formatDate = (str, opt) => new Date(Date.parse(str)).toLocaleDateString('en-US', opt)

export function setIntersection(setA, setB) {
  return new Set([...setA].filter(x => setB.has(x)))
}
