import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { register } from '../api/auth'
import { setAuthToken } from '../auth/token'

function RegisterPage() {
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [age, setAge] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError('')

    const parsedAge = age.trim() === '' ? undefined : Number(age)
    if (parsedAge !== undefined && Number.isNaN(parsedAge)) {
      setError('Возраст должен быть числом')
      return
    }

    const result = await register(name, email, password, parsedAge)
    if (result.error || !result.token) {
      setError(result.error || 'Не удалось зарегистрироваться')
      return
    }

    setAuthToken(result.token)
    navigate('/')
  }

  return (
    <div className="auth-page">
      <form className="auth-form" onSubmit={handleSubmit}>
        <h1>Регистрация</h1>
        <input
          value={name}
          onChange={(event) => setName(event.target.value)}
          placeholder="Имя"
          required
        />
        <input
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="Email"
          required
        />
        <input
          type="number"
          min={0}
          value={age}
          onChange={(event) => setAge(event.target.value)}
          placeholder="Возраст (необязательно)"
        />
        <input
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Пароль"
          required
        />
        {error && <p className="auth-error">{error}</p>}
        <button type="submit">Зарегистрироваться</button>
        <Link to="/login">Уже есть аккаунт</Link>
        <Link to="/">На главную</Link>
      </form>
    </div>
  )
}

export default RegisterPage
