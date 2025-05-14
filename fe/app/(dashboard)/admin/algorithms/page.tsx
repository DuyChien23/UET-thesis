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
import { apiService } from "@/lib/api"
import { getErrorMessage } from "@/lib/errors"

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
  algorithm_id: string
  algorithm_name?: string  
  parameters: Record<string, any>
  description?: string
  status: "enabled" | "disabled"
  created_at?: string
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
        const algorithmsData = await apiService.getAlgorithms()
        setAlgorithms(algorithmsData)
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
        let curvesData: Curve[] = []
        
        if (selectedAlgorithm) {
          // If an algorithm is selected, only fetch curves for that algorithm
          curvesData = await apiService.getCurves({ algorithm_id: selectedAlgorithm.id });
        } else {
          // Fetch all curves
          curvesData = await apiService.getCurves();
        }
        
        setCurves(curvesData)
      } catch (error) {
        toast({
          title: "Error",
          description: `Failed to load curves: ${getErrorMessage(error)}`,
          variant: "destructive",
        })
      } finally {
        setIsLoadingCurves(false)
      }
    }

    fetchCurves()
  }, [selectedAlgorithm, toast])

  // Handle adding a new algorithm
  const handleAddAlgorithm = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const algorithmData = {
        name: newAlgorithm.name,
        type: newAlgorithm.type,
        description: newAlgorithm.description,
        is_default: false // Default algorithms should be set carefully
      }

      const createdAlgorithm = await apiService.createAlgorithm(algorithmData)
      
      setAlgorithms([...algorithms, createdAlgorithm])
      setIsAddingAlgorithm(false)
      setNewAlgorithm({ name: "", type: "", description: "" })

      toast({
        title: "Algorithm Added",
        description: `Algorithm ${createdAlgorithm.name} has been added successfully.`,
      })
    } catch (error) {
      toast({
        title: "Error",
        description: `Failed to add algorithm: ${getErrorMessage(error)}`,
        variant: "destructive",
      })
    }
  }

  // Handle updating an algorithm
  const handleUpdateAlgorithm = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedAlgorithm) return

    try {
      const algorithmData = {
        name: selectedAlgorithm.name,
        type: selectedAlgorithm.type,
        description: selectedAlgorithm.description
      }

      const updatedAlgorithm = await apiService.updateAlgorithm(
        selectedAlgorithm.id, 
        algorithmData
      )
      
      setAlgorithms(
        algorithms.map((algorithm) =>
          algorithm.id === selectedAlgorithm.id ? updatedAlgorithm : algorithm
        )
      )
      setSelectedAlgorithm(null)

      toast({
        title: "Algorithm Updated",
        description: `Algorithm ${updatedAlgorithm.name} has been updated successfully.`,
      })
    } catch (error) {
      toast({
        title: "Error",
        description: `Failed to update algorithm: ${getErrorMessage(error)}`,
        variant: "destructive",
      })
    }
  }

  // Handle deleting an algorithm
  const handleDeleteAlgorithm = async (algorithmId: string) => {
    if (!confirm("Are you sure you want to delete this algorithm? This will also disable all associated curves.")) {
      return
    }

    try {
      await apiService.deleteAlgorithm(algorithmId)
      
      // Update local state to reflect deletion
      setAlgorithms(algorithms.filter((algorithm) => algorithm.id !== algorithmId))
      // Update curves list to reflect disabled status
      setCurves(
        curves.map((curve) =>
          curve.algorithm_id === algorithmId ? { ...curve, status: "disabled" } : curve
        )
      )

      toast({
        title: "Algorithm Deleted",
        description: "Algorithm has been deleted successfully.",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: `Failed to delete algorithm: ${getErrorMessage(error)}`,
        variant: "destructive",
      })
    }
  }

  // Handle adding a new curve
  const handleAddCurve = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      // Parse JSON parameters
      let parsedParameters: Record<string, any> = {}
      try {
        parsedParameters = JSON.parse(newCurve.parameters as string)
      } catch (error) {
        toast({
          title: "Invalid JSON",
          description: "Parameters must be a valid JSON object",
          variant: "destructive",
        })
        return
      }

      const curveData = {
        name: newCurve.name,
        algorithm_id: newCurve.algorithmId,
        description: newCurve.description,
        parameters: parsedParameters
      }

      const createdCurve = await apiService.createCurve(curveData)
      
      setCurves([...curves, createdCurve])
      setIsAddingCurve(false)
      setNewCurve({
        name: "",
        algorithmId: "",
        parameters: "",
        description: "",
      })

      toast({
        title: "Curve Added",
        description: `Curve ${createdCurve.name} has been added successfully.`,
      })
    } catch (error) {
      toast({
        title: "Error",
        description: `Failed to add curve: ${getErrorMessage(error)}`,
        variant: "destructive",
      })
    }
  }

  // Handle updating a curve
  const handleUpdateCurve = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedCurve) return

    try {
      // Parse JSON parameters
      let parsedParameters: Record<string, any> = {}
      if (typeof selectedCurve.parameters === 'string') {
        try {
          parsedParameters = JSON.parse(selectedCurve.parameters as string)
        } catch (error) {
          toast({
            title: "Invalid JSON",
            description: "Parameters must be a valid JSON object",
            variant: "destructive",
          })
          return
        }
      } else {
        parsedParameters = selectedCurve.parameters
      }

      const curveData = {
        name: selectedCurve.name,
        description: selectedCurve.description,
        parameters: parsedParameters,
        status: selectedCurve.status,
      }

      const updatedCurve = await apiService.updateCurve(selectedCurve.id, curveData)
      
      setCurves(
        curves.map((curve) =>
          curve.id === selectedCurve.id ? updatedCurve : curve
        )
      )
      setSelectedCurve(null)

      toast({
        title: "Curve Updated",
        description: `Curve ${updatedCurve.name} has been updated successfully.`,
      })
    } catch (error) {
      toast({
        title: "Error",
        description: `Failed to update curve: ${getErrorMessage(error)}`,
        variant: "destructive",
      })
    }
  }

  // Handle toggling curve status (enabled/disabled)
  const handleToggleCurveStatus = async (curveId: string, newStatus: "enabled" | "disabled") => {
    const curve = curves.find((c) => c.id === curveId)
    if (!curve) return

    const statusText = newStatus === "enabled" ? "enable" : "disable"
    if (!confirm(`Are you sure you want to ${statusText} this curve?`)) {
      return
    }

    try {
      const updatedCurve = await apiService.updateCurve(curveId, { status: newStatus })
      
      setCurves(
        curves.map((c) =>
          c.id === curveId ? updatedCurve : c
        )
      )

      toast({
        title: "Status Updated",
        description: `Curve has been ${newStatus === "enabled" ? "enabled" : "disabled"}.`,
      })
    } catch (error) {
      toast({
        title: "Error",
        description: `Failed to update curve status: ${getErrorMessage(error)}`,
        variant: "destructive",
      })
    }
  }

  // Handle deleting a curve
  const handleDeleteCurve = async (curveId: string) => {
    if (!confirm("Are you sure you want to delete this curve?")) {
      return
    }

    try {
      await apiService.deleteCurve(curveId)
      
      // Update local state to reflect deletion
      setCurves(curves.filter((curve) => curve.id !== curveId))

      toast({
        title: "Curve Deleted",
        description: "Curve has been deleted successfully.",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: `Failed to delete curve: ${getErrorMessage(error)}`,
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
                            <div className="flex justify-end gap-2">
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => setSelectedAlgorithm(algorithm)}
                                title="Edit Algorithm"
                              >
                                <Edit className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => handleDeleteAlgorithm(algorithm.id)}
                                title="Delete Algorithm"
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
                          <TableCell>{curve.algorithm_name}</TableCell>
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
                                onClick={() => handleDeleteCurve(curve.id)}
                                title="Delete Curve"
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
