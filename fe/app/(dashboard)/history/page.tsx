"use client"

import { useState, useEffect } from "react"
import { ProtectedRoute } from "@/components/protected-route"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
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
import { Label } from "@/components/ui/label"
import { Loader2, Search, FileCheck, FileX, Download, Eye, Calendar, Trash2, AlertTriangle } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { useAuth } from "@/contexts/auth-context"
import { format } from "date-fns"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"

// Types
type VerificationRecord = {
  id: string
  document_hash: string
  public_key_id: string
  algorithm_name: string
  curve_name: string
  status: string
  verified_at: string
  metadata?: Record<string, any>
}

type VerificationHistoryResponse = {
  items: VerificationRecord[]
  total_count: number
  offset: number
  limit: number
}

export default function HistoryPage() {
  const [records, setRecords] = useState<VerificationRecord[]>([])
  const [totalCount, setTotalCount] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [validFilter, setValidFilter] = useState("all")
  const [dateFilter, setDateFilter] = useState("all")
  const [selectedRecord, setSelectedRecord] = useState<VerificationRecord | null>(null)
  const [recordToDelete, setRecordToDelete] = useState<string | null>(null)
  const [isDeletingRecord, setIsDeletingRecord] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const [limit] = useState(10)
  const { toast } = useToast()
  const { token } = useAuth()

  const fetchRecords = async (page = 1, status: string | null = null, dateRange: string | null = null) => {
    if (!token) return
    
    setIsLoading(true)
    try {
      console.log("API URL:", process.env.NEXT_PUBLIC_API_URL)
      console.log("Token available:", !!token)
      
      // Calculate offset based on page number
      const offset = (page - 1) * limit
      
      // Build query parameters
      let queryParams = new URLSearchParams({
        limit: limit.toString(),
        offset: offset.toString()
      })
      
      // Add status filter if selected
      if (status && status !== "all") {
        queryParams.append("status", status === "valid" ? "success" : "failure")
      }
      
      // Add date filter if selected
      if (dateRange && dateRange !== "all") {
        const now = new Date()
        let startDate: Date
        
        if (dateRange === "today") {
          startDate = new Date(now.setHours(0, 0, 0, 0))
        } else if (dateRange === "week") {
          startDate = new Date(now.setDate(now.getDate() - 7))
        } else if (dateRange === "month") {
          startDate = new Date(now.setMonth(now.getMonth() - 1))
        } else {
          startDate = new Date(now.setFullYear(now.getFullYear() - 1))
        }
        
        queryParams.append("start_date", startDate.toISOString())
      }
      
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/verify/history/user?${queryParams.toString()}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )
      
      if (!response.ok) {
        throw new Error('Failed to fetch verification history')
      }
      
      const data: VerificationHistoryResponse = await response.json()
      setRecords(data.items)
      setTotalCount(data.total_count)
      setCurrentPage(page)
    } catch (error) {
      console.error('Error fetching records:', error)
      toast({
        title: "Error",
        description: "Failed to load verification history",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (token) {
      fetchRecords(currentPage, validFilter, dateFilter)
    }
  }, [token])

  // Apply filters
  const applyFilters = () => {
    fetchRecords(1, validFilter, dateFilter)
  }
  
  // When filter values change, reset to first page
  useEffect(() => {
    if (token && !isLoading) {
      applyFilters()
    }
  }, [validFilter, dateFilter])

  const handleExport = async () => {
    if (!token) return
    
    try {
      // Call the export API
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/verify/history/export`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )
      
      if (!response.ok) {
        throw new Error('Failed to export verification history')
      }
      
      // Get the blob data
      const blob = await response.blob()
      
      // Create a download link
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.style.display = 'none'
      a.href = url
      
      // Get current date for filename
      const date = new Date().toISOString().split('T')[0]
      a.download = `verification-history-${date}.csv`
      
      // Trigger download
      document.body.appendChild(a)
      a.click()
      
      // Cleanup
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      toast({
        title: "Export Complete",
        description: "Verification history has been exported to CSV",
        variant: "default",
      })
    } catch (error) {
      console.error('Error exporting history:', error)
      toast({
        title: "Export Failed",
        description: "Failed to export verification history",
        variant: "destructive",
      })
    }
  }
  
  const handleDeleteRecord = async () => {
    if (!token || !recordToDelete) return
    
    setIsDeletingRecord(true)
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/verify/records/${recordToDelete}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to delete verification record')
      }
      
      // Update state to remove the deleted record
      setRecords(prevRecords => prevRecords.filter(record => record.id !== recordToDelete))
      
      // If the deleted record was selected for viewing, close that dialog
      if (selectedRecord && selectedRecord.id === recordToDelete) {
        setSelectedRecord(null)
      }
      
      // Close the delete dialog
      setRecordToDelete(null)
      
      toast({
        title: "Record Deleted",
        description: "Verification record has been deleted successfully",
        variant: "default",
      })
    } catch (error) {
      console.error('Error deleting record:', error)
      toast({
        title: "Delete Failed",
        description: error instanceof Error ? error.message : "Failed to delete verification record",
        variant: "destructive",
      })
    } finally {
      setIsDeletingRecord(false)
    }
  }

  // Calculate total pages for pagination
  const totalPages = Math.ceil(totalCount / limit)
  
  // Filter records by search term client-side
  const filteredRecords = records.filter(record => 
    record.document_hash.toLowerCase().includes(searchTerm.toLowerCase()) ||
    record.algorithm_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (record.curve_name && record.curve_name.toLowerCase().includes(searchTerm.toLowerCase()))
  )

  // Pagination controls
  const goToPage = (page: number) => {
    if (page < 1 || page > totalPages) return
    fetchRecords(page, validFilter, dateFilter)
  }

  return (
    <ProtectedRoute>
      <div className="container py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold">Verification History</h1>
          <p className="text-muted-foreground">View your signature verification history</p>
        </div>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Your Verification History</CardTitle>
              <CardDescription>All your signature verification attempts</CardDescription>
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
                  placeholder="Search records..."
                  className="pl-8"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>

              <div className="flex flex-col sm:flex-row gap-2 sm:items-center">
                <div className="flex items-center gap-2">
                  <Label htmlFor="valid-filter" className="whitespace-nowrap">
                    Status:
                  </Label>
                  <Select value={validFilter} onValueChange={setValidFilter}>
                    <SelectTrigger id="valid-filter" className="w-[130px]">
                      <SelectValue placeholder="Filter by status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All</SelectItem>
                      <SelectItem value="valid">Valid</SelectItem>
                      <SelectItem value="invalid">Invalid</SelectItem>
                    </SelectContent>
                  </Select>
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
            </div>

            {isLoading ? (
              <div className="flex justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
              </div>
            ) : filteredRecords.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <Calendar className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium">No Records Found</h3>
                <p className="text-muted-foreground mt-1">No verification records match your current filters</p>
              </div>
            ) : (
              <>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Document Hash</TableHead>
                      <TableHead>Algorithm</TableHead>
                      <TableHead>Curve</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Time</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredRecords.map((record) => (
                      <TableRow key={record.id}>
                        <TableCell className="font-mono text-xs max-w-[200px] truncate">{record.document_hash}</TableCell>
                        <TableCell>{record.algorithm_name}</TableCell>
                        <TableCell>{record.curve_name || 'N/A'}</TableCell>
                        <TableCell>
                          {record.status === 'success' ? (
                            <Badge className="bg-green-500 flex items-center gap-1">
                              <FileCheck className="h-3 w-3" /> Valid
                            </Badge>
                          ) : (
                            <Badge variant="destructive" className="flex items-center gap-1">
                              <FileX className="h-3 w-3" /> Invalid
                            </Badge>
                          )}
                        </TableCell>
                        <TableCell>{format(new Date(record.verified_at), "MMM d, yyyy HH:mm")}</TableCell>
                        <TableCell className="text-right">
                          <div className="flex justify-end gap-2">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => setSelectedRecord(record)}
                              title="View Details"
                            >
                              <Eye className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => setRecordToDelete(record.id)}
                              title="Delete Record"
                            >
                              <Trash2 className="h-4 w-4 text-destructive" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                
                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-center gap-2 mt-6">
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={() => goToPage(currentPage - 1)}
                      disabled={currentPage === 1}
                    >
                      Previous
                    </Button>
                    
                    <span className="text-sm text-muted-foreground">
                      Page {currentPage} of {totalPages}
                    </span>
                    
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={() => goToPage(currentPage + 1)}
                      disabled={currentPage === totalPages}
                    >
                      Next
                    </Button>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>

        {/* Record Details Dialog */}
        {selectedRecord && (
          <Dialog open={!!selectedRecord} onOpenChange={(open) => !open && setSelectedRecord(null)}>
            <DialogContent className="sm:max-w-[550px]">
              <DialogHeader>
                <DialogTitle>Verification Record Details</DialogTitle>
                <DialogDescription>Detailed information about this verification record</DialogDescription>
              </DialogHeader>

              <div className="space-y-4 py-4">
                <div className="flex items-center justify-between">
                  <span className="font-medium">Status</span>
                  {selectedRecord.status === 'success' ? (
                    <Badge className="bg-green-500 flex items-center gap-1">
                      <FileCheck className="h-3 w-3" /> Valid
                    </Badge>
                  ) : (
                    <Badge variant="destructive" className="flex items-center gap-1">
                      <FileX className="h-3 w-3" /> Invalid
                    </Badge>
                  )}
                </div>

                <div>
                  <Label className="text-muted-foreground">Document Hash</Label>
                  <p className="font-mono text-xs bg-muted p-2 rounded mt-1">{selectedRecord.document_hash}</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-muted-foreground">Algorithm</Label>
                    <p className="font-medium">{selectedRecord.algorithm_name}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Curve</Label>
                    <p className="font-medium">{selectedRecord.curve_name || 'N/A'}</p>
                  </div>
                </div>

                <div>
                  <Label className="text-muted-foreground">Public Key ID</Label>
                  <p className="font-medium">{selectedRecord.public_key_id}</p>
                </div>

                <div>
                  <Label className="text-muted-foreground">Verification Time</Label>
                  <p className="font-medium">{format(new Date(selectedRecord.verified_at), "PPpp")}</p>
                </div>

                {selectedRecord.metadata && (
                  <div>
                    <Label className="text-muted-foreground">Metadata</Label>
                    <div className="bg-muted p-2 rounded mt-1 space-y-1">
                      {Object.entries(selectedRecord.metadata).map(([key, value]) => (
                        <div key={key} className="grid grid-cols-2 text-sm">
                          <span className="font-medium">{key}</span>
                          <span>{typeof value === 'object' ? JSON.stringify(value) : String(value)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <DialogFooter>
                <Button variant="destructive" 
                  onClick={() => {
                    setRecordToDelete(selectedRecord.id)
                    setSelectedRecord(null)
                  }}
                  className="mr-auto">
                  Delete
                </Button>
                <Button variant="outline" onClick={() => setSelectedRecord(null)}>
                  Close
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        )}
        
        {/* Delete Confirmation Dialog */}
        <AlertDialog open={!!recordToDelete} onOpenChange={(open) => !open && setRecordToDelete(null)}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-destructive" />
                Confirm Deletion
              </AlertDialogTitle>
              <AlertDialogDescription>
                Are you sure you want to delete this verification record? This action cannot be undone.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction 
                onClick={handleDeleteRecord}
                disabled={isDeletingRecord} 
                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              >
                {isDeletingRecord ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Deleting...
                  </>
                ) : 'Delete'}
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </ProtectedRoute>
  )
}
