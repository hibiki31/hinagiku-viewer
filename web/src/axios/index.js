import Axios from 'axios'

const axios = Axios.create({
  baseURL: process.env.VUE_APP_API_HOST,
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  },
  responseType: 'json'
})

export default axios
