"use client"

import { useState, useEffect } from "react"
import { ProtectedRoute } from "@/components/protected-route"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Loader2, Search, UserCog, Shield } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

type User = {
  id: string
  username: string
  email: string
  status: "active" | "inactive" | "suspended"
  createdAt: string
  lastLogin?: string
  roles: string[]
}

export default function AdminUsersPage() {
  const [users, setUsers] = useState<User[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [userRoles, setUserRoles] = useState<string[]>([])
  const [availableRoles, setAvailableRoles] = useState<{ id: string; name: string }[]>([])
  const { toast } = useToast()

  useEffect(() => {
    const fetchUsers = async () => {
      setIsLoading(true)
      try {
        // This would be a real API call in production
        // const response = await fetch('/api/users', {
        //   headers: {
        //     'Authorization': `Bearer ${localStorage.getItem('token')}`
        //   }
        // })

        // Simulate API call
        await new Promise((resolve) => setTimeout(resolve, 1000))

        // Mock data
        const mockUsers: User[] = [
          {
            id: "user-1",
            username: "admin",
            email: "admin@example.com",
            status: "active",
            createdAt: "2023-01-10T08:30:00Z",
            lastLogin: "2023-05-15T14:22:00Z",
            roles: ["admin", "user"],
          },
          {
            id: "user-2",
            username: "johndoe",
            email: "john.doe@example.com",
            status: "active",
            createdAt: "2023-02-15T10:45:00Z",
            lastLogin: "2023-05-14T09:15:00Z",
            roles: ["user"],
          },
          {
            id: "user-3",
            username: "janedoe",
            email: "jane.doe@example.com",
            status: "active",
            createdAt: "2023-03-20T14:20:00Z",
            lastLogin: "2023-05-13T16:30:00Z",
            roles: ["user"],
          },
          {
            id: "user-4",
            username: "bobsmith",
            email: "bob.smith@example.com",
            status: "inactive",
            createdAt: "2023-04-05T09:10:00Z",
            lastLogin: "2023-04-25T11:45:00Z",
            roles: ["user"],
          },
          {
            id: "user-5",
            username: "alicejones",
            email: "alice.jones@example.com",
            status: "suspended",
            createdAt: "2023-03-12T16:40:00Z",
            lastLogin: "2023-04-10T08:20:00Z",
            roles: ["user"],
          },
        ]

        setUsers(mockUsers)

        // Mock available roles
        setAvailableRoles([
          { id: "role-1", name: "admin" },
          { id: "role-2", name: "user" },
          { id: "role-3", name: "auditor" },
          { id: "role-4", name: "manager" },
        ])
      } catch (error) {
        toast({
          title: "Error",
          description: "Failed to load users",
          variant: "destructive",
        })
      } finally {
        setIsLoading(false)
      }
    }

    fetchUsers()
  }, [toast])

  const filteredUsers = users.filter((user) => {
    const matchesSearch =
      user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesStatus = statusFilter === "all" || user.status === statusFilter

    return matchesSearch && matchesStatus
  })

  const handleStatusChange = async (userId: string, newStatus: "active" | "inactive" | "suspended") => {
    try {
      // This would be a real API call in production
      // const response = await fetch(`/api/users/${userId}/status`, {
      //   method: 'PATCH',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     'Authorization': `Bearer ${localStorage.getItem('token')}`
      //   },
      //   body: JSON.stringify({ status: newStatus })
      // })

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500))

      // Update local state
      setUsers(users.map((user) => (user.id === userId ? { ...user, status: newStatus } : user)))

      toast({
        title: "Status Updated",
        description: `User status has been updated to ${newStatus}`,
        variant: "default",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update user status",
        variant: "destructive",
      })
    }
  }

  const handleEditUser = (user: User) => {
    setEditingUser(user)
    setUserRoles([...user.roles])
  }

  const handleSaveUserRoles = async () => {
    if (!editingUser) return

    try {
      // This would be a real API call in production
      // const response = await fetch(`/api/users/${editingUser.id}/roles`, {
      //   method: 'PUT',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     'Authorization': `Bearer ${localStorage.getItem('token')}`
      //   },
      //   body: JSON.stringify({ roles: userRoles })
      // })

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Update local state
      setUsers(users.map((user) => (user.id === editingUser.id ? { ...user, roles: userRoles } : user)))

      setEditingUser(null)

      toast({
        title: "Roles Updated",
        description: "User roles have been updated successfully",
        variant: "default",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update user roles",
        variant: "destructive",
      })
    }
  }

  const toggleRole = (role: string) => {
    if (userRoles.includes(role)) {
      setUserRoles(userRoles.filter((r) => r !== role))
    } else {
      setUserRoles([...userRoles, role])
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active":
        return <Badge className="bg-green-500">Active</Badge>
      case "inactive":
        return (
          <Badge variant="outline" className="text-amber-500 border-amber-500">
            Inactive
          </Badge>
        )
      case "suspended":
        return <Badge variant="destructive">Suspended</Badge>
      default:
        return <Badge variant="outline">{status}</Badge>
    }
  }

  return (
    <ProtectedRoute adminOnly>
      <div className="container py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold">User Management</h1>
          <p className="text-muted-foreground">Manage system users and their roles</p>
        </div>

        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Users</CardTitle>
            <CardDescription>View and manage all users in the system</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-6">
              <div className="relative w-full sm:w-96">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search users..."
                  className="pl-8"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>

              <div className="flex items-center gap-2">
                <Label htmlFor="status-filter" className="whitespace-nowrap">
                  Status:
                </Label>
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger id="status-filter" className="w-[130px]">
                    <SelectValue placeholder="Filter by status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All</SelectItem>
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="inactive">Inactive</SelectItem>
                    <SelectItem value="suspended">Suspended</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {isLoading ? (
              <div className="flex justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
              </div>
            ) : filteredUsers.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <UserCog className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium">No Users Found</h3>
                <p className="text-muted-foreground mt-1">No users match your current filters</p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Username</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Roles</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Last Login</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredUsers.map((user) => (
                    <TableRow key={user.id}>
                      <TableCell className="font-medium">{user.username}</TableCell>
                      <TableCell>{user.email}</TableCell>
                      <TableCell>{getStatusBadge(user.status)}</TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1">
                          {user.roles.map((role) => (
                            <Badge key={role} variant="outline" className="bg-primary/10">
                              {role}
                            </Badge>
                          ))}
                        </div>
                      </TableCell>
                      <TableCell>{new Date(user.createdAt).toLocaleDateString()}</TableCell>
                      <TableCell>{user.lastLogin ? new Date(user.lastLogin).toLocaleDateString() : "Never"}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Select
                            onValueChange={(value) => handleStatusChange(user.id, value as any)}
                            defaultValue={user.status}
                          >
                            <SelectTrigger className="w-[110px]">
                              <SelectValue placeholder="Status" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="active">Active</SelectItem>
                              <SelectItem value="inactive">Inactive</SelectItem>
                              <SelectItem value="suspended">Suspended</SelectItem>
                            </SelectContent>
                          </Select>

                          <Button variant="outline" size="icon" onClick={() => handleEditUser(user)}>
                            <Shield className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* Edit User Roles Dialog */}
        {editingUser && (
          <Dialog open={!!editingUser} onOpenChange={(open) => !open && setEditingUser(null)}>
            <DialogContent className="sm:max-w-[500px]">
              <DialogHeader>
                <DialogTitle>Edit User Roles</DialogTitle>
                <DialogDescription>Manage roles for user {editingUser.username}</DialogDescription>
              </DialogHeader>

              <div className="py-4">
                <div className="mb-4">
                  <Label className="text-base">Available Roles</Label>
                  <div className="mt-3 space-y-2">
                    {availableRoles.map((role) => (
                      <div key={role.id} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id={`role-${role.id}`}
                          checked={userRoles.includes(role.name)}
                          onChange={() => toggleRole(role.name)}
                          className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                        />
                        <Label htmlFor={`role-${role.id}`} className="text-sm font-normal">
                          {role.name}
                        </Label>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <DialogFooter>
                <Button variant="outline" onClick={() => setEditingUser(null)}>
                  Cancel
                </Button>
                <Button onClick={handleSaveUserRoles}>Save Changes</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        )}
      </div>
    </ProtectedRoute>
  )
}
