"use client"

import type React from "react"

import { useState } from "react"
import { ProtectedRoute } from "@/components/protected-route"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { CheckCircle2, Upload, Loader2, Copy } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

export default function SignPage() {
  const [document, setDocument] = useState("")
  const [privateKey, setPrivateKey] = useState("")
  const [algorithmId, setAlgorithmId] = useState("")
  const [curveName, setCurveName] = useState("")
  const [isSigning, setIsSigning] = useState(false)
  const [signResult, setSignResult] = useState<{
    signature: string
    documentHash: string
    signingId: string
    signingTime: string
    publicKey: string
  } | null>(null)
  const { toast } = useToast()

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (event) => {
      setDocument(event.target?.result as string)
    }
    reader.readAsText(file)
  }

  const handleSign = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSigning(true)
    setSignResult(null)

    try {
      // This would be a real API call in production
      // const response = await fetch('/api/sign', {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     'Authorization': `Bearer ${localStorage.getItem('token')}`
      //   },
      //   body: JSON.stringify({
      //     document,
      //     private_key: privateKey,
      //     algorithm_id: algorithmId,
      //     curve_name: curveName
      //   })
      // })

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1500))

      // Simulate response
      const mockResponse = {
        signature: `sig-${Math.random().toString(36).substring(2, 30)}`,
        document_hash: `hash-${Math.random().toString(36).substring(2, 15)}`,
        signing_id: `sign-${Math.random().toString(36).substring(2, 10)}`,
        signing_time: new Date().toISOString(),
        public_key: `pub-${Math.random().toString(36).substring(2, 30)}`,
      }

      setSignResult({
        signature: mockResponse.signature,
        documentHash: mockResponse.document_hash,
        signingId: mockResponse.signing_id,
        signingTime: mockResponse.signing_time,
        publicKey: mockResponse.public_key,
      })

      toast({
        title: "Document Signed Successfully",
        description: "Your document has been signed. You can now copy the signature.",
        variant: "default",
      })
    } catch (error) {
      toast({
        title: "Signing Error",
        description: "An error occurred during signing. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsSigning(false)
    }
  }

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text)
    toast({
      title: `${label} Copied`,
      description: `The ${label.toLowerCase()} has been copied to your clipboard.`,
      variant: "default",
    })
  }

  return (
    <ProtectedRoute>
      <div className="container py-8">
        <div className="mx-auto max-w-3xl">
          <h1 className="mb-6 text-3xl font-bold">Sign Document</h1>

          <Card>
            <CardHeader>
              <CardTitle>Document Signing</CardTitle>
              <CardDescription>Sign a document using your private key</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSign} className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="document">Document</Label>
                  <div className="grid gap-2">
                    <Textarea
                      id="document"
                      placeholder="Paste document content here"
                      value={document}
                      onChange={(e) => setDocument(e.target.value)}
                      className="min-h-[100px]"
                      required
                    />
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-muted-foreground">Or upload a file:</span>
                      <div className="relative">
                        <Input
                          id="document-file"
                          type="file"
                          onChange={handleFileUpload}
                          className="absolute inset-0 opacity-0"
                        />
                        <Button type="button" variant="outline" size="sm">
                          <Upload className="mr-2 h-4 w-4" />
                          Upload
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="privateKey">Private Key</Label>
                  <Textarea
                    id="privateKey"
                    placeholder="Paste your private key here"
                    value={privateKey}
                    onChange={(e) => setPrivateKey(e.target.value)}
                    required
                  />
                  <p className="text-xs text-muted-foreground">
                    Your private key is never sent to our servers. All signing is done locally in your browser.
                  </p>
                </div>

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="algorithm">Algorithm</Label>
                    <Select value={algorithmId} onValueChange={setAlgorithmId} required>
                      <SelectTrigger id="algorithm">
                        <SelectValue placeholder="Select algorithm" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="algo-1">ECDSA</SelectItem>
                        <SelectItem value="algo-2">RSA</SelectItem>
                        <SelectItem value="algo-3">EdDSA</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="curve">Curve</Label>
                    <Select value={curveName} onValueChange={setCurveName} required>
                      <SelectTrigger id="curve">
                        <SelectValue placeholder="Select curve" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="curve-1">secp256k1</SelectItem>
                        <SelectItem value="curve-2">P-256</SelectItem>
                        <SelectItem value="curve-3">P-384</SelectItem>
                        <SelectItem value="curve-4">P-521</SelectItem>
                        <SelectItem value="curve-5">Ed25519</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <Button type="submit" className="w-full" disabled={isSigning}>
                  {isSigning ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Signing...
                    </>
                  ) : (
                    "Sign Document"
                  )}
                </Button>
              </form>
            </CardContent>

            {signResult && (
              <CardFooter className="flex flex-col items-start">
                <Alert className="bg-green-50 text-green-800 dark:bg-green-900/20 dark:text-green-400">
                  <CheckCircle2 className="h-4 w-4" />
                  <AlertTitle>Document Signed Successfully</AlertTitle>
                  <AlertDescription>
                    <div className="mt-2 space-y-4 text-sm">
                      <div>
                        <div className="mb-1 flex items-center justify-between">
                          <Label>Signature</Label>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 px-2"
                            onClick={() => copyToClipboard(signResult.signature, "Signature")}
                          >
                            <Copy className="h-3 w-3" />
                          </Button>
                        </div>
                        <div className="rounded bg-muted p-2 font-mono text-xs">{signResult.signature}</div>
                      </div>

                      <div>
                        <div className="mb-1 flex items-center justify-between">
                          <Label>Public Key</Label>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 px-2"
                            onClick={() => copyToClipboard(signResult.publicKey, "Public Key")}
                          >
                            <Copy className="h-3 w-3" />
                          </Button>
                        </div>
                        <div className="rounded bg-muted p-2 font-mono text-xs">{signResult.publicKey}</div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label className="text-xs">Document Hash</Label>
                          <div className="rounded bg-muted p-2 font-mono text-xs">{signResult.documentHash}</div>
                        </div>
                        <div>
                          <Label className="text-xs">Signing ID</Label>
                          <div className="rounded bg-muted p-2 font-mono text-xs">{signResult.signingId}</div>
                        </div>
                      </div>

                      <p>Time: {new Date(signResult.signingTime).toLocaleString()}</p>
                    </div>
                  </AlertDescription>
                </Alert>
              </CardFooter>
            )}
          </Card>
        </div>
      </div>
    </ProtectedRoute>
  )
}
