import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { login } from '../api/auth'
import { setAuthToken } from '../auth/token'

function LoginPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError('')

    const result = await login(email, password)
    if (result.error || !result.token) {
      setError(result.error || 'Не удалось войти')
      return
    }

    setAuthToken(result.token)
    navigate('/')
  }

  return (
    <div className="auth-page">
      <form className="auth-form" onSubmit={handleSubmit}>
        <h1>Вход</h1>
        <input
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="Email"
          required
        />
        <input
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Пароль"
          required
        />
        {error && <p className="auth-error">{error}</p>}
        <button type="submit">Войти</button>
        <Link to="/register">Создать аккаунт</Link>
        <Link to="/">На главную</Link>
      </form>
    </div>
  )
}

export default LoginPage
