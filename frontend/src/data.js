export const STATIC_PATH = import.meta.env.SNOWPACK_PUBLIC_STATIC_PATH || ''
export const API_PATH = import.meta.env.SNOWPACK_PUBLIC_API_URL || ''
export const PATH_PREFIX = import.meta.env.SNOWPACK_PUBLIC_PATH_PREFIX || '/explore'

export const campus = [
  { id: 'fh', name: 'Foothill College', image: `${STATIC_PATH}/img/logo-foothill.png` },
  { id: 'da', name: 'De Anza College', image: `${STATIC_PATH}/img/logo-deanza.png` },
  { id: 'wv', name: 'West Valley College', image: `${STATIC_PATH}/img/logo-westvalley.png` },
  { id: 'mc', name: 'Mission College', image: `${STATIC_PATH}/img/logo-mission.png` },
]
