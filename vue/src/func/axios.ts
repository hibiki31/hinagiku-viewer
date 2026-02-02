import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_APP_API_HOST || '',
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  },
  responseType: 'json'
})

export default api
