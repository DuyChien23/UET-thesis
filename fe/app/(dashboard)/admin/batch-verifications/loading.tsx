import { Loader2 } from "lucide-react"

export default function Loading() {
  return (
    <div className="container py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Batch Verifications</h1>
        <p className="text-muted-foreground">View and manage batch signature verification operations</p>
      </div>

      <div className="flex justify-center items-center h-[400px]">
        <Loader2 className="h-12 w-12 animate-spin text-primary" />
      </div>
    </div>
  )
}
