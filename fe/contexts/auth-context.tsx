"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import { useRouter } from "next/navigation"
import { apiService } from "@/lib/api"

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

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  // Check if user has admin role
  const isAdmin = user?.roles?.includes("admin") || false

  useEffect(() => {
    // Check if user is logged in on mount
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem("token")
        if (!token) {
          setIsLoading(false)
          return
        }

        // Fetch current user profile
        try {
          const userData = await apiService.getUserProfile();
          setUser(userData);
        } catch (error) {
          console.error("Failed to get user data:", error);
          localStorage.removeItem("token");
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
      // Call the real API login endpoint
      const response = await apiService.login({ username, password });
      
      // Save token to localStorage
      localStorage.setItem("token", response.access_token);
      
      // Try to get user profile immediately after login to get complete user data
      try {
        const userData = await apiService.getUserProfile();
        setUser({
          id: userData.id,
          username: userData.username,
          email: userData.email,
          roles: userData.roles || ["user"],
        });
      } catch (error) {
        // Fallback to response data if profile fetch fails
        console.error("Failed to fetch user profile after login:", error);
        setUser({
          id: response.id || "",
          username: response.username || username,
          email: response.email || "",
          roles: response.roles || ["user"],
        });
      }
      
      router.push("/dashboard");
    } catch (error) {
      console.error("Login failed:", error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }

  const logout = async () => {
    setIsLoading(true)
    try {
      // Call the real API logout endpoint
      await apiService.logout();
      
      // Clear local storage and state
      localStorage.removeItem("token");
      setUser(null);
      router.push("/login");
    } catch (error) {
      console.error("Logout failed:", error)
      // Even if the API call fails, we should clean up local state
      localStorage.removeItem("token");
      setUser(null);
      router.push("/login");
    } finally {
      setIsLoading(false)
    }
  }

  const register = async (username: string, email: string, password: string) => {
    setIsLoading(true)
    try {
      // Call the real API register endpoint
      await apiService.register({ username, email, password });
      
      // Redirect to login page with registered=true parameter
      router.push("/login?registered=true");
    } catch (error) {
      console.error("Registration failed:", error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

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
