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
import { CheckCircle2, XCircle, Upload, Loader2 } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

export default function VerifyPage() {
  const [document, setDocument] = useState("")
  const [signature, setSignature] = useState("")
  const [publicKey, setPublicKey] = useState("")
  const [algorithmId, setAlgorithmId] = useState("")
  const [curveName, setCurveName] = useState("")
  const [isVerifying, setIsVerifying] = useState(false)
  const [verificationResult, setVerificationResult] = useState<{
    isValid: boolean
    verificationId: string
    verificationTime: string
    documentHash: string
  } | null>(null)
  const { toast } = useToast()

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>, setter: (value: string) => void) => {
    const file = e.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (event) => {
      setter(event.target?.result as string)
    }
    reader.readAsText(file)
  }

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsVerifying(true)
    setVerificationResult(null)

    try {
      // This would be a real API call in production
      // const response = await fetch('/api/verify', {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     'Authorization': `Bearer ${localStorage.getItem('token')}`
      //   },
      //   body: JSON.stringify({
      //     document,
      //     signature,
      //     public_key: publicKey,
      //     algorithm_id: algorithmId,
      //     curve_name: curveName
      //   })
      // })

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1500))

      // Simulate response
      const mockResponse = {
        is_valid: Math.random() > 0.3, // 70% chance of success for demo
        verification_id: `ver-${Math.random().toString(36).substring(2, 10)}`,
        verification_time: new Date().toISOString(),
        document_hash: `hash-${Math.random().toString(36).substring(2, 15)}`,
      }

      setVerificationResult({
        isValid: mockResponse.is_valid,
        verificationId: mockResponse.verification_id,
        verificationTime: mockResponse.verification_time,
        documentHash: mockResponse.document_hash,
      })

      toast({
        title: mockResponse.is_valid ? "Verification Successful" : "Verification Failed",
        description: mockResponse.is_valid
          ? "The signature is valid for this document."
          : "The signature could not be verified for this document.",
        variant: mockResponse.is_valid ? "default" : "destructive",
      })
    } catch (error) {
      toast({
        title: "Verification Error",
        description: "An error occurred during verification. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsVerifying(false)
    }
  }

  return (
    <ProtectedRoute>
      <div className="container py-8">
        <div className="mx-auto max-w-3xl">
          <h1 className="mb-6 text-3xl font-bold">Verify Digital Signature</h1>

          <Card>
            <CardHeader>
              <CardTitle>Signature Verification</CardTitle>
              <CardDescription>Verify the authenticity of a document using its digital signature</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleVerify} className="space-y-6">
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
                          onChange={(e) => handleFileUpload(e, setDocument)}
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
                  <Label htmlFor="signature">Signature</Label>
                  <Textarea
                    id="signature"
                    placeholder="Paste signature here"
                    value={signature}
                    onChange={(e) => setSignature(e.target.value)}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="publicKey">Public Key</Label>
                  <Textarea
                    id="publicKey"
                    placeholder="Paste public key here"
                    value={publicKey}
                    onChange={(e) => setPublicKey(e.target.value)}
                    required
                  />
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

                <Button type="submit" className="w-full" disabled={isVerifying}>
                  {isVerifying ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Verifying...
                    </>
                  ) : (
                    "Verify Signature"
                  )}
                </Button>
              </form>
            </CardContent>

            {verificationResult && (
              <CardFooter className="flex flex-col items-start">
                <Alert
                  className={
                    verificationResult.isValid
                      ? "bg-green-50 text-green-800 dark:bg-green-900/20 dark:text-green-400"
                      : "bg-red-50 text-red-800 dark:bg-red-900/20 dark:text-red-400"
                  }
                >
                  {verificationResult.isValid ? <CheckCircle2 className="h-4 w-4" /> : <XCircle className="h-4 w-4" />}
                  <AlertTitle>{verificationResult.isValid ? "Valid Signature" : "Invalid Signature"}</AlertTitle>
                  <AlertDescription>
                    <div className="mt-2 space-y-1 text-sm">
                      <p>Verification ID: {verificationResult.verificationId}</p>
                      <p>Time: {new Date(verificationResult.verificationTime).toLocaleString()}</p>
                      <p>Document Hash: {verificationResult.documentHash}</p>
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
