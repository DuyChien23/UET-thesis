"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { ProtectedRoute } from "@/components/protected-route"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { Loader2, Plus, Edit, Users, Shield } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

// Types
type Role = {
  id: string
  name: string
  description: string
  permissions: Permission[]
}

type Permission = {
  id: string
  name: string
  description: string
}

type UserRole = {
  userId: string
  username: string
  email: string
  roles: string[]
}

export default function RolesPage() {
  // State for roles
  const [roles, setRoles] = useState<Role[]>([])
  const [isLoadingRoles, setIsLoadingRoles] = useState(true)
  const [selectedRole, setSelectedRole] = useState<Role | null>(null)
  const [isAddingRole, setIsAddingRole] = useState(false)
  const [newRole, setNewRole] = useState({
    name: "",
    description: "",
    permissions: [] as string[],
  })

  // State for permissions
  const [permissions, setPermissions] = useState<Permission[]>([])
  const [isLoadingPermissions, setIsLoadingPermissions] = useState(true)

  // State for user roles
  const [userRoles, setUserRoles] = useState<UserRole[]>([])
  const [isLoadingUserRoles, setIsLoadingUserRoles] = useState(true)
  const [selectedUser, setSelectedUser] = useState<UserRole | null>(null)

  const { toast } = useToast()

  // Fetch roles
  useEffect(() => {
    const fetchRoles = async () => {
      setIsLoadingRoles(true)
      try {
        // This would be a real API call in production
        // const response = await fetch('/api/roles', {
        //   headers: {
        //     'Authorization': `Bearer ${localStorage.getItem('token')}`
        //   }
        // })

        // Simulate API call
        await new Promise((resolve) => setTimeout(resolve, 1000))

        // Mock data
        const mockPermissions: Permission[] = [
          {
            id: "perm-1",
            name: "user:read",
            description: "View user information",
          },
          {
            id: "perm-2",
            name: "user:write",
            description: "Create and update users",
          },
          {
            id: "perm-3",
            name: "user:delete",
            description: "Delete users",
          },
          {
            id: "perm-4",
            name: "role:read",
            description: "View roles and permissions",
          },
          {
            id: "perm-5",
            name: "role:write",
            description: "Create and update roles",
          },
          {
            id: "perm-6",
            name: "algorithm:read",
            description: "View algorithms and curves",
          },
          {
            id: "perm-7",
            name: "algorithm:write",
            description: "Create and update algorithms",
          },
          {
            id: "perm-8",
            name: "key:read",
            description: "View public keys",
          },
          {
            id: "perm-9",
            name: "key:write",
            description: "Create and update public keys",
          },
          {
            id: "perm-10",
            name: "verification:perform",
            description: "Perform signature verification",
          },
          {
            id: "perm-11",
            name: "system:read",
            description: "View system status",
          },
          {
            id: "perm-12",
            name: "system:write",
            description: "Update system configuration",
          },
        ]

        setPermissions(mockPermissions)
        setIsLoadingPermissions(false)

        const mockRoles: Role[] = [
          {
            id: "role-1",
            name: "admin",
            description: "Full system access",
            permissions: mockPermissions,
          },
          {
            id: "role-2",
            name: "user",
            description: "Regular user with basic permissions",
            permissions: mockPermissions.filter((p) =>
              ["user:read", "key:read", "key:write", "verification:perform"].includes(p.name),
            ),
          },
          {
            id: "role-3",
            name: "auditor",
            description: "Read-only access for auditing",
            permissions: mockPermissions.filter((p) => p.name.endsWith(":read")),
          },
          {
            id: "role-4",
            name: "manager",
            description: "Manage users and view system status",
            permissions: mockPermissions.filter((p) =>
              ["user:read", "user:write", "role:read", "system:read"].includes(p.name),
            ),
          },
        ]

        setRoles(mockRoles)
      } catch (error) {
        toast({
          title: "Error",
          description: "Failed to load roles",
          variant: "destructive",
        })
      } finally {
        setIsLoadingRoles(false)
      }
    }

    fetchRoles()
  }, [toast])

  // Fetch user roles
  useEffect(() => {
    const fetchUserRoles = async () => {
      setIsLoadingUserRoles(true)
      try {
        // This would be a real API call in production
        // const response = await fetch('/api/users?with_roles=true', {
        //   headers: {
        //     'Authorization': `Bearer ${localStorage.getItem('token')}`
        //   }
        // })

        // Simulate API call
        await new Promise((resolve) => setTimeout(resolve, 1200))

        // Mock data
        const mockUserRoles: UserRole[] = [
          {
            userId: "user-1",
            username: "admin",
            email: "admin@example.com",
            roles: ["admin", "user"],
          },
          {
            userId: "user-2",
            username: "johndoe",
            email: "john.doe@example.com",
            roles: ["user"],
          },
          {
            userId: "user-3",
            username: "janedoe",
            email: "jane.doe@example.com",
            roles: ["user", "auditor"],
          },
          {
            userId: "user-4",
            username: "bobsmith",
            email: "bob.smith@example.com",
            roles: ["manager"],
          },
          {
            userId: "user-5",
            username: "alicejones",
            email: "alice.jones@example.com",
            roles: ["user"],
          },
        ]

        setUserRoles(mockUserRoles)
      } catch (error) {
        toast({
          title: "Error",
          description: "Failed to load user roles",
          variant: "destructive",
        })
      } finally {
        setIsLoadingUserRoles(false)
      }
    }

    fetchUserRoles()
  }, [toast])

  // Handle adding a new role
  const handleAddRole = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      // This would be a real API call in production
      // const response = await fetch('/api/roles', {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     'Authorization': `Bearer ${localStorage.getItem('token')}`
      //   },
      //   body: JSON.stringify({
      //     name: newRole.name,
      //     description: newRole.description,
      //     permissions: newRole.permissions
      //   })
      // })

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Create a mock new role
      const selectedPermissions = permissions.filter((p) => newRole.permissions.includes(p.id))
      const mockNewRole: Role = {
        id: `role-${Math.random().toString(36).substring(2, 10)}`,
        name: newRole.name,
        description: newRole.description,
        permissions: selectedPermissions,
      }

      setRoles([...roles, mockNewRole])
      setIsAddingRole(false)
      setNewRole({
        name: "",
        description: "",
        permissions: [],
      })

      toast({
        title: "Role Added",
        description: "The role has been added successfully",
        variant: "default",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to add role",
        variant: "destructive",
      })
    }
  }

  // Handle updating a role
  const handleUpdateRole = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedRole) return

    try {
      // This would be a real API call in production
      // const response = await fetch(`/api/roles/${selectedRole.id}`, {
      //   method: 'PUT',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     'Authorization': `Bearer ${localStorage.getItem('token')}`
      //   },
      //   body: JSON.stringify({
      //     name: selectedRole.name,
      //     description: selectedRole.description
      //   })
      // })

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Update local state
      setRoles(roles.map((role) => (role.id === selectedRole.id ? { ...selectedRole } : role)))
      setSelectedRole(null)

      toast({
        title: "Role Updated",
        description: "The role has been updated successfully",
        variant: "default",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update role",
        variant: "destructive",
      })
    }
  }

  // Handle updating role permissions
  const handleUpdateRolePermissions = async (roleId: string, permissionId: string, isChecked: boolean) => {
    try {
      // This would be a real API call in production
      // const method = isChecked ? 'POST' : 'DELETE'
      // const response = await fetch(`/api/roles/${roleId}/permissions/${permissionId}`, {
      //   method,
      //   headers: {
      //     'Authorization': `Bearer ${localStorage.getItem('token')}`
      //   }
      // })

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500))

      // Update local state
      setRoles(
        roles.map((role) => {
          if (role.id === roleId) {
            if (isChecked) {
              // Add permission
              const permissionToAdd = permissions.find((p) => p.id === permissionId)
              if (permissionToAdd && !role.permissions.some((p) => p.id === permissionId)) {
                return {
                  ...role,
                  permissions: [...role.permissions, permissionToAdd],
                }
              }
            } else {
              // Remove permission
              return {
                ...role,
                permissions: role.permissions.filter((p) => p.id !== permissionId),
              }
            }
          }
          return role
        }),
      )

      // If we're editing a role, update the selected role as well
      if (selectedRole && selectedRole.id === roleId) {
        if (isChecked) {
          const permissionToAdd = permissions.find((p) => p.id === permissionId)
          if (permissionToAdd && !selectedRole.permissions.some((p) => p.id === permissionId)) {
            setSelectedRole({
              ...selectedRole,
              permissions: [...selectedRole.permissions, permissionToAdd],
            })
          }
        } else {
          setSelectedRole({
            ...selectedRole,
            permissions: selectedRole.permissions.filter((p) => p.id !== permissionId),
          })
        }
      }

      toast({
        title: isChecked ? "Permission Added" : "Permission Removed",
        description: `The permission has been ${isChecked ? "added to" : "removed from"} the role`,
        variant: "default",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: `Failed to ${isChecked ? "add" : "remove"} permission`,
        variant: "destructive",
      })
    }
  }

  // Handle updating user roles
  const handleUpdateUserRole = async (userId: string, roleName: string, isChecked: boolean) => {
    try {
      // This would be a real API call in production
      // const method = isChecked ? 'POST' : 'DELETE'
      // const response = await fetch(`/api/users/${userId}/roles`, {
      //   method,
      //   headers: {
      //     'Content-Type': 'application/json',
      //     'Authorization': `Bearer ${localStorage.getItem('token')}`
      //   },
      //   body: JSON.stringify({ role_name: roleName })
      // })

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500))

      // Update local state
      setUserRoles(
        userRoles.map((user) => {
          if (user.userId === userId) {
            if (isChecked && !user.roles.includes(roleName)) {
              return {
                ...user,
                roles: [...user.roles, roleName],
              }
            } else if (!isChecked && user.roles.includes(roleName)) {
              return {
                ...user,
                roles: user.roles.filter((r) => r !== roleName),
              }
            }
          }
          return user
        }),
      )

      // If we're editing a user, update the selected user as well
      if (selectedUser && selectedUser.userId === userId) {
        if (isChecked && !selectedUser.roles.includes(roleName)) {
          setSelectedUser({
            ...selectedUser,
            roles: [...selectedUser.roles, roleName],
          })
        } else if (!isChecked && selectedUser.roles.includes(roleName)) {
          setSelectedUser({
            ...selectedUser,
            roles: selectedUser.roles.filter((r) => r !== roleName),
          })
        }
      }

      toast({
        title: isChecked ? "Role Assigned" : "Role Removed",
        description: `The role has been ${isChecked ? "assigned to" : "removed from"} the user`,
        variant: "default",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: `Failed to ${isChecked ? "assign" : "remove"} role`,
        variant: "destructive",
      })
    }
  }

  return (
    <ProtectedRoute adminOnly>
      <div className="container py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold">Role Management</h1>
          <p className="text-muted-foreground">Manage roles, permissions, and user role assignments</p>
        </div>

        <Tabs defaultValue="roles" className="w-full">
          <TabsList className="mb-4">
            <TabsTrigger value="roles">Roles & Permissions</TabsTrigger>
            <TabsTrigger value="user-roles">User Role Assignments</TabsTrigger>
          </TabsList>

          {/* Roles & Permissions Tab */}
          <TabsContent value="roles">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Roles</CardTitle>
                  <CardDescription>Manage system roles and their permissions</CardDescription>
                </div>
                <Dialog open={isAddingRole} onOpenChange={setIsAddingRole}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="mr-2 h-4 w-4" />
                      Add Role
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[550px]">
                    <DialogHeader>
                      <DialogTitle>Add New Role</DialogTitle>
                      <DialogDescription>Create a new role with specific permissions</DialogDescription>
                    </DialogHeader>

                    <form onSubmit={handleAddRole} className="space-y-4 py-4">
                      <div className="space-y-2">
                        <Label htmlFor="name">Role Name</Label>
                        <Input
                          id="name"
                          value={newRole.name}
                          onChange={(e) => setNewRole({ ...newRole, name: e.target.value })}
                          placeholder="e.g., editor"
                          required
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="description">Description</Label>
                        <Textarea
                          id="description"
                          value={newRole.description}
                          onChange={(e) => setNewRole({ ...newRole, description: e.target.value })}
                          placeholder="Describe the role and its purpose"
                          required
                        />
                      </div>

                      <div className="space-y-2">
                        <Label>Permissions</Label>
                        <div className="max-h-[200px] overflow-y-auto border rounded-md p-4">
                          <div className="space-y-2">
                            {permissions.map((permission) => (
                              <div key={permission.id} className="flex items-center space-x-2">
                                <Checkbox
                                  id={`permission-${permission.id}`}
                                  checked={newRole.permissions.includes(permission.id)}
                                  onCheckedChange={(checked) => {
                                    if (checked) {
                                      setNewRole({
                                        ...newRole,
                                        permissions: [...newRole.permissions, permission.id],
                                      })
                                    } else {
                                      setNewRole({
                                        ...newRole,
                                        permissions: newRole.permissions.filter((id) => id !== permission.id),
                                      })
                                    }
                                  }}
                                />
                                <Label
                                  htmlFor={`permission-${permission.id}`}
                                  className="text-sm font-normal cursor-pointer"
                                >
                                  {permission.name} - {permission.description}
                                </Label>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>

                      <DialogFooter>
                        <Button type="button" variant="outline" onClick={() => setIsAddingRole(false)}>
                          Cancel
                        </Button>
                        <Button type="submit">Add Role</Button>
                      </DialogFooter>
                    </form>
                  </DialogContent>
                </Dialog>
              </CardHeader>
              <CardContent>
                {isLoadingRoles ? (
                  <div className="flex justify-center py-8">
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Role Name</TableHead>
                        <TableHead>Description</TableHead>
                        <TableHead>Permissions</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {roles.map((role) => (
                        <TableRow key={role.id}>
                          <TableCell className="font-medium">{role.name}</TableCell>
                          <TableCell>{role.description}</TableCell>
                          <TableCell>
                            <div className="flex flex-wrap gap-1">
                              {role.permissions.length > 3 ? (
                                <>
                                  {role.permissions.slice(0, 3).map((permission) => (
                                    <Badge key={permission.id} variant="outline" className="bg-primary/10">
                                      {permission.name}
                                    </Badge>
                                  ))}
                                  <Badge variant="outline">+{role.permissions.length - 3} more</Badge>
                                </>
                              ) : (
                                role.permissions.map((permission) => (
                                  <Badge key={permission.id} variant="outline" className="bg-primary/10">
                                    {permission.name}
                                  </Badge>
                                ))
                              )}
                            </div>
                          </TableCell>
                          <TableCell className="text-right">
                            <Button variant="ghost" size="icon" onClick={() => setSelectedRole(role)} title="Edit Role">
                              <Edit className="h-4 w-4" />
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* User Role Assignments Tab */}
          <TabsContent value="user-roles">
            <Card>
              <CardHeader>
                <CardTitle>User Role Assignments</CardTitle>
                <CardDescription>Manage which roles are assigned to each user</CardDescription>
              </CardHeader>
              <CardContent>
                {isLoadingUserRoles ? (
                  <div className="flex justify-center py-8">
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Username</TableHead>
                        <TableHead>Email</TableHead>
                        <TableHead>Assigned Roles</TableHead>
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {userRoles.map((user) => (
                        <TableRow key={user.userId}>
                          <TableCell className="font-medium">{user.username}</TableCell>
                          <TableCell>{user.email}</TableCell>
                          <TableCell>
                            <div className="flex flex-wrap gap-1">
                              {user.roles.map((role) => (
                                <Badge key={role} variant="outline" className="bg-primary/10">
                                  {role}
                                </Badge>
                              ))}
                            </div>
                          </TableCell>
                          <TableCell>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => setSelectedUser(user)}
                              className="flex items-center gap-1"
                            >
                              <Shield className="h-4 w-4" />
                              Manage Roles
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Edit Role Dialog */}
        {selectedRole && (
          <Dialog open={!!selectedRole} onOpenChange={(open) => !open && setSelectedRole(null)}>
            <DialogContent className="sm:max-w-[550px]">
              <DialogHeader>
                <DialogTitle>Edit Role: {selectedRole.name}</DialogTitle>
                <DialogDescription>Update role details and permissions</DialogDescription>
              </DialogHeader>

              <form onSubmit={handleUpdateRole} className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="editName">Role Name</Label>
                  <Input
                    id="editName"
                    value={selectedRole.name}
                    onChange={(e) => setSelectedRole({ ...selectedRole, name: e.target.value })}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="editDescription">Description</Label>
                  <Textarea
                    id="editDescription"
                    value={selectedRole.description}
                    onChange={(e) => setSelectedRole({ ...selectedRole, description: e.target.value })}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label>Permissions</Label>
                  <div className="max-h-[200px] overflow-y-auto border rounded-md p-4">
                    <div className="space-y-2">
                      {permissions.map((permission) => (
                        <div key={permission.id} className="flex items-center space-x-2">
                          <Checkbox
                            id={`edit-permission-${permission.id}`}
                            checked={selectedRole.permissions.some((p) => p.id === permission.id)}
                            onCheckedChange={(checked) => {
                              handleUpdateRolePermissions(selectedRole.id, permission.id, !!checked)
                            }}
                          />
                          <Label
                            htmlFor={`edit-permission-${permission.id}`}
                            className="text-sm font-normal cursor-pointer"
                          >
                            {permission.name} - {permission.description}
                          </Label>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <DialogFooter>
                  <Button type="button" variant="outline" onClick={() => setSelectedRole(null)}>
                    Cancel
                  </Button>
                  <Button type="submit">Update Role</Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        )}

        {/* Edit User Roles Dialog */}
        {selectedUser && (
          <Dialog open={!!selectedUser} onOpenChange={(open) => !open && setSelectedUser(null)}>
            <DialogContent className="sm:max-w-[550px]">
              <DialogHeader>
                <DialogTitle>Manage Roles for {selectedUser.username}</DialogTitle>
                <DialogDescription>Assign or remove roles for this user</DialogDescription>
              </DialogHeader>

              <div className="py-4">
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">{selectedUser.email}</span>
                  </div>

                  <div className="space-y-2">
                    <Label>Assigned Roles</Label>
                    <div className="border rounded-md p-4">
                      <div className="space-y-2">
                        {roles.map((role) => (
                          <div key={role.id} className="flex items-center space-x-2">
                            <Checkbox
                              id={`user-role-${role.id}`}
                              checked={selectedUser.roles.includes(role.name)}
                              onCheckedChange={(checked) => {
                                handleUpdateUserRole(selectedUser.userId, role.name, !!checked)
                              }}
                            />
                            <Label htmlFor={`user-role-${role.id}`} className="text-sm font-normal cursor-pointer">
                              <span className="font-medium">{role.name}</span> - {role.description}
                            </Label>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <DialogFooter>
                <Button variant="outline" onClick={() => setSelectedUser(null)}>
                  Close
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        )}
      </div>
    </ProtectedRoute>
  )
}
