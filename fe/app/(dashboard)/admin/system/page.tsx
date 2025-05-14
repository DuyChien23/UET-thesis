"use client"

import { useState, useEffect } from "react"
import { ProtectedRoute } from "@/components/protected-route"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Loader2, Database, Server, CheckCircle, XCircle, AlertTriangle } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

// Types
type SystemStatus = {
  status: "ok" | "warning" | "error"
  version: string
  timestamp: string
  database: "ok" | "warning" | "error"
  redis: "ok" | "warning" | "error"
}

type DetailedStatus = {
  database: {
    status: "ok" | "warning" | "error"
    connectionPool: number
    activeConnections: number
    maxConnections: number
    uptime: string
    version: string
  }
  redis: {
    status: "ok" | "warning" | "error"
    memoryUsage: string
    connectedClients: number
    maxClients: number
    uptime: string
    version: string
  }
  algorithms: {
    name: string
    status: "ok" | "warning" | "error"
    message?: string
  }[]
  curves: {
    total: number
    enabled: number
    disabled: number
  }
  system: {
    cpuUsage: number
    memoryUsage: number
    diskUsage: number
    uptime: string
    lastRestart: string
  }
}

type ApiUsage = {
  endpoint: string
  count: number
  averageResponseTime: number
  errorRate: number
  lastHour: {
    time: string
    count: number
  }[]
}

