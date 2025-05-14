"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { ProtectedRoute } from "@/components/protected-route"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { CheckCircle2, XCircle, Upload, Loader2, Copy, Info } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { apiService, type Algorithm, type Curve } from "@/lib/api"
import { getErrorMessage } from "@/lib/errors"

export default function VerifyPage() {
  const [document, setDocument] = useState("")
  const [signature, setSignature] = useState("")
  const [publicKey, setPublicKey] = useState("")
  const [algorithmId, setAlgorithmId] = useState("")
  const [curveName, setCurveName] = useState("")
  const [isVerifying, setIsVerifying] = useState(false)
  const [isLoadingAlgorithms, setIsLoadingAlgorithms] = useState(false)
  const [isLoadingCurves, setIsLoadingCurves] = useState(false)
  const [algorithms, setAlgorithms] = useState<Algorithm[]>([])
  const [curves, setCurves] = useState<Curve[]>([])
  const [error, setError] = useState<string | null>(null)
  const [verificationResult, setVerificationResult] = useState<{
    isValid: boolean;
    documentHash: string;
    publicKey: string;
    curveName: string;
    bitSize: number;
    verificationId?: string;
    verificationTime?: string;
  } | null>(null)
  const { toast } = useToast()

  // Fetch algorithms on component mount
  useEffect(() => {
    const fetchAlgorithms = async () => {
      setIsLoadingAlgorithms(true)
      try {
        const algorithmsData = await apiService.getAlgorithms()
        console.log('Algorithms data from API:', algorithmsData)
        setAlgorithms(algorithmsData || [])
        if (algorithmsData && algorithmsData.length > 0) {
          console.log('Setting initial algorithm ID:', algorithmsData[0].id)
          setAlgorithmId(algorithmsData[0].id)
        }
      } catch (err) {
        setAlgorithms([])
        console.error('Error fetching algorithms:', err)
        toast({
          title: "Error",
          description: "Failed to load algorithms. " + getErrorMessage(err),
          variant: "destructive",
        })
      } finally {
        setIsLoadingAlgorithms(false)
      }
    }

    fetchAlgorithms()
  }, [toast])

  // Fetch curves when algorithm changes
  useEffect(() => {
    if (!algorithmId) return
    console.log('Algorithm ID changed to:', algorithmId)

    const fetchCurves = async () => {
      setIsLoadingCurves(true)
      setCurveName("")
      try {
        const curvesData = await apiService.getCurves(algorithmId)
        console.log('Curves data from API:', curvesData)
        setCurves(curvesData || [])
        if (curvesData && curvesData.length > 0) {
          console.log('Setting initial curve name:', curvesData[0].name)
          setCurveName(curvesData[0].name)
        }
      } catch (err) {
        setCurves([])
        console.error('Error fetching curves:', err)
        toast({
          title: "Error",
          description: "Failed to load curves. " + getErrorMessage(err),
          variant: "destructive",
        })
      } finally {
        setIsLoadingCurves(false)
      }
    }

    fetchCurves()
  }, [algorithmId, toast])
  
  // Log current state for debugging
  useEffect(() => {
    console.log('Current state:', { 
      algorithmId, 
      curveName, 
      algorithmsCount: algorithms.length, 
      curvesCount: curves.length 
    })
  }, [algorithmId, curveName, algorithms, curves])

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
    setError(null)

    try {
      // Call the real API endpoint
      const response = await apiService.verifyDocument(
        document,
        signature,
        publicKey,
        algorithmId,
        curveName
      )
      
      // Use the correct response structure
      setVerificationResult({
        isValid: response.verification,
        documentHash: response.meta_data.document,
        publicKey: response.meta_data.public_key,
        curveName: response.meta_data.curve_name,
        bitSize: response.meta_data.bit_size,
        verificationId: response.meta_data.verification_id,
        verificationTime: response.meta_data.verification_time || new Date().toISOString()
      })

      toast({
        title: response.verification ? "Verification Successful" : "Verification Failed",
        description: response.verification
          ? "The signature is valid for this document."
          : "The signature could not be verified for this document.",
        variant: response.verification ? "default" : "destructive",
      })
    } catch (err) {
      setError(getErrorMessage(err))
      toast({
        title: "Verification Error",
        description: getErrorMessage(err),
        variant: "destructive",
      })
    } finally {
      setIsVerifying(false)
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
          <h1 className="mb-6 text-3xl font-bold">Verify Digital Signature</h1>

          <Card>
            <CardHeader>
              <CardTitle>Signature Verification</CardTitle>
              <CardDescription>Verify the authenticity of a document using its digital signature</CardDescription>
            </CardHeader>
            <CardContent>
              {error && (
                <Alert className="mb-4 bg-destructive/10 text-destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              
              <Alert className="mb-4 bg-blue-50 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400">
                <Info className="h-4 w-4" />
                <AlertDescription>
                  <p className="font-medium">How it works:</p>
                  <ol className="ml-4 mt-2 list-decimal space-y-1 text-sm">
                    <li>Your document will be hashed using the same algorithm that was used to sign it</li>
                    <li>The signature is verified against the document hash using the provided public key</li>
                    <li>The verification happens securely on our servers</li>
                  </ol>
                </AlertDescription>
              </Alert>
            
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
                    <Select 
                      value={algorithmId} 
                      onValueChange={(value) => {
                        console.log('Algorithm selected:', value);
                        setAlgorithmId(value);
                      }}
                      disabled={isLoadingAlgorithms || algorithms.length === 0}
                      required
                    >
                      <SelectTrigger id="algorithm">
                        <SelectValue placeholder={isLoadingAlgorithms ? "Loading..." : "Select algorithm"} />
                      </SelectTrigger>
                      <SelectContent>
                        {algorithms.length > 0 ? (
                          algorithms.map((algorithm) => (
                            <SelectItem key={algorithm.id} value={algorithm.id}>
                              {algorithm.name} ({algorithm.type || 'Unknown'})
                            </SelectItem>
                          ))
                        ) : (
                          <SelectItem disabled value="none">No algorithms available</SelectItem>
                        )}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="curve">Curve</Label>
                    <Select 
                      value={curveName} 
                      onValueChange={(value) => {
                        console.log('Curve selected:', value);
                        setCurveName(value);
                      }}
                      disabled={isLoadingCurves || curves.length === 0 || !algorithmId}
                      required
                    >
                      <SelectTrigger id="curve">
                        <SelectValue placeholder={isLoadingCurves ? "Loading..." : "Select curve"} />
                      </SelectTrigger>
                      <SelectContent>
                        {curves.length > 0 ? (
                          curves.map((curve) => (
                            <SelectItem key={curve.id} value={curve.name}>
                              {curve.name}
                            </SelectItem>
                          ))
                        ) : (
                          <SelectItem disabled value="none">No curves available</SelectItem>
                        )}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <Button type="submit" className="w-full" disabled={isVerifying || !algorithmId || !curveName}>
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
              <CardFooter className="flex flex-col items-start w-full">
                <Alert
                  className={`w-full ${
                    verificationResult.isValid
                      ? "bg-green-50 text-green-800 dark:bg-green-900/20 dark:text-green-400"
                      : "bg-red-50 text-red-800 dark:bg-red-900/20 dark:text-red-400"
                  }`}
                >
                  {verificationResult.isValid ? <CheckCircle2 className="h-4 w-4" /> : <XCircle className="h-4 w-4" />}
                  <AlertTitle className="text-lg font-semibold mb-4">
                    {verificationResult.isValid ? "Valid Signature" : "Invalid Signature"}
                  </AlertTitle>
                  <AlertDescription>
                    <div className="mt-2 space-y-6">
                      <div>
                        <div className="mb-2 flex items-center justify-between">
                          <Label className="text-sm font-semibold">Document Hash</Label>
                          <Button
                            variant="ghost"
                            size="sm"
                            className={`h-6 px-2 ${
                              verificationResult.isValid
                                ? "hover:bg-green-100 dark:hover:bg-green-900/40"
                                : "hover:bg-red-100 dark:hover:bg-red-900/40"
                            }`}
                            onClick={() => copyToClipboard(verificationResult.documentHash, "Document Hash")}
                          >
                            <Copy className="h-3 w-3 mr-1" />
                            <span className="text-xs">Copy</span>
                          </Button>
                        </div>
                        <div 
                          className={`rounded p-3 font-mono text-xs break-all ${
                            verificationResult.isValid
                              ? "bg-white/50 dark:bg-black/20"
                              : "bg-white/50 dark:bg-black/20"
                          }`}
                          title={verificationResult.documentHash}
                        >
                          {verificationResult.documentHash}
                        </div>
                      </div>

                      <div>
                        <div className="mb-2 flex items-center justify-between">
                          <Label className="text-sm font-semibold">Public Key</Label>
                          <Button
                            variant="ghost"
                            size="sm"
                            className={`h-6 px-2 ${
                              verificationResult.isValid
                                ? "hover:bg-green-100 dark:hover:bg-green-900/40"
                                : "hover:bg-red-100 dark:hover:bg-red-900/40"
                            }`}
                            onClick={() => copyToClipboard(verificationResult.publicKey, "Public Key")}
                          >
                            <Copy className="h-3 w-3 mr-1" />
                            <span className="text-xs">Copy</span>
                          </Button>
                        </div>
                        <div 
                          className={`rounded p-3 font-mono text-xs break-all ${
                            verificationResult.isValid
                              ? "bg-white/50 dark:bg-black/20"
                              : "bg-white/50 dark:bg-black/20"
                          }`}
                          title={verificationResult.publicKey}
                        >
                          {verificationResult.publicKey}
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <div className="mb-2 flex items-center justify-between">
                            <Label className="text-sm font-semibold">Curve</Label>
                            <span className="font-mono text-xs">{verificationResult.curveName}</span>
                          </div>
                        </div>

                        <div>
                          <div className="mb-2 flex items-center justify-between">
                            <Label className="text-sm font-semibold">Bit Size</Label>
                            <span className="font-mono text-xs">{verificationResult.bitSize} bits</span>
                          </div>
                        </div>
                      </div>

                      {verificationResult.verificationId && (
                        <div>
                          <div className="mb-2 flex items-center justify-between">
                            <Label className="text-sm font-semibold">Verification ID</Label>
                            <Button
                              variant="ghost"
                              size="sm"
                              className={`h-6 px-2 ${
                                verificationResult.isValid
                                  ? "hover:bg-green-100 dark:hover:bg-green-900/40"
                                  : "hover:bg-red-100 dark:hover:bg-red-900/40"
                              }`}
                              onClick={() => copyToClipboard(verificationResult.verificationId, "Verification ID")}
                            >
                              <Copy className="h-3 w-3 mr-1" />
                              <span className="text-xs">Copy</span>
                            </Button>
                          </div>
                          <div 
                            className={`rounded p-3 font-mono text-xs break-all ${
                              verificationResult.isValid
                                ? "bg-white/50 dark:bg-black/20"
                                : "bg-white/50 dark:bg-black/20"
                            }`}
                            title={verificationResult.verificationId}
                          >
                            {verificationResult.verificationId}
                          </div>
                        </div>
                      )}

                      <div className="mt-4 flex items-center justify-between border-t pt-4 border-opacity-20" 
                        style={{
                          borderColor: verificationResult.isValid ? 'rgb(134, 239, 172)' : 'rgb(252, 165, 165)'
                        }}>
                        <Label className="text-sm font-semibold">Verification Time</Label>
                        <p className="font-mono text-xs">
                          {verificationResult.verificationTime 
                            ? new Date(verificationResult.verificationTime).toLocaleString() 
                            : new Date().toLocaleString()}
                        </p>
                      </div>
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
