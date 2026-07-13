import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import './App.css'

type Todo = {
  id: number
  title: string
  description: string | null
  completed: boolean
}

type AuthResponse = {
  access_token: string
  refresh_token?: string
  token_type: string
}

const API_BASE_URL = 'http://127.0.0.1:8000'

function App() {
  const [email, setEmail] = useState('demo@example.com')
  const [password, setPassword] = useState('demo1234')
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
  const [todos, setTodos] = useState<Todo[]>([])
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [message, setMessage] = useState('')

  useEffect(() => {
    if (!token) return
    fetch(`${API_BASE_URL}/todos`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(async (response) => {
        if (!response.ok) throw new Error('Unable to load todos')
        return response.json()
      })
      .then((data) => setTodos(data))
      .catch(() => setMessage('Unable to load todos'))
  }, [token])

  async function handleAuth(event: FormEvent) {
    event.preventDefault()
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })

    const data = (await response.json()) as AuthResponse
    if (!response.ok) {
      setMessage('Login failed')
      return
    }

    localStorage.setItem('token', data.access_token)
    setToken(data.access_token)
    setMessage('Logged in successfully')
  }

  async function handleCreateTodo(event: FormEvent) {
    event.preventDefault()
    if (!token) return

    const response = await fetch(`${API_BASE_URL}/todos`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ title, description, completed: false }),
    })

    if (!response.ok) {
      setMessage('Unable to create todo')
      return
    }

    const newTodo = (await response.json()) as Todo
    setTodos((current) => [newTodo, ...current])
    setTitle('')
    setDescription('')
    setMessage('Todo created')
  }

  function handleLogout() {
    localStorage.removeItem('token')
    setToken(null)
    setTodos([])
    setMessage('Logged out')
  }

  return (
    <div className="app-shell">
      <h1>Todo App</h1>
      <p>Sign in and manage your todos through the FastAPI backend.</p>

      {message ? <p className="message">{message}</p> : null}

      {!token ? (
        <form onSubmit={handleAuth} className="card">
          <h2>Login</h2>
          <input
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="Email"
          />
          <input
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            type="password"
            placeholder="Password"
          />
          <button type="submit">Sign in</button>
        </form>
      ) : (
        <>
          <div className="card">
            <h2>Create todo</h2>
            <form onSubmit={handleCreateTodo} className="todo-form">
              <input
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                placeholder="Todo title"
              />
              <input
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                placeholder="Description"
              />
              <button type="submit">Add todo</button>
            </form>
          </div>

          <div className="card">
            <div className="toolbar">
              <h2>Your todos</h2>
              <button onClick={handleLogout} type="button">
                Logout
              </button>
            </div>
            {todos.length === 0 ? <p>No todos yet.</p> : null}
            <ul className="todo-list">
              {todos.map((todo) => (
                <li key={todo.id}>
                  <strong>{todo.title}</strong>
                  {todo.description ? <p>{todo.description}</p> : null}
                  <span>{todo.completed ? 'Completed' : 'Pending'}</span>
                </li>
              ))}
            </ul>
          </div>
        </>
      )}
    </div>
  )
}

export default App
