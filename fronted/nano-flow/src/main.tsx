import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App' // 这里引入你刚才写的 App.tsx
import './index.css'    // 这里引入 Tailwind 的样式

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)