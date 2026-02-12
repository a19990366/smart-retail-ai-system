import React from 'react'
import ReactDOM from 'react-dom/client'
import { MantineProvider } from '@mantine/core' // 1. 引入 Provider
import '@mantine/core/styles.css' // 2. 引入 Mantine 核心樣式 (這行沒加會跑版)
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    {/* 3. 用 MantineProvider 把 App 包起來 */}
    <MantineProvider>
      <App />
    </MantineProvider>
  </React.StrictMode>,
)