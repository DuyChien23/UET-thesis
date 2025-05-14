"use client"

import { useAuth } from "@/contexts/auth-context"
import { ProtectedRoute } from "@/components/protected-route"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { FileSignature, Key, History, ShieldCheck, Users } from "lucide-react"
import Link from "next/link"

export default function DashboardPage() {
  const { user, isAdmin } = useAuth()

  const userCards = [
    {
      title: "Sign Document",
      description: "Sign a document using your private key",
      icon: <FileSignature className="h-6 w-6" />,
      href: "/sign",
    },
    {
      title: "Verify Signature",
      description: "Verify a document signature",
      icon: <ShieldCheck className="h-6 w-6" />,
      href: "/verify",
    },
    {
      title: "My Keys",
      description: "Manage your public keys",
      icon: <Key className="h-6 w-6" />,
      href: "/keys",
    },
    {
      title: "Verification History",
      description: "View your verification history",
      icon: <History className="h-6 w-6" />,
      href: "/history",
    },
  ]

  const adminCards = [
    {
      title: "User Management",
      description: "Manage system users",
      icon: <Users className="h-6 w-6" />,
      href: "/admin/users",
    },
  ]

  const cards = isAdmin ? [...userCards, ...adminCards] : userCards

  return (
    <ProtectedRoute>
      <div className="container py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Welcome, {user?.username}</h1>
          <p className="text-muted-foreground">Digital Signature System Dashboard</p>
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {cards.map((card, index) => (
            <Link key={index} href={card.href}>
              <Card className="h-full transition-all hover:shadow-md">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-lg font-medium">{card.title}</CardTitle>
                  <div className="rounded-full bg-primary/10 p-2 text-primary">{card.icon}</div>
                </CardHeader>
                <CardContent>
                  <CardDescription>{card.description}</CardDescription>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </ProtectedRoute>
  )
}
