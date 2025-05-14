// @ts-nocheck
/* eslint-disable */
"use client"

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
import { useAuth } from "@/contexts/auth-context"

export default function KeysPage() {
  const [keys, setKeys] = useState([])
  const [algorithms, setAlgorithms] = useState([])
  const [curves, setCurves] = useState([])
  const [filteredCurves, setFilteredCurves] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [viewKey, setViewKey] = useState(null)
  const [isLoadingAlgorithms, setIsLoadingAlgorithms] = useState(false)
  const [isLoadingCurves, setIsLoadingCurves] = useState(false)
  const [newKey, setNewKey] = useState({
    algorithm_name: '',
    curve_name: '',
    key_data: '',
    name: '',
    description: ''
  })
  const { toast } = useToast()
  const { token } = useAuth()
  const [errorMsg, setErrorMsg] = useState(null)
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || ''

  useEffect(() => {
    if (!token) return
    
    const fetchKeys = async () => {
      setIsLoading(true)
      setErrorMsg(null)
      
      try {
        if (!apiUrl) throw new Error("API URL not configured")
        
        const res = await fetch(`${apiUrl}/api/public-keys`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        if (!res.ok) throw new Error(await res.text())
        
        const data = await res.json()
        setKeys(data.keys || [])
      } catch (error) {
        const msg = error.message || "Failed to load keys"
        setErrorMsg(msg)
        toast({
          title: 'Error',
          description: msg,
          variant: 'destructive',
        })
      } finally {
        setIsLoading(false)
      }
    }

    const fetchAlgorithms = async () => {
      setIsLoadingAlgorithms(true)
      
      try {
        if (!apiUrl) throw new Error("API URL not configured")
        
        const res = await fetch(`${apiUrl}/api/algorithms`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        if (!res.ok) throw new Error(await res.text())
        
        const data = await res.json()
        setAlgorithms(data.algorithms || [])
      } catch (error) {
        toast({
          title: 'Error',
          description: 'Failed to load algorithms',
          variant: 'destructive',
        })
      } finally {
        setIsLoadingAlgorithms(false)
      }
    }
    
    fetchKeys()
    fetchAlgorithms()
  }, [token, toast, apiUrl])

  const fetchCurvesByAlgorithm = async (algorithmName) => {
    setIsLoadingCurves(true)
    
    try {
      if (!token) throw new Error("No token found")
      if (!apiUrl) throw new Error("API URL not configured")
      
      const res = await fetch(`${apiUrl}/api/curves?algorithm_name=${algorithmName}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (!res.ok) throw new Error(await res.text())
      
      const data = await res.json()
      setCurves(data.curves || [])
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load curves',
        variant: 'destructive',
      })
      setCurves([])
    } finally {
      setIsLoadingCurves(false)
    }
  }

  const handleAlgorithmChange = async (value) => {
    setNewKey(prev => ({ ...prev, algorithm_name: value, curve_name: '' }))
    await fetchCurvesByAlgorithm(value)
  }

  useEffect(() => {
    if (newKey.algorithm_name && curves.length > 0) {
      const filtered = curves.filter(curve => 
        curve.algorithm_name === newKey.algorithm_name
      )
      
      setFilteredCurves(filtered)
      
      if (filtered.length > 0 && !filtered.some(c => c.name === newKey.curve_name)) {
        setNewKey(prev => ({ ...prev, curve_name: '' }))
      }
    } else {
      setFilteredCurves([])
    }
  }, [newKey.algorithm_name, curves, newKey.curve_name])

  const handleAddKey = async (e) => {
    e.preventDefault()
    setIsSubmitting(true)
    
    try {
      if (!token) throw new Error("No token found")
      if (!apiUrl) throw new Error("API URL not configured")
      
      const res = await fetch(`${apiUrl}/api/public-keys`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          key_data: newKey.key_data,
          algorithm_name: newKey.algorithm_name,
          curve_name: newKey.curve_name,
          name: newKey.name,
          description: newKey.description
        })
      })
      
      if (!res.ok) {
        const errorData = await res.json()
        throw new Error(errorData.detail || 'Failed to add public key')
      }

      setNewKey({
        algorithm_name: '',
        curve_name: '',
        key_data: '',
        name: '',
        description: ''
      })
      
      toast({
        title: 'Key Added',
        description: 'Your public key has been added successfully',
        variant: 'default',
      })
      
      const fetchRes = await fetch(`${apiUrl}/api/public-keys`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (fetchRes.ok) {
        const data = await fetchRes.json()
        setKeys(data.keys || [])
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to add your public key',
        variant: 'destructive',
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDeleteKey = async (keyId) => {
    try {
      if (!token) throw new Error("No token found")
      if (!apiUrl) throw new Error("API URL not configured")
      
      const res = await fetch(`${apiUrl}/api/public-keys/${keyId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (!res.ok) {
        const errorData = await res.json()
        throw new Error(errorData.detail || 'Failed to delete public key')
      }
      
      setKeys(keys.filter(key => key.id !== keyId))
      
      toast({
        title: 'Key Deleted',
        description: 'Your public key has been deleted successfully',
        variant: 'default',
      })
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to delete your public key',
        variant: 'destructive',
      })
    }
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    toast({
      title: 'Copied',
      description: 'Public key copied to clipboard',
      variant: 'default',
    })
  }

  const getStatusBadge = (isActive) => {
    if (!isActive) {
      return <Badge variant="destructive">Disabled</Badge>
    }
    return <Badge variant="default">Active</Badge>
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
                    value={newKey.key_data}
                    onChange={(e) => setNewKey({ ...newKey, key_data: e.target.value })}
                    placeholder="Paste your public key here"
                    className="min-h-[100px]"
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="description">Description (Optional)</Label>
                  <Input
                    id="description"
                    value={newKey.description}
                    onChange={(e) => setNewKey({ ...newKey, description: e.target.value })}
                    placeholder="Key description"
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="algorithm">Algorithm</Label>
                    <Select 
                      value={newKey.algorithm_name} 
                      onValueChange={handleAlgorithmChange}
                      required
                      disabled={isLoadingAlgorithms}
                    >
                      <SelectTrigger id="algorithm">
                        <SelectValue placeholder={isLoadingAlgorithms ? "Loading algorithms..." : "Select algorithm"} />
                      </SelectTrigger>
                      <SelectContent>
                        {algorithms.map((algo) => (
                          <SelectItem key={algo.id} value={algo.name}>
                            {algo.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="curve">Curve</Label>
                    <Select 
                      value={newKey.curve_name} 
                      onValueChange={(value) => setNewKey({ ...newKey, curve_name: value })}
                      disabled={!newKey.algorithm_name || isLoadingCurves}
                    >
                      <SelectTrigger id="curve">
                        <SelectValue placeholder={
                          isLoadingCurves ? "Loading curves..." : 
                          !newKey.algorithm_name ? "Select an algorithm first" : 
                          "Select curve"
                        } />
                      </SelectTrigger>
                      <SelectContent>
                        {filteredCurves.map((curve) => (
                          <SelectItem key={curve.id} value={curve.name}>
                            {curve.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
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
            ) : errorMsg ? (
              <div className="flex flex-col items-center justify-center py-8 text-center text-destructive">
                <p className="mb-2">Error: {errorMsg}</p>
                <Button onClick={() => window.location.reload()}>Retry</Button>
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
                      <TableCell>{key.algorithm_name}</TableCell>
                      <TableCell>{key.curve_name || 'N/A'}</TableCell>
                      <TableCell>{new Date(key.created_at).toLocaleDateString()}</TableCell>
                      <TableCell>{getStatusBadge(key.is_active)}</TableCell>
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
                            onClick={() => copyToClipboard(key.key_data)}
                            title="Copy Key"
                          >
                            <Copy className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleDeleteKey(key.id)}
                            title="Delete Key"
                          >
                            <Trash2 className="h-4 w-4 text-destructive" />
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
                      value={viewKey.key_data}
                      className="font-mono text-xs h-[150px]"
                    />
                    <Button
                      variant="ghost"
                      size="icon"
                      className="absolute top-2 right-2"
                      onClick={() => copyToClipboard(viewKey.key_data)}
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Algorithm</Label>
                    <p className="mt-1">{viewKey.algorithm_name}</p>
                  </div>
                  <div>
                    <Label>Curve</Label>
                    <p className="mt-1">{viewKey.curve_name || 'N/A'}</p>
                  </div>
                </div>
                
                <div>
                  <Label>Status</Label>
                  <p className="mt-1">{getStatusBadge(viewKey.is_active)}</p>
                </div>
                
                {viewKey.description && (
                  <div>
                    <Label>Description</Label>
                    <p className="mt-1">{viewKey.description}</p>
                  </div>
                )}
                
                <div>
                  <Label>Created At</Label>
                  <p className="mt-1">{new Date(viewKey.created_at).toLocaleString()}</p>
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
