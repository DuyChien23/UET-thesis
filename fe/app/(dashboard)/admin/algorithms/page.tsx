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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Loader2, Plus, Edit, Trash2, Info } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

// Types
type Algorithm = {
  id: string
  name: string
  type: "ECDSA" | "RSA" | "EdDSA" | string
  description: string
  createdAt: string
}

type Curve = {
  id: string
  name: string
  algorithmId: string
  algorithmName: string
  parameters: Record<string, any>
  description: string
  status: "enabled" | "disabled"
  createdAt: string
}

export default function AlgorithmsPage() {
  // State for algorithms
  const [algorithms, setAlgorithms] = useState<Algorithm[]>([])
  const [isLoadingAlgorithms, setIsLoadingAlgorithms] = useState(true)
  const [selectedAlgorithm, setSelectedAlgorithm] = useState<Algorithm | null>(null)
  const [isAddingAlgorithm, setIsAddingAlgorithm] = useState(false)
  const [newAlgorithm, setNewAlgorithm] = useState({
    name: "",
    type: "",
    description: "",
  })

  // State for curves
  const [curves, setCurves] = useState<Curve[]>([])
  const [isLoadingCurves, setIsLoadingCurves] = useState(true)
  const [selectedCurve, setSelectedCurve] = useState<Curve | null>(null)
  const [isAddingCurve, setIsAddingCurve] = useState(false)
  const [newCurve, setNewCurve] = useState({
    name: "",
    algorithmId: "",
    parameters: "",
    description: "",
  })

  const { toast } = useToast()

  // Fetch algorithms
  useEffect(() => {
    const fetchAlgorithms = async () => {
      setIsLoadingAlgorithms(true)
      try {
        // This would be a real API call in production
        // const response = await fetch('/api/algorithms', {
        //   headers: {
        //     'Authorization': `Bearer ${localStorage.getItem('token')}`
        //   }
        // })

        // Simulate API call
        await new Promise((resolve) => setTimeout(resolve, 1000))

        // Mock data
        const mockAlgorithms: Algorithm[] = [
          {
            id: "algo-1",
            name: "ECDSA",
            type: "ECDSA",
            description: "Elliptic Curve Digital Signature Algorithm",
            createdAt: "2023-01-15T10:30:00Z",
          },
          {
            id: "algo-2",
            name: "RSA",
            type: "RSA",
            description: "Rivest–Shamir–Adleman algorithm",
            createdAt: "2023-01-15T10:35:00Z",
          },
          {
            id: "algo-3",
            name: "EdDSA",
            type: "EdDSA",
            description: "Edwards-curve Digital Signature Algorithm",
            createdAt: "2023-01-15T10:40:00Z",
          },
        ]

        setAlgorithms(mockAlgorithms)
      } catch (error) {
        toast({
          title: "Error",
          description: "Failed to load algorithms",
          variant: "destructive",
        })
      } finally {
        setIsLoadingAlgorithms(false)
      }
    }

    fetchAlgorithms()
  }, [toast])

  // Fetch curves
  useEffect(() => {
    const fetchCurves = async () => {
      setIsLoadingCurves(true)
      try {
        // This would be a real API call in production
        // const response = await fetch('/api/curves', {
        //   headers: {
        //     'Authorization': `Bearer ${localStorage.getItem('token')}`
        //   }
        // })

        // Simulate API call
        await new Promise((resolve) => setTimeout(resolve, 1000))

        // Mock data
        const mockCurves: Curve[] = [
          {
            id: "curve-1",
            name: "secp256k1",
            algorithmId: "algo-1",
            algorithmName: "ECDSA",
            parameters: {
              a: "0",
              b: "7",
              p: "0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F",
              n: "0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141",
              h: "1",
              Gx: "0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798",
              Gy: "0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8",
            },
            description: "Bitcoin curve, used in blockchain applications",
            status: "enabled",
            createdAt: "2023-01-20T11:30:00Z",
          },
          {
            id: "curve-2",
            name: "P-256",
            algorithmId: "algo-1",
            algorithmName: "ECDSA",
            parameters: {
              a: "-3",
              b: "0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B",
              p: "0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF",
              n: "0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551",
              h: "1",
              Gx: "0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296",
              Gy: "0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5",
            },
            description: "NIST P-256 curve, widely used in TLS",
            status: "enabled",
            createdAt: "2023-01-20T11:35:00Z",
          },
          {
            id: "curve-3",
            name: "Ed25519",
            algorithmId: "algo-3",
            algorithmName: "EdDSA",
            parameters: {
              a: "-1",
              d: "-121665/121666",
              p: "2^255 - 19",
              n: "2^252 + 27742317777372353535851937790883648493",
              h: "8",
              Gx: "15112221349535400772501151409588531511454012693041857206046113283949847762202",
              Gy: "46316835694926478169428394003475163141307993866256225615783033603165251855960",
            },
            description: "Edwards curve, used in modern cryptography",
            status: "enabled",
            createdAt: "2023-01-20T11:40:00Z",
          },
          {
            id: "curve-4",
            name: "P-521",
            algorithmId: "algo-1",
            algorithmName: "ECDSA",
            parameters: {
              a: "-3",
              b: "0x051953EB9618E1C9A1F929A21A0B68540EEA2DA725B99B315F3B8B489918EF109E156193951EC7E937B1652C0BD3BB1BF073573DF883D2C34F1EF451FD46B503F00",
              p: "0x01FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF",
              n: "0x01FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFA51868783BF2F966B7FCC0148F709A5D03BB5C9B8899C47AEBB6FB71E91386409",
              h: "1",
              Gx: "0x00C6858E06B70404E9CD9E3ECB662395B4429C648139053FB521F828AF606B4D3DBAA14B5E77EFE75928FE1DC127A2FFA8DE3348B3C1856A429BF97E7E31C2E5BD66",
              Gy: "0x011839296A789A3BC0045C8A5FB42C7D1BD998F54449579B446817AFBD17273E662C97EE72995EF42640C550B9013FAD0761353C7086A272C24088BE94769FD16650",
            },
            description: "NIST P-521 curve, highest security level",
            status: "disabled",
            createdAt: "2023-01-20T11:45:00Z",
          },
        ]

        setCurves(mockCurves)
      } catch (error) {
        toast({
          title: "Error",
          description: "Failed to load curves",
          variant: "destructive",
        })
      } finally {
        setIsLoadingCurves(false)
      }
    }

    fetchCurves()
  }, [toast])

  // Handle adding a new algorithm
  const handleAddAlgorithm = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      // This would be a real API call in production
      // const response = await fetch('/api/algorithms', {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     'Authorization': `Bearer ${localStorage.getItem('token')}`
      //   },
      //   body: JSON.stringify(newAlgorithm)
      // })

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Create a mock new algorithm
      const mockNewAlgorithm: Algorithm = {
        id: `algo-${Math.random().toString(36).substring(2, 10)}`,
        name: newAlgorithm.name,
        type: newAlgorithm.type,
        description: newAlgorithm.description,
        createdAt: new Date().toISOString(),
      }

      setAlgorithms([...algorithms, mockNewAlgorithm])
      setIsAddingAlgorithm(false)
      setNewAlgorithm({
        name: "",
        type: "",
        description: "",
      })

      toast({
        title: "Algorithm Added",
        description: "The algorithm has been added successfully",
        variant: "default",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to add algorithm",
        variant: "destructive",
      })
    }
  }

  // Handle updating an algorithm
  const handleUpdateAlgorithm = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedAlgorithm) return

    try {
      // This would be a real API call in production
      // const response = await fetch(`/api/algorithms/${selectedAlgorithm.id}`, {
      //   method: 'PUT',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     'Authorization': `Bearer ${localStorage.getItem('token')}`
      //   },
      //   body: JSON.stringify({
      //     name: selectedAlgorithm.name,
      //     type: selectedAlgorithm.type,
      //     description: selectedAlgorithm.description
      //   })
      // })

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Update local state
      setAlgorithms(algorithms.map((algo) => (algo.id === selectedAlgorithm.id ? { ...selectedAlgorithm } : algo)))
      setSelectedAlgorithm(null)

      toast({
        title: "Algorithm Updated",
        description: "The algorithm has been updated successfully",
        variant: "default",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update algorithm",
        variant: "destructive",
      })
    }
  }

  // Handle adding a new curve
  const handleAddCurve = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      // This would be a real API call in production
      // const response = await fetch('/api/curves', {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     'Authorization': `Bearer ${localStorage.getItem('token')}`
      //   },
      //   body: JSON.stringify({
      //     name: newCurve.name,
      //     algorithm_id: newCurve.algorithmId,
      //     parameters: JSON.parse(newCurve.parameters),
      //     description: newCurve.description
      //   })
      // })

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Find the algorithm name
      const algorithm = algorithms.find((algo) => algo.id === newCurve.algorithmId)

      // Create a mock new curve
      const mockNewCurve: Curve = {
        id: `curve-${Math.random().toString(36).substring(2, 10)}`,
        name: newCurve.name,
        algorithmId: newCurve.algorithmId,
        algorithmName: algorithm?.name || "",
        parameters: JSON.parse(newCurve.parameters),
        description: newCurve.description,
        status: "enabled",
        createdAt: new Date().toISOString(),
      }

      setCurves([...curves, mockNewCurve])
      setIsAddingCurve(false)
      setNewCurve({
        name: "",
        algorithmId: "",
        parameters: "",
        description: "",
      })

      toast({
        title: "Curve Added",
        description: "The curve has been added successfully",
        variant: "default",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to add curve",
        variant: "destructive",
      })
    }
  }

  // Handle updating a curve
  const handleUpdateCurve = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedCurve) return

    try {
      // This would be a real API call in production
      // const response = await fetch(`/api/curves/${selectedCurve.id}`, {
      //   method: 'PUT',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     'Authorization': `Bearer ${localStorage.getItem('token')}`
      //   },
      //   body: JSON.stringify({
      //     name: selectedCurve.name,
      //     parameters: selectedCurve.parameters,
      //     description: selectedCurve.description,
      //     status: selectedCurve.status
      //   })
      // })

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Update local state
      setCurves(curves.map((curve) => (curve.id === selectedCurve.id ? { ...selectedCurve } : curve)))
      setSelectedCurve(null)

      toast({
        title: "Curve Updated",
        description: "The curve has been updated successfully",
        variant: "default",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update curve",
        variant: "destructive",
      })
    }
  }

  // Handle toggling curve status
  const handleToggleCurveStatus = async (curveId: string, newStatus: "enabled" | "disabled") => {
    try {
      // This would be a real API call in production
      // const response = await fetch(`/api/curves/${curveId}`, {
      //   method: 'PUT',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     'Authorization': `Bearer ${localStorage.getItem('token')}`
      //   },
      //   body: JSON.stringify({
      //     status: newStatus
      //   })
      // })

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Update local state
      setCurves(curves.map((curve) => (curve.id === curveId ? { ...curve, status: newStatus } : curve)))

      toast({
        title: "Curve Status Updated",
        description: `The curve has been ${newStatus === "enabled" ? "enabled" : "disabled"}`,
        variant: "default",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update curve status",
        variant: "destructive",
      })
    }
  }

  return (
    <ProtectedRoute adminOnly>
      <div className="container py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold">Algorithm Management</h1>
          <p className="text-muted-foreground">Manage cryptographic algorithms and curves</p>
        </div>

        <Tabs defaultValue="algorithms" className="w-full">
          <TabsList className="mb-4">
            <TabsTrigger value="algorithms">Algorithms</TabsTrigger>
            <TabsTrigger value="curves">Curves</TabsTrigger>
          </TabsList>

          {/* Algorithms Tab */}
          <TabsContent value="algorithms">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Algorithms</CardTitle>
                  <CardDescription>Manage supported cryptographic algorithms</CardDescription>
                </div>
                <Dialog open={isAddingAlgorithm} onOpenChange={setIsAddingAlgorithm}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="mr-2 h-4 w-4" />
                      Add Algorithm
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[550px]">
                    <DialogHeader>
                      <DialogTitle>Add New Algorithm</DialogTitle>
                      <DialogDescription>Add a new cryptographic algorithm to the system</DialogDescription>
                    </DialogHeader>

                    <form onSubmit={handleAddAlgorithm} className="space-y-4 py-4">
                      <div className="space-y-2">
                        <Label htmlFor="name">Algorithm Name</Label>
                        <Input
                          id="name"
                          value={newAlgorithm.name}
                          onChange={(e) => setNewAlgorithm({ ...newAlgorithm, name: e.target.value })}
                          placeholder="e.g., ECDSA"
                          required
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="type">Algorithm Type</Label>
                        <Select
                          value={newAlgorithm.type}
                          onValueChange={(value) => setNewAlgorithm({ ...newAlgorithm, type: value })}
                          required
                        >
                          <SelectTrigger id="type">
                            <SelectValue placeholder="Select algorithm type" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="ECDSA">ECDSA</SelectItem>
                            <SelectItem value="RSA">RSA</SelectItem>
                            <SelectItem value="EdDSA">EdDSA</SelectItem>
                            <SelectItem value="other">Other</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="description">Description</Label>
                        <Textarea
                          id="description"
                          value={newAlgorithm.description}
                          onChange={(e) => setNewAlgorithm({ ...newAlgorithm, description: e.target.value })}
                          placeholder="Describe the algorithm and its use cases"
                          required
                        />
                      </div>

                      <DialogFooter>
                        <Button type="button" variant="outline" onClick={() => setIsAddingAlgorithm(false)}>
                          Cancel
                        </Button>
                        <Button type="submit">Add Algorithm</Button>
                      </DialogFooter>
                    </form>
                  </DialogContent>
                </Dialog>
              </CardHeader>
              <CardContent>
                {isLoadingAlgorithms ? (
                  <div className="flex justify-center py-8">
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                  </div>
                ) : algorithms.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-8 text-center">
                    <Info className="h-12 w-12 text-muted-foreground mb-4" />
                    <h3 className="text-lg font-medium">No Algorithms</h3>
                    <p className="text-muted-foreground mt-1">No algorithms have been added yet</p>
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Description</TableHead>
                        <TableHead>Created</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {algorithms.map((algorithm) => (
                        <TableRow key={algorithm.id}>
                          <TableCell className="font-medium">{algorithm.name}</TableCell>
                          <TableCell>{algorithm.type}</TableCell>
                          <TableCell>{algorithm.description}</TableCell>
                          <TableCell>{new Date(algorithm.createdAt).toLocaleDateString()}</TableCell>
                          <TableCell className="text-right">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => setSelectedAlgorithm(algorithm)}
                              title="Edit Algorithm"
                            >
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

          {/* Curves Tab */}
          <TabsContent value="curves">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Curves</CardTitle>
                  <CardDescription>Manage elliptic curves for cryptographic algorithms</CardDescription>
                </div>
                <Dialog open={isAddingCurve} onOpenChange={setIsAddingCurve}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="mr-2 h-4 w-4" />
                      Add Curve
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[550px]">
                    <DialogHeader>
                      <DialogTitle>Add New Curve</DialogTitle>
                      <DialogDescription>Add a new elliptic curve to the system</DialogDescription>
                    </DialogHeader>

                    <form onSubmit={handleAddCurve} className="space-y-4 py-4">
                      <div className="space-y-2">
                        <Label htmlFor="curveName">Curve Name</Label>
                        <Input
                          id="curveName"
                          value={newCurve.name}
                          onChange={(e) => setNewCurve({ ...newCurve, name: e.target.value })}
                          placeholder="e.g., secp256k1"
                          required
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="algorithmId">Algorithm</Label>
                        <Select
                          value={newCurve.algorithmId}
                          onValueChange={(value) => setNewCurve({ ...newCurve, algorithmId: value })}
                          required
                        >
                          <SelectTrigger id="algorithmId">
                            <SelectValue placeholder="Select algorithm" />
                          </SelectTrigger>
                          <SelectContent>
                            {algorithms.map((algorithm) => (
                              <SelectItem key={algorithm.id} value={algorithm.id}>
                                {algorithm.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="parameters">Parameters (JSON)</Label>
                        <Textarea
                          id="parameters"
                          value={newCurve.parameters}
                          onChange={(e) => setNewCurve({ ...newCurve, parameters: e.target.value })}
                          placeholder='{"a": "0", "b": "7", "p": "0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F"}'
                          className="font-mono text-xs"
                          required
                        />
                        <p className="text-xs text-muted-foreground">
                          Enter curve parameters in JSON format. Include all required parameters for the curve type.
                        </p>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="curveDescription">Description</Label>
                        <Textarea
                          id="curveDescription"
                          value={newCurve.description}
                          onChange={(e) => setNewCurve({ ...newCurve, description: e.target.value })}
                          placeholder="Describe the curve and its use cases"
                          required
                        />
                      </div>

                      <DialogFooter>
                        <Button type="button" variant="outline" onClick={() => setIsAddingCurve(false)}>
                          Cancel
                        </Button>
                        <Button type="submit">Add Curve</Button>
                      </DialogFooter>
                    </form>
                  </DialogContent>
                </Dialog>
              </CardHeader>
              <CardContent>
                {isLoadingCurves ? (
                  <div className="flex justify-center py-8">
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                  </div>
                ) : curves.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-8 text-center">
                    <Info className="h-12 w-12 text-muted-foreground mb-4" />
                    <h3 className="text-lg font-medium">No Curves</h3>
                    <p className="text-muted-foreground mt-1">No curves have been added yet</p>
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Algorithm</TableHead>
                        <TableHead>Description</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {curves.map((curve) => (
                        <TableRow key={curve.id}>
                          <TableCell className="font-medium">{curve.name}</TableCell>
                          <TableCell>{curve.algorithmName}</TableCell>
                          <TableCell>{curve.description}</TableCell>
                          <TableCell>
                            {curve.status === "enabled" ? (
                              <Badge className="bg-green-500">Enabled</Badge>
                            ) : (
                              <Badge variant="outline" className="text-amber-500 border-amber-500">
                                Disabled
                              </Badge>
                            )}
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex justify-end gap-2">
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => setSelectedCurve(curve)}
                                title="Edit Curve"
                              >
                                <Edit className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() =>
                                  handleToggleCurveStatus(curve.id, curve.status === "enabled" ? "disabled" : "enabled")
                                }
                                title={curve.status === "enabled" ? "Disable Curve" : "Enable Curve"}
                              >
                                <Trash2
                                  className={`h-4 w-4 ${
                                    curve.status === "enabled" ? "text-destructive" : "text-green-500"
                                  }`}
                                />
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
          </TabsContent>
        </Tabs>

        {/* Edit Algorithm Dialog */}
        {selectedAlgorithm && (
          <Dialog open={!!selectedAlgorithm} onOpenChange={(open) => !open && setSelectedAlgorithm(null)}>
            <DialogContent className="sm:max-w-[550px]">
              <DialogHeader>
                <DialogTitle>Edit Algorithm</DialogTitle>
                <DialogDescription>Update algorithm details</DialogDescription>
              </DialogHeader>

              <form onSubmit={handleUpdateAlgorithm} className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="editName">Algorithm Name</Label>
                  <Input
                    id="editName"
                    value={selectedAlgorithm.name}
                    onChange={(e) => setSelectedAlgorithm({ ...selectedAlgorithm, name: e.target.value })}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="editType">Algorithm Type</Label>
                  <Select
                    value={selectedAlgorithm.type}
                    onValueChange={(value) => setSelectedAlgorithm({ ...selectedAlgorithm, type: value })}
                    required
                  >
                    <SelectTrigger id="editType">
                      <SelectValue placeholder="Select algorithm type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="ECDSA">ECDSA</SelectItem>
                      <SelectItem value="RSA">RSA</SelectItem>
                      <SelectItem value="EdDSA">EdDSA</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="editDescription">Description</Label>
                  <Textarea
                    id="editDescription"
                    value={selectedAlgorithm.description}
                    onChange={(e) => setSelectedAlgorithm({ ...selectedAlgorithm, description: e.target.value })}
                    required
                  />
                </div>

                <DialogFooter>
                  <Button type="button" variant="outline" onClick={() => setSelectedAlgorithm(null)}>
                    Cancel
                  </Button>
                  <Button type="submit">Update Algorithm</Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        )}

        {/* Edit Curve Dialog */}
        {selectedCurve && (
          <Dialog open={!!selectedCurve} onOpenChange={(open) => !open && setSelectedCurve(null)}>
            <DialogContent className="sm:max-w-[550px]">
              <DialogHeader>
                <DialogTitle>Edit Curve</DialogTitle>
                <DialogDescription>Update curve details</DialogDescription>
              </DialogHeader>

              <form onSubmit={handleUpdateCurve} className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="editCurveName">Curve Name</Label>
                  <Input
                    id="editCurveName"
                    value={selectedCurve.name}
                    onChange={(e) => setSelectedCurve({ ...selectedCurve, name: e.target.value })}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="editCurveDescription">Description</Label>
                  <Textarea
                    id="editCurveDescription"
                    value={selectedCurve.description}
                    onChange={(e) => setSelectedCurve({ ...selectedCurve, description: e.target.value })}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="editCurveParameters">Parameters (JSON)</Label>
                  <Textarea
                    id="editCurveParameters"
                    value={JSON.stringify(selectedCurve.parameters, null, 2)}
                    onChange={(e) => {
                      try {
                        const parsedParams = JSON.parse(e.target.value)
                        setSelectedCurve({ ...selectedCurve, parameters: parsedParams })
                      } catch (error) {
                        // Don't update if JSON is invalid
                      }
                    }}
                    className="font-mono text-xs min-h-[200px]"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="editCurveStatus">Status</Label>
                  <Select
                    value={selectedCurve.status}
                    onValueChange={(value: "enabled" | "disabled") =>
                      setSelectedCurve({ ...selectedCurve, status: value })
                    }
                    required
                  >
                    <SelectTrigger id="editCurveStatus">
                      <SelectValue placeholder="Select status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="enabled">Enabled</SelectItem>
                      <SelectItem value="disabled">Disabled</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <DialogFooter>
                  <Button type="button" variant="outline" onClick={() => setSelectedCurve(null)}>
                    Cancel
                  </Button>
                  <Button type="submit">Update Curve</Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        )}
      </div>
    </ProtectedRoute>
  )
}
