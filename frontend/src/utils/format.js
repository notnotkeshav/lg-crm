/**
 * Format a currency value with the specified currency code
 * @param {number} value - The value to format
 * @param {string} currency - The currency code (e.g., 'USD', 'INR')
 * @returns {string} Formatted currency string
 */
export function formatCurrency(value, currency = 'INR') {
  if (!value) return '-'
  
  const formatter = new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })

  return formatter.format(value)
}

/**
 * Format a date string into a localized format
 * @param {string} dateString - The date string to format
 * @param {Object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted date string
 */
export function formatDate(dateString, options = {}) {
  if (!dateString) return '-'

  const defaultOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }

  const formatter = new Intl.DateTimeFormat('en-US', { ...defaultOptions, ...options })
  return formatter.format(new Date(dateString))
}

/**
 * Format a number with specified options
 * @param {number} value - The number to format
 * @param {Object} options - Intl.NumberFormat options
 * @returns {string} Formatted number string
 */
export function formatNumber(value, options = {}) {
  if (value === null || value === undefined) return '-'

  const defaultOptions = {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  }

  const formatter = new Intl.NumberFormat('en-IN', { ...defaultOptions, ...options })
  return formatter.format(value)
}

/**
 * Format a date-time string into a localized format
 * @param {string} dateTimeString - The date-time string to format
 * @param {Object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted date-time string
 */
export function formatDateTime(dateTimeString, options = {}) {
  if (!dateTimeString) return '-'

  const defaultOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }

  const formatter = new Intl.DateTimeFormat('en-US', { ...defaultOptions, ...options })
  return formatter.format(new Date(dateTimeString))
}

/**
 * Format a time duration in milliseconds to human readable format
 * @param {number} duration - Duration in milliseconds
 * @returns {string} Formatted duration string
 */
export function formatDuration(duration) {
  if (!duration) return '-'

  const hours = Math.floor(duration / 3600000)
  const minutes = Math.floor((duration % 3600000) / 60000)
  const seconds = Math.floor((duration % 60000) / 1000)

  const parts = []
  if (hours > 0) parts.push(`${hours}h`)
  if (minutes > 0) parts.push(`${minutes}m`)
  if (seconds > 0 && hours === 0) parts.push(`${seconds}s`)

  return parts.join(' ') || '0s'
}

/**
 * Format a file size in bytes to human readable format
 * @param {number} bytes - Size in bytes
 * @returns {string} Formatted size string
 */
export function formatFileSize(bytes) {
  if (!bytes) return '0 B'

  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let size = bytes
  let unitIndex = 0

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }

  return `${formatNumber(size, { maximumFractionDigits: 1 })} ${units[unitIndex]}`
} 