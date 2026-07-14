import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import './App.css'

type ChecklistItem = {
  id: number
  title: string
  completed: boolean
  todo_id: number
}

type Todo = {
  id: number
  title: string
  description: string | null
  completed: boolean
  folder_id: number | null
  checklist_items: ChecklistItem[]
}

type Folder = {
  id: number
  name: string
  owner_id: number
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
  const [isRegistering, setIsRegistering] = useState(false)
  const [todos, setTodos] = useState<Todo[]>([])
  const [message, setMessage] = useState('')

  // Folder states
  const [folders, setFolders] = useState<Folder[]>([])
  const [selectedFolderId, setSelectedFolderId] = useState<number | null>(null)
  const [newFolderName, setNewFolderName] = useState('')
  const [editingFolderId, setEditingFolderId] = useState<number | null>(null)
  const [editFolderName, setEditFolderName] = useState('')

  // Task creation states
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')

  // Detail panel states
  const [selectedTodoId, setSelectedTodoId] = useState<number | null>(null)
  const [editTitle, setEditTitle] = useState('')
  const [editDescription, setEditDescription] = useState('')
  const [newSubtaskTitle, setNewSubtaskTitle] = useState('')
  const [detailSaveStatus, setDetailSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle')

  const selectedTodo = todos.find((t) => t.id === selectedTodoId)

  // Fetch initial todos and folders
  useEffect(() => {
    if (!token) return

    fetch(`${API_BASE_URL}/todos`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(async (response) => {
        if (!response.ok) throw new Error()
        return response.json()
      })
      .then((data) => setTodos(data))
      .catch(() => setMessage('Unable to load tasks'))

    fetch(`${API_BASE_URL}/folders`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(async (response) => {
        if (!response.ok) throw new Error()
        return response.json()
      })
      .then((data) => setFolders(data))
      .catch(() => setMessage('Unable to load folders'))
  }, [token])

  // Sync editing text inside detail pane when selection changes
  useEffect(() => {
    if (selectedTodo) {
      setEditTitle(selectedTodo.title)
      setEditDescription(selectedTodo.description || '')
      setDetailSaveStatus('idle')
    } else {
      setEditTitle('')
      setEditDescription('')
    }
  }, [selectedTodoId])

  async function handleAuth(event: FormEvent) {
    event.preventDefault()
    setMessage('')
    
    const endpoint = isRegistering ? '/register' : '/login'
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })

    const data = await response.json()
    if (!response.ok) {
      setMessage(data.detail || `${isRegistering ? 'Registration' : 'Login'} failed`)
      return
    }

    if (isRegistering) {
      setMessage('Account registered! Please sign in.')
      setIsRegistering(false)
    } else {
      const authData = data as AuthResponse
      localStorage.setItem('token', authData.access_token)
      setToken(authData.access_token)
      setMessage('Logged in successfully')
    }
  }

  function handleLogout() {
    localStorage.removeItem('token')
    setToken(null)
    setTodos([])
    setFolders([])
    setSelectedFolderId(null)
    setSelectedTodoId(null)
    setMessage('Logged out')
  }

  // Folder actions
  async function handleCreateFolder(event: FormEvent) {
    event.preventDefault()
    if (!token || !newFolderName.trim()) return

    const response = await fetch(`${API_BASE_URL}/folders`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ name: newFolderName }),
    })

    if (!response.ok) {
      setMessage('Unable to create folder')
      return
    }

    const folder = (await response.json()) as Folder
    setFolders((current) => [...current, folder])
    setSelectedFolderId(folder.id)
    setNewFolderName('')
  }

  async function handleRenameFolder(folderId: number) {
    if (!token || !editFolderName.trim()) return

    const response = await fetch(`${API_BASE_URL}/folders/${folderId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ name: editFolderName }),
    })

    if (!response.ok) {
      setMessage('Unable to rename folder')
      return
    }

    const updated = (await response.json()) as Folder
    setFolders((current) => current.map((f) => (f.id === folderId ? updated : f)))
    setEditingFolderId(null)
  }

  async function handleDeleteFolder(folderId: number) {
    if (!token) return
    if (!confirm('Are you sure you want to delete this folder and all tasks inside it?')) return

    const response = await fetch(`${API_BASE_URL}/folders/${folderId}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      setMessage('Unable to delete folder')
      return
    }

    setFolders((current) => current.filter((f) => f.id !== folderId))
    setTodos((current) => current.filter((t) => t.folder_id !== folderId))
    if (selectedFolderId === folderId) {
      setSelectedFolderId(null)
    }
    setSelectedTodoId(null)
  }

  // Todo / Task actions
  async function handleCreateTodo(event: FormEvent) {
    event.preventDefault()
    if (!token || !title.trim()) return

    const response = await fetch(`${API_BASE_URL}/todos`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        title,
        description: description || null,
        completed: false,
        folder_id: selectedFolderId,
      }),
    })

    if (!response.ok) {
      setMessage('Unable to create task')
      return
    }

    const newTodo = (await response.json()) as Todo
    setTodos((current) => [newTodo, ...current])
    setTitle('')
    setDescription('')
  }

  async function handleToggleComplete(todo: Todo) {
    if (!token) return
    const response = await fetch(`${API_BASE_URL}/todos/${todo.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ completed: !todo.completed }),
    })

    if (!response.ok) {
      setMessage('Unable to update task status')
      return
    }

    const updatedTodo = (await response.json()) as Todo
    setTodos((current) => current.map((t) => (t.id === todo.id ? { ...t, completed: updatedTodo.completed } : t)))
  }

  async function handleDeleteTodo(id: number) {
    if (!token) return
    const response = await fetch(`${API_BASE_URL}/todos/${id}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      setMessage('Unable to delete task')
      return
    }

    setTodos((current) => current.filter((t) => t.id !== id))
    if (selectedTodoId === id) {
      setSelectedTodoId(null)
    }
  }

  async function handleSaveDetails(todoId: number) {
    if (!token) return
    setDetailSaveStatus('saving')

    const response = await fetch(`${API_BASE_URL}/todos/${todoId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ title: editTitle, description: editDescription || null }),
    })

    if (!response.ok) {
      setDetailSaveStatus('error')
      return
    }

    const updatedTodo = (await response.json()) as Todo
    setTodos((current) =>
      current.map((t) =>
        t.id === todoId
          ? { ...t, title: updatedTodo.title, description: updatedTodo.description }
          : t
      )
    )
    setDetailSaveStatus('saved')
  }

  // Checklist actions
  async function handleCreateChecklistItem(event: FormEvent) {
    event.preventDefault()
    if (!token || !selectedTodoId || !newSubtaskTitle.trim()) return

    const response = await fetch(`${API_BASE_URL}/todos/${selectedTodoId}/checklist`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ title: newSubtaskTitle, completed: false }),
    })

    if (!response.ok) {
      setMessage('Unable to add subtask')
      return
    }

    const newItem = (await response.json()) as ChecklistItem
    setTodos((current) =>
      current.map((t) =>
        t.id === selectedTodoId
          ? { ...t, checklist_items: [...(t.checklist_items || []), newItem] }
          : t
      )
    )
    setNewSubtaskTitle('')
  }

  async function handleToggleChecklistItem(todoId: number, item: ChecklistItem) {
    if (!token) return

    const response = await fetch(`${API_BASE_URL}/todos/${todoId}/checklist/${item.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ completed: !item.completed }),
    })

    if (!response.ok) {
      setMessage('Unable to update subtask')
      return
    }

    const updatedItem = (await response.json()) as ChecklistItem
    setTodos((current) =>
      current.map((t) =>
        t.id === todoId
          ? {
              ...t,
              checklist_items: t.checklist_items.map((i) =>
                i.id === item.id ? updatedItem : i
              ),
            }
          : t
      )
    )
  }

  async function handleDeleteChecklistItem(todoId: number, itemId: number) {
    if (!token) return

    const response = await fetch(`${API_BASE_URL}/todos/${todoId}/checklist/${itemId}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      setMessage('Unable to delete subtask')
      return
    }

    setTodos((current) =>
      current.map((t) =>
        t.id === todoId
          ? {
              ...t,
              checklist_items: t.checklist_items.filter((i) => i.id !== itemId),
            }
          : t
      )
    )
  }

  // Filter tasks based on selection
  const filteredTodos = todos.filter((todo) => todo.folder_id === selectedFolderId)

  return (
    <div className="app-shell">
      {message ? (
        <div className="global-message" onClick={() => setMessage('')}>
          <span>{message}</span>
          <button className="close-msg">×</button>
        </div>
      ) : null}

      {!token ? (
        <div className="auth-container">
          <div className="auth-card">
            <div className="auth-brand">📁 TaskGroup</div>
            <h2>{isRegistering ? 'Create Account' : 'Welcome Back'}</h2>
            <p className="auth-subtitle">
              {isRegistering ? 'Register below to start organizing tasks' : 'Sign in to access your folders and checklist items'}
            </p>
            <form onSubmit={handleAuth} className="auth-form">
              <div className="form-group">
                <label>Email Address</label>
                <input
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="name@example.com"
                  type="email"
                  required
                />
              </div>
              <div className="form-group">
                <label>Password</label>
                <input
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="••••••••"
                  type="password"
                  required
                />
              </div>
              <button type="submit" className="auth-btn">
                {isRegistering ? 'Sign up' : 'Sign in'}
              </button>
            </form>
            <div className="auth-toggle">
              {isRegistering ? 'Already have an account?' : "Don't have an account?"}{' '}
              <button onClick={() => setIsRegistering(!isRegistering)} className="toggle-link-btn">
                {isRegistering ? 'Sign in' : 'Register now'}
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="dashboard-container">
          {/* 1. SIDEBAR */}
          <div className="sidebar">
            <div className="sidebar-header">
              <div className="logo">📁 TaskGroup</div>
            </div>

            <div className="sidebar-section">
              <button
                className={`folder-btn-row ${selectedFolderId === null ? 'active' : ''}`}
                onClick={() => {
                  setSelectedFolderId(null)
                  setSelectedTodoId(null)
                }}
              >
                <span className="icon">📂</span>
                <span className="name">All Tasks</span>
              </button>
            </div>

            <div className="sidebar-section">
              <div className="section-title">FOLDERS</div>
              <div className="folder-list">
                {folders.map((folder) => (
                  <div
                    key={folder.id}
                    className={`folder-item-container ${selectedFolderId === folder.id ? 'active' : ''}`}
                  >
                    {editingFolderId === folder.id ? (
                      <form
                        onSubmit={(e) => {
                          e.preventDefault()
                          handleRenameFolder(folder.id)
                        }}
                        className="folder-rename-form"
                      >
                        <input
                          value={editFolderName}
                          onChange={(e) => setEditFolderName(e.target.value)}
                          autoFocus
                          className="folder-rename-input"
                        />
                        <button type="submit" className="save-folder-btn">✓</button>
                        <button type="button" onClick={() => setEditingFolderId(null)} className="cancel-folder-btn">✗</button>
                      </form>
                    ) : (
                      <>
                        <button
                          className="folder-item-btn"
                          onClick={() => {
                            setSelectedFolderId(folder.id)
                            setSelectedTodoId(null)
                          }}
                        >
                          <span className="icon">📁</span>
                          <span className="name">{folder.name}</span>
                        </button>
                        <div className="folder-actions">
                          <button
                            onClick={() => {
                              setEditingFolderId(folder.id)
                              setEditFolderName(folder.name)
                            }}
                            className="folder-action-btn"
                            title="Rename folder"
                          >
                            ✏️
                          </button>
                          <button
                            onClick={() => handleDeleteFolder(folder.id)}
                            className="folder-action-btn delete"
                            title="Delete folder"
                          >
                            🗑️
                          </button>
                        </div>
                      </>
                    )}
                  </div>
                ))}
              </div>

              <form onSubmit={handleCreateFolder} className="new-folder-form">
                <input
                  placeholder="+ Create folder..."
                  value={newFolderName}
                  onChange={(e) => setNewFolderName(e.target.value)}
                  className="new-folder-input"
                />
              </form>
            </div>

            <div className="sidebar-footer">
              <button onClick={handleLogout} className="logout-btn">
                🚪 Sign out
              </button>
            </div>
          </div>

          {/* 2. MAIN TASK PANEL */}
          <div className="main-panel">
            <div className="panel-header">
              <div className="panel-title-container">
                <h1>{selectedFolderId === null ? 'All Tasks' : folders.find((f) => f.id === selectedFolderId)?.name || 'Folder'}</h1>
                <span className="task-count-badge">{filteredTodos.length} Tasks</span>
              </div>
            </div>

            <form onSubmit={handleCreateTodo} className="task-input-form">
              <input
                placeholder="What task needs addressing?"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="task-title-input"
                required
              />
              <input
                placeholder="Add brief details / tag..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="task-description-input"
              />
              <button type="submit" className="add-task-btn">
                Add Task
              </button>
            </form>

            <div className="task-list">
              {filteredTodos.map((todo) => {
                const totalChecklist = todo.checklist_items?.length || 0
                const completedChecklist = todo.checklist_items?.filter((i) => i.completed).length || 0

                return (
                  <div
                    key={todo.id}
                    className={`task-row ${selectedTodoId === todo.id ? 'selected' : ''} ${todo.completed ? 'completed' : ''}`}
                    onClick={() => setSelectedTodoId(todo.id)}
                  >
                    <div className="task-row-left" onClick={(e) => e.stopPropagation()}>
                      <input
                        type="checkbox"
                        checked={todo.completed}
                        onChange={() => handleToggleComplete(todo)}
                        className="task-row-checkbox"
                      />
                      <div className="task-text-container">
                        <strong className="task-row-title">{todo.title}</strong>
                        {todo.description && <p className="task-row-desc">{todo.description}</p>}
                        {totalChecklist > 0 && (
                          <div className="task-row-subtask-badge">
                            ☑ {completedChecklist}/{totalChecklist} Checklist Items
                          </div>
                        )}
                      </div>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDeleteTodo(todo.id)
                      }}
                      className="task-row-delete-btn"
                      title="Delete task"
                    >
                      🗑️
                    </button>
                  </div>
                )
              })}

              {filteredTodos.length === 0 && (
                <div className="empty-state">
                  <div className="empty-icon">📝</div>
                  <h3>No tasks found</h3>
                  <p>Create a task above to populate this workspace.</p>
                </div>
              )}
            </div>
          </div>

          {/* 3. TASK DETAIL SIDEBAR PANEL */}
          {selectedTodo && (
            <div className="detail-panel">
              <div className="detail-header">
                <h3>Task Details</h3>
                <button onClick={() => setSelectedTodoId(null)} className="close-detail-btn" title="Close panel">
                  ×
                </button>
              </div>

              <div className="detail-body">
                {/* Title */}
                <div className="detail-section">
                  <label className="section-label">TITLE</label>
                  <input
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    onBlur={() => handleSaveDetails(selectedTodo.id)}
                    className="detail-title-field"
                    placeholder="Task Title"
                  />
                </div>

                {/* Note Editor */}
                <div className="detail-section">
                  <label className="section-label">NOTES (AUTOSAVED)</label>
                  <textarea
                    value={editDescription}
                    onChange={(e) => setEditDescription(e.target.value)}
                    onBlur={() => handleSaveDetails(selectedTodo.id)}
                    className="detail-notes-field"
                    placeholder="Add details, notes, links or reminders about this task here..."
                  />
                  {detailSaveStatus === 'saving' && <div className="save-status-msg saving">Saving notes...</div>}
                  {detailSaveStatus === 'saved' && <div className="save-status-msg saved">✓ All changes saved</div>}
                </div>

                {/* Checklist / subtasks */}
                <div className="detail-section">
                  <label className="section-label">CHECKLIST</label>
                  <div className="checklist-wrapper">
                    {selectedTodo.checklist_items?.map((item) => (
                      <div key={item.id} className="checklist-row">
                        <input
                          type="checkbox"
                          checked={item.completed}
                          onChange={() => handleToggleChecklistItem(selectedTodo.id, item)}
                          className="checklist-checkbox"
                        />
                        <span className={`checklist-item-title ${item.completed ? 'completed' : ''}`}>
                          {item.title}
                        </span>
                        <button
                          onClick={() => handleDeleteChecklistItem(selectedTodo.id, item.id)}
                          className="checklist-delete-btn"
                          title="Delete item"
                        >
                          ×
                        </button>
                      </div>
                    ))}

                    <form onSubmit={handleCreateChecklistItem} className="add-checklist-form">
                      <input
                        placeholder="+ Add checklist item..."
                        value={newSubtaskTitle}
                        onChange={(e) => setNewSubtaskTitle(e.target.value)}
                        className="add-checklist-input"
                      />
                    </form>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default App
