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
import { Progress } from "@/components/ui/progress"
import { Loader2, Search, Download, Eye, Calendar, FileCheck, FileX } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { format } from "date-fns"

// Types
type BatchVerification = {
  id: string
  userId: string
  username: string
  totalCount: number
  successCount: number
  verificationTime: string
  metadata?: Record<string, any>
}

type BatchItem = {
  index: number
  verificationRecordId: string
  documentHash: string
  isValid: boolean
}

export default function BatchVerificationsPage() {
  const [batches, setBatches] = useState<BatchVerification[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [dateFilter, setDateFilter] = useState("all")
  const [selectedBatch, setSelectedBatch] = useState<BatchVerification | null>(null)
  const [batchItems, setBatchItems] = useState<BatchItem[]>([])
  const [isLoadingItems, setIsLoadingItems] = useState(false)
  const { toast } = useToast()

  useEffect(() => {
    const fetchBatches = async () => {
      setIsLoading(true)
      try {
        // This would be a real API call in production
        // const response = await fetch('/api/batch-verifications', {
        //   headers: {
        //     'Authorization': `Bearer ${localStorage.getItem('token')}`
        //   }
        // })

        // Simulate API call
        await new Promise((resolve) => setTimeout(resolve, 1500))

        // Mock data
        const mockBatches: BatchVerification[] = Array(15)
          .fill(0)
          .map((_, index) => {
            const totalCount = Math.floor(Math.random() * 20) + 5
            const successCount = Math.floor(Math.random() * totalCount)
            const date = new Date()
            date.setDate(date.getDate() - Math.floor(Math.random() * 30))

            return {
              id: `batch-${Math.random().toString(36).substring(2, 10)}`,
              userId: `user-${(index % 5) + 1}`,
              username: ["admin", "johndoe", "janedoe", "bobsmith", "alicejones"][index % 5],
              totalCount,
              successCount,
              verificationTime: date.toISOString(),
              metadata: {
                source: ["API", "Web Interface", "Bulk Upload", "Scheduled Task"][index % 4],
                ipAddress: `192.168.1.${index + 1}`,
                userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
              },
            }
          })

        setBatches(mockBatches)
      } catch (error) {
        toast({
          title: "Error",
          description: "Failed to load batch verifications",
          variant: "destructive",
        })
      } finally {
        setIsLoading(false)
      }
    }

    fetchBatches()
  }, [toast])

  const filteredBatches = batches.filter((batch) => {
    const matchesSearch =
      batch.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
      batch.id.toLowerCase().includes(searchTerm.toLowerCase())

    const batchDate = new Date(batch.verificationTime)
    const now = new Date()
    const matchesDate =
      dateFilter === "all" ||
      (dateFilter === "today" &&
        batchDate.getDate() === now.getDate() &&
        batchDate.getMonth() === now.getMonth() &&
        batchDate.getFullYear() === now.getFullYear()) ||
      (dateFilter === "week" && now.getTime() - batchDate.getTime() < 7 * 24 * 60 * 60 * 1000) ||
      (dateFilter === "month" && now.getTime() - batchDate.getTime() < 30 * 24 * 60 * 60 * 1000)

    return matchesSearch && matchesDate
  })

  const handleViewBatch = async (batch: BatchVerification) => {
    setSelectedBatch(batch)
    setIsLoadingItems(true)

    try {
      // This would be a real API call in production
      // const response = await fetch(`/api/batch-verifications/${batch.id}/items`, {
      //   headers: {
      //     'Authorization': `Bearer ${localStorage.getItem('token')}`
      //   }
      // })

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Mock data
      const mockItems: BatchItem[] = Array(batch.totalCount)
        .fill(0)
        .map((_, index) => {
          const isValid = index < batch.successCount

          return {
            index,
            verificationRecordId: `ver-${Math.random().toString(36).substring(2, 10)}`,
            documentHash: `hash-${Math.random().toString(36).substring(2, 15)}`,
            isValid,
          }
        })

      setBatchItems(mockItems)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load batch items",
        variant: "destructive",
      })
    } finally {
      setIsLoadingItems(false)
    }
  }

  const handleExport = () => {
    toast({
      title: "Export Started",
      description: "Batch verification records are being exported to CSV",
      variant: "default",
    })
  }

  return (
    <ProtectedRoute adminOnly>
      <div className="container py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold">Batch Verifications</h1>
          <p className="text-muted-foreground">View and manage batch signature verification operations</p>
        </div>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Batch Verification History</CardTitle>
              <CardDescription>All batch verification operations across the system</CardDescription>
            </div>
            <Button onClick={handleExport} className="flex items-center gap-2">
              <Download className="h-4 w-4" />
              Export CSV
            </Button>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-6">
              <div className="relative w-full sm:w-96">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search batches..."
                  className="pl-8"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>

              <div className="flex items-center gap-2">
                <Label htmlFor="date-filter" className="whitespace-nowrap">
                  Date:
                </Label>
                <Select value={dateFilter} onValueChange={setDateFilter}>
                  <SelectTrigger id="date-filter" className="w-[130px]">
                    <SelectValue placeholder="Filter by date" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Time</SelectItem>
                    <SelectItem value="today">Today</SelectItem>
                    <SelectItem value="week">This Week</SelectItem>
                    <SelectItem value="month">This Month</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {isLoading ? (
              <div className="flex justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
              </div>
            ) : filteredBatches.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <Calendar className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium">No Batches Found</h3>
                <p className="text-muted-foreground mt-1">No batch verifications match your current filters</p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Batch ID</TableHead>
                    <TableHead>User</TableHead>
                    <TableHead>Success Rate</TableHead>
                    <TableHead>Total Items</TableHead>
                    <TableHead>Time</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredBatches.map((batch) => (
                    <TableRow key={batch.id}>
                      <TableCell className="font-medium">{batch.id}</TableCell>
                      <TableCell>{batch.username}</TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          <div className="flex items-center justify-between text-xs">
                            <span>
                              {batch.successCount} / {batch.totalCount} (
                              {Math.round((batch.successCount / batch.totalCount) * 100)}%)
                            </span>
                            <Badge
                              variant={
                                batch.successCount / batch.totalCount >= 0.9
                                  ? "default"
                                  : batch.successCount / batch.totalCount >= 0.7
                                    ? "outline"
                                    : "destructive"
                              }
                              className={
                                batch.successCount / batch.totalCount >= 0.9
                                  ? "bg-green-500"
                                  : batch.successCount / batch.totalCount >= 0.7
                                    ? "text-amber-500 border-amber-500"
                                    : ""
                              }
                            >
                              {batch.successCount / batch.totalCount >= 0.9
                                ? "Good"
                                : batch.successCount / batch.totalCount >= 0.7
                                  ? "Fair"
                                  : "Poor"}
                            </Badge>
                          </div>
                          <Progress value={(batch.successCount / batch.totalCount) * 100} className="h-2" />
                        </div>
                      </TableCell>
                      <TableCell>{batch.totalCount}</TableCell>
                      <TableCell>{format(new Date(batch.verificationTime), "MMM d, yyyy HH:mm")}</TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="icon" onClick={() => handleViewBatch(batch)} title="View Details">
                          <Eye className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* Batch Details Dialog */}
        {selectedBatch && (
          <Dialog open={!!selectedBatch} onOpenChange={(open) => !open && setSelectedBatch(null)}>
            <DialogContent className="sm:max-w-[700px]">
              <DialogHeader>
                <DialogTitle>Batch Verification Details</DialogTitle>
                <DialogDescription>Detailed information about this batch verification operation</DialogDescription>
              </DialogHeader>

              <div className="space-y-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-muted-foreground">Batch ID</Label>
                    <p className="font-medium">{selectedBatch.id}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">User</Label>
                    <p className="font-medium">{selectedBatch.username}</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-muted-foreground">Verification Time</Label>
                    <p className="font-medium">{format(new Date(selectedBatch.verificationTime), "PPpp")}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Success Rate</Label>
                    <p className="font-medium">
                      {selectedBatch.successCount} / {selectedBatch.totalCount} (
                      {Math.round((selectedBatch.successCount / selectedBatch.totalCount) * 100)}%)
                    </p>
                  </div>
                </div>

                {selectedBatch.metadata && (
                  <div>
                    <Label className="text-muted-foreground">Metadata</Label>
                    <div className="bg-muted p-2 rounded mt-1 space-y-1">
                      {Object.entries(selectedBatch.metadata).map(([key, value]) => (
                        <div key={key} className="grid grid-cols-2 text-sm">
                          <span className="font-medium">{key}</span>
                          <span>{value as string}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <Label>Batch Items</Label>
                    {isLoadingItems && <Loader2 className="h-4 w-4 animate-spin text-primary" />}
                  </div>

                  {isLoadingItems ? (
                    <div className="flex justify-center py-8">
                      <Loader2 className="h-8 w-8 animate-spin text-primary" />
                    </div>
                  ) : (
                    <div className="border rounded-md overflow-hidden">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Index</TableHead>
                            <TableHead>Document Hash</TableHead>
                            <TableHead>Status</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {batchItems.map((item) => (
                            <TableRow key={item.index}>
                              <TableCell>{item.index + 1}</TableCell>
                              <TableCell className="font-mono text-xs">{item.documentHash}</TableCell>
                              <TableCell>
                                {item.isValid ? (
                                  <Badge className="bg-green-500 flex items-center gap-1">
                                    <FileCheck className="h-3 w-3" /> Valid
                                  </Badge>
                                ) : (
                                  <Badge variant="destructive" className="flex items-center gap-1">
                                    <FileX className="h-3 w-3" /> Invalid
                                  </Badge>
                                )}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  )}
                </div>
              </div>

              <DialogFooter>
                <Button variant="outline" onClick={() => setSelectedBatch(null)}>
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
