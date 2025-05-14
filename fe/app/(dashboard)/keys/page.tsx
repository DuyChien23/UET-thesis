"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { ProtectedRoute } from "@/components/protected-route"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Loader2, Plus, Key, Copy, Eye, Trash2 } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

type PublicKey = {
  id: string
  algorithmName: string
  curveName: string
  keyData: string
  format: string
  name: string
  status: "active" | "revoked" | "expired"
  createdAt: string
}

export default function KeysPage() {
  const [keys, setKeys] = useState<PublicKey[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [viewKey, setViewKey] = useState<PublicKey | null>(null)
  const [newKey, setNewKey] = useState({
    algorithmId: '',
    curveId: '',
    keyData: '',
    format: 'PEM',
    name: '',
    expiresAt: ''
  })
  const { toast } = useToast()

  useEffect(() => {
    const fetchKeys = async () => {
      setIsLoading(true)
      try {
        // This would be a real API call in production
        // const response = await fetch('/api/users/me/public-keys', {
        //   headers: {
        //     'Authorization': `Bearer ${localStorage.getItem('token')}`
        //   }
        // })
        
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // Mock data
        const mockKeys: PublicKey[] = [
          {
            id: 'key-1',
            algorithmName: 'ECDSA',
            curveName: 'secp256k1',
            keyData: '-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE7Ee8TlNaDqGa+RU9kXYkBbQl8o5X\nY/F7SHKyuMXoDWLzy4bOoYQ+U+JsEqLZQ7pJsQPJG2Xz1JE4UrEJ3RJYdQ==\n-----END PUBLIC KEY-----',
            format: 'PEM',
            name: 'My Primary Key',
            status: 'active',
            createdAt: '2023-01-15T10:30:00Z'
          },
          {
            id: 'key-2',
            algorithmName: 'EdDSA',
            curveName: 'Ed25519',
            keyData: '-----BEGIN PUBLIC KEY-----\nMCowBQYDK2VwAyEAJrQLj5P/89IXsjbY5FeVfP2ue2wVwkMSYiCi8YLXnPc=\n-----END PUBLIC KEY-----',
            format: 'PEM',
            name: 'Backup Key',
            status: 'active',
            createdAt: '2023-03-22T14:15:00Z'
          },
          {
            id: 'key-3',
            algorithmName: 'RSA',
            curveName: 'N/A',
            keyData: '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvwDWGqIpt4hLSf0zdLmE\nXYYOTxGTLnGu2kRx5JbQTmAw8Lm0EjZkP9IPDZr+nCDiTlZWtZCFpL9O7MhaZwOX\n9tUYjVJDKcAvmJRC+wc+LnTZz1vJxERYdQUshlzS5uPJw6XuD8LwS5pTQKnLjQMa\nYnshYQZDYQO6HyS0J3oOD1pu+j9K/+35bDXEg6I0LnYKxUrs1Bk1mVxW6H7cBDMM\nXKK7cJdRJYPLWvOYVVzCIlXBpUjGkGwuFHHm/hNJjpxv9P1q7q0E1QDCzM0H1x8j\nxGzJxYB7UOCnGJLYqT7v1VpAVG0jmLqRRQwk0Y3sPwGl2nWsLQPN4Y5C+5m6r+8i\nzQIDAQAB\n-----END PUBLIC KEY-----',
            format: 'PEM',
            name: 'Legacy RSA Key',
            status: 'expired',
            createdAt: '2022-11-05T09:45:00Z'
          }
        ]
        
        setKeys(mockKeys)
      } catch (error) {
        toast({
          title: 'Error',
          description: 'Failed to load your public keys',
          variant: 'destructive',
        })
      } finally {
        setIsLoading(false)
      }
    }

    fetchKeys()
  }, [toast])

  const handleAddKey = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    try {
      // This would be a real API call in production
      // const response = await fetch('/api/users/me/public-keys', {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     'Authorization': `Bearer ${localStorage.getItem('token')}`
      //   },
      //   body: JSON.stringify(newKey)
      // })
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      // Create a mock new key
      const mockNewKey: PublicKey = {
        id: `key-${Math.random().toString(36).substring(2, 10)}`,
        algorithmName: newKey.algorithmId === 'algo-1' ? 'ECDSA' : newKey.algorithmId === 'algo-2' ? 'RSA' : 'EdDSA',
        curveName: newKey.curveId === 'curve-1' ? 'secp256k1' : newKey.curveId === 'curve-2' ? 'P-256' : 'Ed25519',
        keyData: newKey.keyData,
        format: newKey.format as 'PEM',
        name: newKey.name,
        status: 'active',
        createdAt: new Date().toISOString()
      }
      
      setKeys([...keys, mockNewKey])
      
      // Reset form
      setNewKey({
        algorithmId: '',
        curveId: '',
        keyData: '',
        format: 'PEM',
        name: '',
        expiresAt: ''
      })
      
      toast({
        title: 'Key Added',
        description: 'Your public key has been added successfully',
        variant: 'default',
      })
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to add your public key',
        variant: 'destructive',
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleRevokeKey = async (keyId: string) => {
    try {
      // This would be a real API call in production
      // const response = await fetch(`  => {
    try {
      // This would be a real API call in production
      // const response = await fetch(`/api/public-keys/${keyId}/status`, {
      //   method: 'PATCH',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     'Authorization': `Bearer ${localStorage.getItem('token')}`
      //   },
      //   body: JSON.stringify({ status: 'revoked', reason: 'User requested revocation' })
      // })
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Update local state
      setKeys(keys.map(key => 
        key.id === keyId ? { ...key, status: 'revoked' as const } : key
      ))
      
      toast({
        title: 'Key Revoked',
        description: 'Your public key has been revoked successfully',
        variant: 'default',
      })
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to revoke your public key',
        variant: 'destructive',
      })
    }
  }
\
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast({
      title: 'Copied',
      description: 'Public key copied to clipboard',
      variant: 'default',
    })
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-500">Active</Badge>
      case 'revoked':
        return <Badge variant="destructive">Revoked</Badge>
      case 'expired':
        return <Badge variant="outline" className="text-amber-500 border-amber-500">Expired</Badge>
      default:
        return <Badge variant="outline">{status}</Badge>
    }
  }

  return (
    <ProtectedRoute>
      <div className="container py-8">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold">My Public Keys</h1>
          
          <Dialog>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Add New Key
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[550px]">
              <DialogHeader>
                <DialogTitle>Add New Public Key</DialogTitle>
                <DialogDescription>
                  Register a new public key to use for signature verification
                </DialogDescription>
              </DialogHeader>
              
              <form onSubmit={handleAddKey} className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Key Name</Label>
                  <Input
                    id="name"
                    value={newKey.name}
                    onChange={(e) => setNewKey({ ...newKey, name: e.target.value })}
                    placeholder="My Signing Key"
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="keyData">Public Key</Label>
                  <Textarea
                    id="keyData"
                    value={newKey.keyData}
                    onChange={(e) => setNewKey({ ...newKey, keyData: e.target.value })}
                    placeholder="Paste your public key here"
                    className="min-h-[100px]"
                    required
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="algorithm">Algorithm</Label>
                    <Select 
                      value={newKey.algorithmId} 
                      onValueChange={(value) => setNewKey({ ...newKey, algorithmId: value })}
                      required
                    >
                      <SelectTrigger id="algorithm">
                        <SelectValue placeholder="Select algorithm" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="algo-1">ECDSA</SelectItem>
                        <SelectItem value="algo-2">RSA</SelectItem>
                        <SelectItem value="algo-3">EdDSA</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="curve">Curve</Label>
                    <Select 
                      value={newKey.curveId} 
                      onValueChange={(value) => setNewKey({ ...newKey, curveId: value })}
                      required
                    >
                      <SelectTrigger id="curve">
                        <SelectValue placeholder="Select curve" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="curve-1">secp256k1</SelectItem>
                        <SelectItem value="curve-2">P-256</SelectItem>
                        <SelectItem value="curve-3">P-384</SelectItem>
                        <SelectItem value="curve-4">P-521</SelectItem>
                        <SelectItem value="curve-5">Ed25519</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="format">Format</Label>
                    <Select 
                      value={newKey.format} 
                      onValueChange={(value) => setNewKey({ ...newKey, format: value })}
                      required
                    >
                      <SelectTrigger id="format">
                        <SelectValue placeholder="Select format" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="PEM">PEM</SelectItem>
                        <SelectItem value="DER">DER</SelectItem>
                        <SelectItem value="raw">Raw</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="expiresAt">Expires At (Optional)</Label>
                    <Input
                      id="expiresAt"
                      type="date"
                      value={newKey.expiresAt}
                      onChange={(e) => setNewKey({ ...newKey, expiresAt: e.target.value })}
                    />
                  </div>
                </div>
                
                <DialogFooter>
                  <Button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Adding...
                      </>
                    ) : (
                      'Add Key'
                    )}
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>
        
        <Card>
          <CardHeader>
            <CardTitle>Public Keys</CardTitle>
            <CardDescription>
              Manage your public keys used for signature verification
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
              </div>
            ) : keys.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <Key className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium">No Public Keys</h3>
                <p className="text-muted-foreground mt-1">
                  You haven&apos;t added any public keys yet
                </p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Algorithm</TableHead>
                    <TableHead>Curve</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {keys.map((key) => (
                    <TableRow key={key.id}>
                      <TableCell className="font-medium">{key.name}</TableCell>
                      <TableCell>{key.algorithmName}</TableCell>
                      <TableCell>{key.curveName}</TableCell>
                      <TableCell>{new Date(key.createdAt).toLocaleDateString()}</TableCell>
                      <TableCell>{getStatusBadge(key.status)}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => setViewKey(key)}
                            title="View Key"
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => copyToClipboard(key.keyData)}
                            title="Copy Key"
                          >
                            <Copy className="h-4 w-4" />
                          </Button>
                          {key.status === 'active' && (
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleRevokeKey(key.id)}
                              title="Revoke Key"
                            >
                              <Trash2 className="h-4 w-4 text-destructive" />
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
        
        {/* View Key Dialog */}
        {viewKey && (
          <Dialog open={!!viewKey} onOpenChange={(open) => !open && setViewKey(null)}>
            <DialogContent className="sm:max-w-[550px]">
              <DialogHeader>
                <DialogTitle>{viewKey.name}</DialogTitle>
                <DialogDescription>
                  Public key details
                </DialogDescription>
              </DialogHeader>
              
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label>Public Key</Label>
                  <div className="relative">
                    <Textarea
                      readOnly
                      value={viewKey.keyData}
                      className="font-mono text-xs h-[150px]"
                    />
                    <Button
                      variant="ghost"
                      size="icon"
                      className="absolute top-2 right-2"
                      onClick={() => copyToClipboard(viewKey.keyData)}
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Algorithm</Label>
                    <p className="mt-1">{viewKey.algorithmName}</p>
                  </div>
                  <div>
                    <Label>Curve</Label>
                    <p className="mt-1">{viewKey.curveName}</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Format</Label>
                    <p className="mt-1">{viewKey.format}</p>
                  </div>
                  <div>
                    <Label>Status</Label>
                    <p className="mt-1">{getStatusBadge(viewKey.status)}</p>
                  </div>
                </div>
                
                <div>
                  <Label>Created At</Label>
                  <p className="mt-1">{new Date(viewKey.createdAt).toLocaleString()}</p>
                </div>
              </div>
              
              <DialogFooter>
                <Button variant="outline" onClick={() => setViewKey(null)}>
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