export default function SystemStatusPage() {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [detailedStatus, setDetailedStatus] = useState<DetailedStatus | null>(null)
  const [apiUsage, setApiUsage] = useState<ApiUsage[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const { toast } = useToast()

  useEffect(() => {
    const fetchSystemStatus = async () => {
      setIsLoading(true)
      try {
        // This would be a real API call in production
        // const response = await fetch('/api/system/status', {
        //   headers: {
        //     'Authorization': `Bearer ${localStorage.getItem('token')}`
        //   }
        // })

        // Simulate API call
        await new Promise((resolve) => setTimeout(resolve, 1500))

        // Mock data
        const mockSystemStatus: SystemStatus = {
          status: "ok",
          version: "1.2.3",
          timestamp: new Date().toISOString(),
          database: "ok",
          redis: "ok",
        }

        const mockDetailedStatus: DetailedStatus = {
          database: {
            status: "ok",
            connectionPool: 10,
            activeConnections: 3,
            maxConnections: 20,
            uptime: "5 days, 7 hours",
            version: "PostgreSQL 14.5",
          },
          redis: {
            status: "ok",
            memoryUsage: "45.2 MB",
            connectedClients: 8,
            maxClients: 100,
            uptime: "5 days, 7 hours",
            version: "Redis 6.2.6",
          },
          algorithms: [
            {
              name: "ECDSA",
              status: "ok",
            },
            {
              name: "RSA",
              status: "ok",
            },
            {
              name: "EdDSA",
              status: "warning",
              message: "Performance degradation detected",
            },
          ],
          curves: {
            total: 5,
            enabled: 4,
            disabled: 1,
          },
          system: {
            cpuUsage: 32,
            memoryUsage: 45,
            diskUsage: 28,
            uptime: "5 days, 7 hours",
            lastRestart: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
          },
        }

        const mockApiUsage: ApiUsage[] = [
          {
            endpoint: "/api/verify",
            count: 1245,
            averageResponseTime: 120,
            errorRate: 0.5,
            lastHour: Array(12)
              .fill(0)
              .map((_, i) => ({
                time: new Date(Date.now() - i * 5 * 60 * 1000).toISOString(),
                count: Math.floor(Math.random() * 30) + 10,
              }))
              .reverse(),
          },
          {
            endpoint: "/api/auth/login",
            count: 532,
            averageResponseTime: 85,
            errorRate: 1.2,
            lastHour: Array(12)
              .fill(0)
              .map((_, i) => ({
                time: new Date(Date.now() - i * 5 * 60 * 1000).toISOString(),
                count: Math.floor(Math.random() * 15) + 5,
              }))
              .reverse(),
          },
          {
            endpoint: "/api/users",
            count: 328,
            averageResponseTime: 95,
            errorRate: 0.2,
            lastHour: Array(12)
              .fill(0)
              .map((_, i) => ({
                time: new Date(Date.now() - i * 5 * 60 * 1000).toISOString(),
                count: Math.floor(Math.random() * 10) + 2,
              }))
              .reverse(),
          },
          {
            endpoint: "/api/public-keys",
            count: 876,
            averageResponseTime: 110,
            errorRate: 0.8,
            lastHour: Array(12)
              .fill(0)
              .map((_, i) => ({
                time: new Date(Date.now() - i * 5 * 60 * 1000).toISOString(),
                count: Math.floor(Math.random() * 20) + 8,
              }))
              .reverse(),
          },
          {
            endpoint: "/api/verify/batch",
            count: 215,
            averageResponseTime: 350,
            errorRate: 1.5,
            lastHour: Array(12)
              .fill(0)
              .map((_, i) => ({
                time: new Date(Date.now() - i * 5 * 60 * 1000).toISOString(),
                count: Math.floor(Math.random() * 8) + 1,
              }))
              .reverse(),
          },
        ]

        setSystemStatus(mockSystemStatus)
        setDetailedStatus(mockDetailedStatus)
        setApiUsage(mockApiUsage)
      } catch (error) {
        toast({
          title: "Error",
          description: "Failed to load system status",
          variant: "destructive",
        })
      } finally {
        setIsLoading(false)
      }
    }

    fetchSystemStatus()

    // Set up polling for real-time updates
    const intervalId = setInterval(fetchSystemStatus, 30000) // Update every 30 seconds

    return () => clearInterval(intervalId)
  }, [toast])

  const getStatusBadge = (status: "ok" | "warning" | "error") => {
    switch (status) {
      case "ok":
        return (
          <Badge className="bg-green-500 flex items-center gap-1">
            <CheckCircle className="h-3 w-3" /> Operational
          </Badge>
        )
      case "warning":
        return (
          <Badge variant="outline" className="text-amber-500 border-amber-500 flex items-center gap-1">
            <AlertTriangle className="h-3 w-3" /> Degraded
          </Badge>
        )
      case "error":
        return (
          <Badge variant="destructive" className="flex items-center gap-1">
            <XCircle className="h-3 w-3" /> Down
          </Badge>
        )
      default:
        return <Badge variant="outline">{status}</Badge>
    }
  }

  if (isLoading) {
    return (
      <ProtectedRoute adminOnly>
        <div className="container py-8">
          <div className="mb-6">
            <h1 className="text-3xl font-bold">System Status</h1>
            <p className="text-muted-foreground">Monitor system health and performance</p>
          </div>

          <div className="flex justify-center items-center h-[400px]">
            <Loader2 className="h-12 w-12 animate-spin text-primary" />
          </div>
        </div>
      </ProtectedRoute>
    )
  }

  return (
    <ProtectedRoute adminOnly>
      <div className="container py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold">System Status</h1>
          <p className="text-muted-foreground">Monitor system health and performance</p>
        </div>

        {/* System Overview */}
        <div className="grid gap-6 md:grid-cols-3 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">System Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="text-2xl font-bold">
                  {systemStatus?.status === "ok"
                    ? "Healthy"
                    : systemStatus?.status === "warning"
                      ? "Degraded"
                      : "Error"}
                </div>
                {systemStatus && getStatusBadge(systemStatus.status)}
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                Last updated: {systemStatus ? new Date(systemStatus.timestamp).toLocaleString() : "N/A"}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Version</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{systemStatus?.version || "N/A"}</div>
              <p className="text-xs text-muted-foreground mt-2">
                System uptime: {detailedStatus?.system.uptime || "N/A"}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">API Requests (24h)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {apiUsage.reduce((sum, api) => sum + api.count, 0).toLocaleString()}
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                Avg. response time:{" "}
                {Math.round(apiUsage.reduce((sum, api) => sum + api.averageResponseTime, 0) / apiUsage.length)}ms
              </p>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="components" className="w-full">
          <TabsList className="mb-4">
            <TabsTrigger value="components">System Components</TabsTrigger>
            <TabsTrigger value="resources">Resource Usage</TabsTrigger>
            <TabsTrigger value="api">API Usage</TabsTrigger>
          </TabsList>

          {/* System Components Tab */}
          <TabsContent value="components">
            <div className="grid gap-6 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Database className="h-5 w-5" /> Database
                  </CardTitle>
                  <CardDescription>PostgreSQL database status</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">Status</span>
                      {detailedStatus && getStatusBadge(detailedStatus.database.status)}
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span>Connection Pool</span>
                        <span>
                          {detailedStatus?.database.activeConnections || 0} /{" "}
                          {detailedStatus?.database.connectionPool || 0}
                        </span>
                      </div>
                      <Progress
                        value={
                          detailedStatus
                            ? (detailedStatus.database.activeConnections / detailedStatus.database.connectionPool) * 100
                            : 0
                        }
                        className="h-2"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Version</span>
                        <p>{detailedStatus?.database.version || "N/A"}</p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Uptime</span>
                        <p>{detailedStatus?.database.uptime || "N/A"}</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Server className="h-5 w-5" /> Redis
                  </CardTitle>
                  <CardDescription>Redis cache status</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">Status</span>
                      {detailedStatus && getStatusBadge(detailedStatus.redis.status)}
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span>Connected Clients</span>
                        <span>
                          {detailedStatus?.redis.connectedClients || 0} / {detailedStatus?.redis.maxClients || 0}
                        </span>
                      </div>
                      <Progress
                        value={
                          detailedStatus
                            ? (detailedStatus.redis.connectedClients / detailedStatus.redis.maxClients) * 100
                            : 0
                        }
                        className="h-2"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Memory Usage</span>
                        <p>{detailedStatus?.redis.memoryUsage || "N/A"}</p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Version</span>
                        <p>{detailedStatus?.redis.version || "N/A"}</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Algorithms</CardTitle>
                  <CardDescription>Cryptographic algorithm status</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {detailedStatus?.algorithms.map((algorithm) => (
                      <div key={algorithm.name} className="flex items-center justify-between">
                        <span className="font-medium">{algorithm.name}</span>
                        <div className="flex items-center gap-2">
                          {getStatusBadge(algorithm.status)}
                          {algorithm.message && (
                            <span className="text-xs text-muted-foreground">{algorithm.message}</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Curves</CardTitle>
                  <CardDescription>Elliptic curve configuration</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-3 gap-4">
                      <div className="flex flex-col items-center justify-center p-4 bg-muted rounded-lg">
                        <span className="text-2xl font-bold">{detailedStatus?.curves.total || 0}</span>
                        <span className="text-sm text-muted-foreground">Total</span>
                      </div>
                      <div className="flex flex-col items-center justify-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                        <span className="text-2xl font-bold text-green-600 dark:text-green-400">
                          {detailedStatus?.curves.enabled || 0}
                        </span>
                        <span className="text-sm text-green-600 dark:text-green-400">Enabled</span>
                      </div>
                      <div className="flex flex-col items-center justify-center p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
                        <span className="text-2xl font-bold text-amber-600 dark:text-amber-400">
                          {detailedStatus?.curves.disabled || 0}
                        </span>
                        <span className="text-sm text-amber-600 dark:text-amber-400">Disabled</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Resource Usage Tab */}
          <TabsContent value="resources">
            <div className="grid gap-6 md:grid-cols-3">
              <Card>
                <CardHeader>
                  <CardTitle>CPU Usage</CardTitle>
                  <CardDescription>Current CPU utilization</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-2xl font-bold">{detailedStatus?.system.cpuUsage || 0}%</span>
                      <Badge
                        variant={
                          detailedStatus && detailedStatus.system.cpuUsage > 80
                            ? "destructive"
                            : detailedStatus && detailedStatus.system.cpuUsage > 60
                              ? "outline"
                              : "default"
                        }
                        className={
                          detailedStatus && detailedStatus.system.cpuUsage > 80
                            ? ""
                            : detailedStatus && detailedStatus.system.cpuUsage > 60
                              ? "text-amber-500 border-amber-500"
                              : "bg-green-500"
                        }
                      >
                        {detailedStatus && detailedStatus.system.cpuUsage > 80
                          ? "High"
                          : detailedStatus && detailedStatus.system.cpuUsage > 60
                            ? "Moderate"
                            : "Normal"}
                      </Badge>
                    </div>
                    <div className="space-y-2">
                      <Progress value={detailedStatus?.system.cpuUsage || 0} className="h-2" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Memory Usage</CardTitle>
                  <CardDescription>Current memory utilization</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-2xl font-bold">{detailedStatus?.system.memoryUsage || 0}%</span>
                      <Badge
                        variant={
                          detailedStatus && detailedStatus.system.memoryUsage > 80
                            ? "destructive"
                            : detailedStatus && detailedStatus.system.memoryUsage > 60
                              ? "outline"
                              : "default"
                        }
                        className={
                          detailedStatus && detailedStatus.system.memoryUsage > 80
                            ? ""
                            : detailedStatus && detailedStatus.system.memoryUsage > 60
                              ? "text-amber-500 border-amber-500"
                              : "bg-green-500"
                        }
                      >
                        {detailedStatus && detailedStatus.system.memoryUsage > 80
                          ? "High"
                          : detailedStatus && detailedStatus.system.memoryUsage > 60
                            ? "Moderate"
                            : "Normal"}
                      </Badge>
                    </div>
                    <div className="space-y-2">
                      <Progress value={detailedStatus?.system.memoryUsage || 0} className="h-2" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Disk Usage</CardTitle>
                  <CardDescription>Current disk utilization</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-2xl font-bold">{detailedStatus?.system.diskUsage || 0}%</span>
                      <Badge
                        variant={
                          detailedStatus && detailedStatus.system.diskUsage > 80
                            ? "destructive"
                            : detailedStatus && detailedStatus.system.diskUsage > 60
                              ? "outline"
                              : "default"
                        }
                        className={
                          detailedStatus && detailedStatus.system.diskUsage > 80
                            ? ""
                            : detailedStatus && detailedStatus.system.diskUsage > 60
                              ? "text-amber-500 border-amber-500"
                              : "bg-green-500"
                        }
                      >
                        {detailedStatus && detailedStatus.system.diskUsage > 80
                          ? "High"
                          : detailedStatus && detailedStatus.system.diskUsage > 60
                            ? "Moderate"
                            : "Normal"}
                      </Badge>
                    </div>
                    <div className="space-y-2">
                      <Progress value={detailedStatus?.system.diskUsage || 0} className="h-2" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card className="mt-6">
              <CardHeader>
                <CardTitle>System Information</CardTitle>
                <CardDescription>General system information and statistics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-lg font-medium mb-2">Uptime</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">System Uptime</span>
                        <span>{detailedStatus?.system.uptime || "N/A"}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Last Restart</span>
                        <span>
                          {detailedStatus?.system.lastRestart
                            ? new Date(detailedStatus.system.lastRestart).toLocaleString()
                            : "N/A"}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg font-medium mb-2">Services</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Database</span>
                        <span>{detailedStatus?.database.status === "ok" ? "Running" : "Issues Detected"}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Redis</span>
                        <span>{detailedStatus?.redis.status === "ok" ? "Running" : "Issues Detected"}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">API Server</span>
                        <span>{systemStatus?.status === "ok" ? "Running" : "Issues Detected"}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* API Usage Tab */}
          <TabsContent value="api">
            <Card>
              <CardHeader>
                <CardTitle>API Endpoints</CardTitle>
                <CardDescription>Usage statistics for API endpoints</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Endpoint</TableHead>
                      <TableHead className="text-right">Requests (24h)</TableHead>
                      <TableHead className="text-right">Avg. Response Time</TableHead>
                      <TableHead className="text-right">Error Rate</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {apiUsage.map((api) => (
                      <TableRow key={api.endpoint}>
                        <TableCell className="font-medium">{api.endpoint}</TableCell>
                        <TableCell className="text-right">{api.count.toLocaleString()}</TableCell>
                        <TableCell className="text-right">{api.averageResponseTime}ms</TableCell>
                        <TableCell className="text-right">
                          <span
                            className={
                              api.errorRate > 2
                                ? "text-destructive"
                                : api.errorRate > 1
                                  ? "text-amber-500"
                                  : "text-green-500"
                            }
                          >
                            {api.errorRate}%
                          </span>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>

            <div className="grid gap-6 md:grid-cols-2 mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>Rate Limiting</CardTitle>
                  <CardDescription>Current rate limiting statistics</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">IP-based Rate Limiting</span>
                      <Badge className="bg-green-500">Active</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="font-medium">User-based Rate Limiting</span>
                      <Badge className="bg-green-500">Active</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="font-medium">Endpoint-based Rate Limiting</span>
                      <Badge className="bg-green-500">Active</Badge>
                    </div>
                    <div className="pt-2">
                      <h4 className="text-sm font-medium mb-2">Blocked IPs (Last 24h)</h4>
                      <div className="text-2xl font-bold">12</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>API Health</CardTitle>
                  <CardDescription>Overall API health metrics</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">Average Response Time</span>
                        <span
                          className={
                            Math.round(
                              apiUsage.reduce((sum, api) => sum + api.averageResponseTime, 0) / apiUsage.length,
                            ) > 200
                              ? "text-amber-500"
                              : "text-green-500"
                          }
                        >
                          {Math.round(
                            apiUsage.reduce((sum, api) => sum + api.averageResponseTime, 0) / apiUsage.length,
                          )}
                          ms
                        </span>
                      </div>
                      <Progress
                        value={Math.min(
                          (Math.round(
                            apiUsage.reduce((sum, api) => sum + api.averageResponseTime, 0) / apiUsage.length,
                          ) /
                            500) *
                            100,
                          100,
                        )}
                        className="h-2"
                      />
                    </div>

                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">Average Error Rate</span>
                        <span
                          className={
                            apiUsage.reduce((sum, api) => sum + api.errorRate, 0) / apiUsage.length > 1
                              ? "text-amber-500"
                              : "text-green-500"
                          }
                        >
                          {(apiUsage.reduce((sum, api) => sum + api.errorRate, 0) / apiUsage.length).toFixed(2)}%
                        </span>
                      </div>
                      <Progress
                        value={Math.min(
                          (apiUsage.reduce((sum, api) => sum + api.errorRate, 0) / apiUsage.length / 5) * 100,
                          100,
                        )}
                        className="h-2"
                      />
                    </div>

                    <div className="pt-2">
                      <h4 className="text-sm font-medium mb-2">Total Requests (24h)</h4>
                      <div className="text-2xl font-bold">
                        {apiUsage.reduce((sum, api) => sum + api.count, 0).toLocaleString()}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </ProtectedRoute>
  )
}
