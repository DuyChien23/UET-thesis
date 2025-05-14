import { Loader2 } from "lucide-react"

export default function Loading() {
  return (
    <div className="container py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">System Status</h1>
        <p className="text-muted-foreground">Monitor system health and performance</p>
      </div>

      <div className="flex justify-center items-center h-[400px]">
        <Loader2 className="h-12 w-12 animate-spin text-primary" />
      </div>
    </div>
  )
}
