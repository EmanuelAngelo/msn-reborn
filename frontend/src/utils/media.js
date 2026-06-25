export function getMediaBaseUrl() {
  const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'

  if (apiBase.startsWith('/')) {
    return window.location.origin
  }

  return apiBase.replace(/\/api\/?$/, '')
}

export function resolveMediaUrl(url) {
  if (!url) return ''
  if (url.startsWith('blob:')) return url

  if (url.startsWith('http://') || url.startsWith('https://')) {
    try {
      const parsed = new URL(url)
      if (parsed.pathname.startsWith('/media/')) {
        return `${getMediaBaseUrl()}${parsed.pathname}${parsed.search}`
      }
    } catch {
      return url
    }
    return url
  }

  const path = url.startsWith('/') ? url : `/${url}`
  return `${getMediaBaseUrl()}${path}`
}
