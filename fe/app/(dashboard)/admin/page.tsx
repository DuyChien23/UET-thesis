"use client"

import { ProtectedRoute } from "@/components/protected-route"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Users, Shield, Cpu, BarChart, Settings, Database, History, FileSignature } from "lucide-react"
import Link from "next/link"

export default function AdminDashboardPage() {
  const adminFeatures = [
    {
      title: "User Management",
      description: "Manage system users, their status and roles",
      icon: <Users className="h-6 w-6" />,
      href: "/admin/users",
    },
    {
      title: "Role Management",
      description: "Create and manage roles and permissions",
      icon: <Shield className="h-6 w-6" />,
      href: "/admin/roles",
    },
    {
      title: "Algorithm Management",
      description: "Configure supported algorithms and curves",
      icon: <Cpu className="h-6 w-6" />,
      href: "/admin/algorithms",
    },
    {
      title: "System Status",
      description: "Monitor system health and performance",
      icon: <BarChart className="h-6 w-6" />,
      href: "/admin/system",
    },
    {
      title: "Verification Records",
      description: "View all verification records across users",
      icon: <History className="h-6 w-6" />,
      href: "/admin/verification-records",
    },
    {
      title: "Batch Verifications",
      description: "View and manage batch verification operations",
      icon: <FileSignature className="h-6 w-6" />,
      href: "/admin/batch-verifications",
    },
    {
      title: "Database Configuration",
      description: "Configure database settings and connections",
      icon: <Database className="h-6 w-6" />,
      href: "/admin/database",
    },
    {
      title: "System Configuration",
      description: "Configure system-wide settings and parameters",
      icon: <Settings className="h-6 w-6" />,
      href: "/admin/settings",
    },
  ]

  return (
    <ProtectedRoute adminOnly>
      <div className="container py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Admin Dashboard</h1>
          <p className="text-muted-foreground">Manage and configure the Digital Signature System</p>
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {adminFeatures.map((feature, index) => (
            <Link key={index} href={feature.href}>
              <Card className="h-full transition-all hover:shadow-md">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-lg font-medium">{feature.title}</CardTitle>
                  <div className="rounded-full bg-primary/10 p-2 text-primary">{feature.icon}</div>
                </CardHeader>
                <CardContent>
                  <CardDescription>{feature.description}</CardDescription>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </ProtectedRoute>
  )
}
