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
import { Loader2, Search, FileCheck, FileX, Download, Eye, Calendar } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { format } from "date-fns"

// Types
type VerificationRecord = {
  id: string
  userId: string
  username: string
  documentHash: string
  publicKeyId: string
  algorithmName: string
  curveName: string
  isValid: boolean
  verificationTime: string
  metadata?: Record<string, any>
}

export default function VerificationRecordsPage() {
  const [records, setRecords] = useState<VerificationRecord[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [validFilter, setValidFilter] = useState("all")
  const [dateFilter, setDateFilter] = useState("all")
  const [selectedRecord, setSelectedRecord] = useState<VerificationRecord | null>(null)
  const { toast } = useToast()

  useEffect(() => {
    const fetchRecords = async () => {
      setIsLoading(true)
      try {
        // This would be a real API call in production
        // const response = await fetch('/api/verification-records', {
        //   headers: {
        //     'Authorization': `Bearer ${localStorage.getItem('token')}`
        //   }
        // })

        // Simulate API call
        await new Promise((resolve) => setTimeout(resolve, 1500))

        // Mock data
        const mockRecords: VerificationRecord[] = Array(20)
          .fill(0)
          .map((_, index) => {
            const isValid = Math.random() > 0.3
            const date = new Date()
            date.setDate(date.getDate() - Math.floor(Math.random() * 30))

            return {
              id: `ver-${Math.random().toString(36).substring(2, 10)}`,
              userId: `user-${(index % 5) + 1}`,
              username: ["admin", "johndoe", "janedoe", "bobsmith", "alicejones"][index % 5],
              documentHash: `hash-${Math.random().toString(36).substring(2, 15)}`,
              publicKeyId: `key-${(index % 3) + 1}`,
              algorithmName: ["ECDSA", "RSA", "EdDSA"][index % 3],
              curveName: ["secp256k1", "P-256", "Ed25519", "P-521"][index % 4],
              isValid,
              verificationTime: date.toISOString(),
              metadata: {
                documentType: ["PDF", "Word", "Text", "Image"][index % 4],
                documentName: `document-${index + 1}.${["pdf", "docx", "txt", "jpg"][index % 4]}`,
                ipAddress: `192.168.1.${index + 1}`,
                userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
              },
            }
          })

        setRecords(mockRecords)
      } catch (error) {
        toast({
          title: "Error",
          description: "Failed to load verification records",
          variant: "destructive",
        })
      } finally {
        setIsLoading(false)
      }
    }

    fetchRecords()
  }, [toast])

  const filteredRecords = records.filter((record) => {
    const matchesSearch =
      record.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
      record.documentHash.toLowerCase().includes(searchTerm.toLowerCase()) ||
      record.algorithmName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      record.curveName.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesValid =
      validFilter === "all" ||
      (validFilter === "valid" && record.isValid) ||
      (validFilter === "invalid" && !record.isValid)

    const recordDate = new Date(record.verificationTime)
    const now = new Date()
    const matchesDate =
      dateFilter === "all" ||
      (dateFilter === "today" &&
        recordDate.getDate() === now.getDate() &&
        recordDate.getMonth() === now.getMonth() &&
        recordDate.getFullYear() === now.getFullYear()) ||
      (dateFilter === "week" && now.getTime() - recordDate.getTime() < 7 * 24 * 60 * 60 * 1000) ||
      (dateFilter === "month" && now.getTime() - recordDate.getTime() < 30 * 24 * 60 * 60 * 1000)

    return matchesSearch && matchesValid && matchesDate
  })

  const handleExport = () => {
    toast({
      title: "Export Started",
      description: "Verification records are being exported to CSV",
      variant: "default",
    })
  }

  return (
    <ProtectedRoute adminOnly>
      <div className="container py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold">Verification Records</h1>
          <p className="text-muted-foreground">View and manage all signature verification records</p>
        </div>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Verification History</CardTitle>
              <CardDescription>All signature verification attempts across the system</CardDescription>
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
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>User</TableHead>
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
                      <TableCell className="font-medium">{record.username}</TableCell>
                      <TableCell>{record.algorithmName}</TableCell>
                      <TableCell>{record.curveName}</TableCell>
                      <TableCell>
                        {record.isValid ? (
                          <Badge className="bg-green-500 flex items-center gap-1">
                            <FileCheck className="h-3 w-3" /> Valid
                          </Badge>
                        ) : (
                          <Badge variant="destructive" className="flex items-center gap-1">
                            <FileX className="h-3 w-3" /> Invalid
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell>{format(new Date(record.verificationTime), "MMM d, yyyy HH:mm")}</TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => setSelectedRecord(record)}
                          title="View Details"
                        >
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
                  {selectedRecord.isValid ? (
                    <Badge className="bg-green-500 flex items-center gap-1">
                      <FileCheck className="h-3 w-3" /> Valid
                    </Badge>
                  ) : (
                    <Badge variant="destructive" className="flex items-center gap-1">
                      <FileX className="h-3 w-3" /> Invalid
                    </Badge>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-muted-foreground">User</Label>
                    <p className="font-medium">{selectedRecord.username}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">User ID</Label>
                    <p className="font-medium">{selectedRecord.userId}</p>
                  </div>
                </div>

                <div>
                  <Label className="text-muted-foreground">Document Hash</Label>
                  <p className="font-mono text-xs bg-muted p-2 rounded mt-1">{selectedRecord.documentHash}</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-muted-foreground">Algorithm</Label>
                    <p className="font-medium">{selectedRecord.algorithmName}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Curve</Label>
                    <p className="font-medium">{selectedRecord.curveName}</p>
                  </div>
                </div>

                <div>
                  <Label className="text-muted-foreground">Public Key ID</Label>
                  <p className="font-medium">{selectedRecord.publicKeyId}</p>
                </div>

                <div>
                  <Label className="text-muted-foreground">Verification Time</Label>
                  <p className="font-medium">{format(new Date(selectedRecord.verificationTime), "PPpp")}</p>
                </div>

                {selectedRecord.metadata && (
                  <div>
                    <Label className="text-muted-foreground">Metadata</Label>
                    <div className="bg-muted p-2 rounded mt-1 space-y-1">
                      {Object.entries(selectedRecord.metadata).map(([key, value]) => (
                        <div key={key} className="grid grid-cols-2 text-sm">
                          <span className="font-medium">{key}</span>
                          <span>{value as string}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <DialogFooter>
                <Button variant="outline" onClick={() => setSelectedRecord(null)}>
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
