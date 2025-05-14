"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import { useRouter } from "next/navigation"

type User = {
  id: string
  username: string
  email: string
  roles?: string[]
}

type AuthContextType = {
  user: User | null
  isLoading: boolean
  isAdmin: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

// Mock users for demonstration
const MOCK_USERS = [
  {
    id: "user-1",
    username: "admin",
    email: "admin@example.com",
    password: "admin123",
    roles: ["admin", "user"],
  },
  {
    id: "user-2",
    username: "user",
    email: "user@example.com",
    password: "user123",
    roles: ["user"],
  },
]

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    // Check if user is logged in on mount
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem("token")
        if (!token) {
          setIsLoading(false)
          return
        }

        // For demo purposes, we'll parse the token to get the user
        try {
          const userData = JSON.parse(atob(token.split(".")[1]))
          if (userData && userData.user) {
            setUser(userData.user)
          } else {
            localStorage.removeItem("token")
          }
        } catch (e) {
          localStorage.removeItem("token")
        }
      } catch (error) {
        console.error("Auth check failed:", error)
      } finally {
        setIsLoading(false)
      }
    }

    checkAuth()
  }, [])

  const login = async (username: string, password: string) => {
    setIsLoading(true)
    try {
      // For demo purposes, we'll use mock authentication
      const mockUser = MOCK_USERS.find((u) => u.username === username && u.password === password)

      if (!mockUser) {
        throw new Error("Invalid credentials")
      }

      // Create a simple mock token
      const { password: _, ...userWithoutPassword } = mockUser
      const token = `mock.${btoa(JSON.stringify({ user: userWithoutPassword }))}.token`

      localStorage.setItem("token", token)
      setUser(userWithoutPassword)
      router.push("/dashboard")
    } catch (error) {
      console.error("Login failed:", error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    setIsLoading(true)
    try {
      // Just remove the token for the mock implementation
      localStorage.removeItem("token")
      setUser(null)
      router.push("/login")
    } catch (error) {
      console.error("Logout failed:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const register = async (username: string, email: string, password: string) => {
    setIsLoading(true)
    try {
      // For demo purposes, we'll just redirect to login
      router.push("/login?registered=true")
    } catch (error) {
      console.error("Registration failed:", error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  // Check if user has admin role
  const isAdmin = user?.roles?.includes("admin") || false

  return (
    <AuthContext.Provider value={{ user, isLoading, isAdmin, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
