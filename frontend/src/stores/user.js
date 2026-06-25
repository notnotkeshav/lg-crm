// import router from '@/router'
// import { createResource } from 'frappe-ui'

// export const userResource = createResource({
//   url: '/api/method/frappe.auth.get_logged_user',
//   // url: 'frappe.auth.get_logged_user',
//   cache: false,
//   onError(error) {
//     if (error && error.exc_type === 'AuthenticationError') {
//       router.push({ name: 'Home' })
//     }
//   },
// })

import router from '@/router'
import { createResource } from 'frappe-ui'

export const userResource = createResource({
  url: '/api/method/frappe.auth.get_logged_user',
  cache: false,
  transform: async (response) => {
    const userId = response.message

    const userRes = await fetch(`/api/resource/User/${userId}`)
    const userJson = await userRes.json()

    console.log('User API response:', userJson)  // 🔍 Debug this

    if (userJson && userJson.data && userJson.data.full_name) {
      return userJson.data.full_name
    } else {
      throw new Error('Failed to get full_name from user data')
    }
  },
  onError(error) {
    if (error && error.exc_type === 'AuthenticationError') {
      router.push({ name: 'Home' })
    } else {
      console.error('Failed to fetch user:', error)
    }
  },
})
