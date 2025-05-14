"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { useAuth } from "@/contexts/auth-context"

export function MainNav() {
  const pathname = usePathname()
  const { isAdmin } = useAuth()

  const routes = [
    {
      href: "/dashboard",
      label: "Dashboard",
      active: pathname === "/dashboard",
    },
    {
      href: "/verify",
      label: "Verify Signature",
      active: pathname === "/verify",
    },
    {
      href: "/sign",
      label: "Sign Document",
      active: pathname === "/sign",
    },
    {
      href: "/keys",
      label: "My Keys",
      active: pathname === "/keys",
    },
    {
      href: "/history",
      label: "History",
      active: pathname === "/history",
    },
  ]

  // Admin-only routes
  const adminRoutes = [
    {
      href: "/admin",
      label: "Admin Dashboard",
      active: pathname === "/admin",
    },
    {
      href: "/admin/users",
      label: "Users",
      active: pathname === "/admin/users",
    },
    {
      href: "/admin/roles",
      label: "Roles",
      active: pathname === "/admin/roles",
    },
    {
      href: "/admin/algorithms",
      label: "Algorithms",
      active: pathname === "/admin/algorithms",
    },
    {
      href: "/admin/system",
      label: "System",
      active: pathname === "/admin/system",
    },
  ]

  const allRoutes = isAdmin ? [...routes, ...adminRoutes] : routes

  return (
    <nav className="flex items-center space-x-4 lg:space-x-6">
      {allRoutes.map((route) => (
        <Link
          key={route.href}
          href={route.href}
          className={cn(
            "text-sm font-medium transition-colors hover:text-primary",
            route.active ? "text-primary" : "text-muted-foreground",
          )}
        >
          {route.label}
        </Link>
      ))}
    </nav>
  )
}
