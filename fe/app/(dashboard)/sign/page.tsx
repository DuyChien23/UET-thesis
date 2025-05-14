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
import { CheckCircle2, Upload, Loader2, Copy, Info } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { apiService, type Algorithm, type Curve } from "@/lib/api"
import { getErrorMessage } from "@/lib/errors"

export default function SignPage() {
  const [document, setDocument] = useState("")
  const [privateKey, setPrivateKey] = useState("")
  const [algorithmId, setAlgorithmId] = useState("")
  const [curveName, setCurveName] = useState("")
  const [isSigning, setIsSigning] = useState(false)
  const [isLoadingAlgorithms, setIsLoadingAlgorithms] = useState(false)
  const [isLoadingCurves, setIsLoadingCurves] = useState(false)
  const [algorithms, setAlgorithms] = useState<Algorithm[]>([])
  const [curves, setCurves] = useState<Curve[]>([])
  const [error, setError] = useState<string | null>(null)
  const [signResult, setSignResult] = useState<{
    signature: string
    documentHash: string
    signingId: string
    signingTime: string
    publicKey: string
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
    setError(null)

    try {
      // Call the real API endpoint
      const response = await apiService.signDocument(document, privateKey, curveName)
      
      setSignResult({
        signature: response.signature,
        documentHash: response.document_hash,
        signingId: response.signing_id,
        signingTime: response.signing_time,
        publicKey: response.public_key,
      })

      toast({
        title: "Document Signed Successfully",
        description: "Your document has been signed. You can now copy the signature.",
        variant: "default",
      })
    } catch (err) {
      setError(getErrorMessage(err))
      toast({
        title: "Signing Error",
        description: getErrorMessage(err),
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
                    <li>Your document will be hashed using an algorithm appropriate for the selected curve</li>
                    <li>The document hash is then signed with your private key</li>
                    <li>Your private key is never sent to our servers - the hashing and signing happens locally</li>
                  </ol>
                </AlertDescription>
              </Alert>

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

                <Button type="submit" className="w-full" disabled={isSigning || !algorithmId || !curveName}>
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
              <CardFooter className="flex flex-col items-start w-full">
                <Alert className="w-full bg-green-50 text-green-800 dark:bg-green-900/20 dark:text-green-400">
                  <CheckCircle2 className="h-4 w-4" />
                  <AlertTitle className="text-lg font-semibold mb-4">Document Signed Successfully</AlertTitle>
                  <AlertDescription>
                    <div className="mt-2 space-y-6">
                      <div>
                        <div className="mb-2 flex items-center justify-between">
                          <Label className="text-sm font-semibold">Signature</Label>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 px-2 hover:bg-green-100 dark:hover:bg-green-900/40"
                            onClick={() => copyToClipboard(signResult.signature, "Signature")}
                          >
                            <Copy className="h-3 w-3 mr-1" />
                            <span className="text-xs">Copy</span>
                          </Button>
                        </div>
                        <div 
                          className="rounded bg-white/50 dark:bg-black/20 p-3 font-mono text-xs break-all"
                          title={signResult.signature}
                        >
                          {signResult.signature}
                        </div>
                      </div>

                      <div>
                        <div className="mb-2 flex items-center justify-between">
                          <Label className="text-sm font-semibold">Public Key</Label>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 px-2 hover:bg-green-100 dark:hover:bg-green-900/40"
                            onClick={() => copyToClipboard(signResult.publicKey, "Public Key")}
                          >
                            <Copy className="h-3 w-3 mr-1" />
                            <span className="text-xs">Copy</span>
                          </Button>
                        </div>
                        <div 
                          className="rounded bg-white/50 dark:bg-black/20 p-3 font-mono text-xs break-all"
                          title={signResult.publicKey}
                        >
                          {signResult.publicKey}
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <div className="mb-2 flex items-center justify-between">
                            <Label className="text-sm font-semibold">Document Hash</Label>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-6 px-2 hover:bg-green-100 dark:hover:bg-green-900/40"
                              onClick={() => copyToClipboard(signResult.documentHash, "Document Hash")}
                            >
                              <Copy className="h-3 w-3 mr-1" />
                              <span className="text-xs">Copy</span>
                            </Button>
                          </div>
                          <div 
                            className="rounded bg-white/50 dark:bg-black/20 p-3 font-mono text-xs break-all"
                            title={signResult.documentHash}
                          >
                            {signResult.documentHash}
                          </div>
                        </div>

                        <div>
                          <div className="mb-2 flex items-center justify-between">
                            <Label className="text-sm font-semibold">Signing ID</Label>
                            <Button
                              variant="ghost"
                              size="sm" 
                              className="h-6 px-2 hover:bg-green-100 dark:hover:bg-green-900/40"
                              onClick={() => copyToClipboard(signResult.signingId, "Signing ID")}
                            >
                              <Copy className="h-3 w-3 mr-1" />
                              <span className="text-xs">Copy</span>
                            </Button>
                          </div>
                          <div 
                            className="rounded bg-white/50 dark:bg-black/20 p-3 font-mono text-xs break-all"
                            title={signResult.signingId}
                          >
                            {signResult.signingId}
                          </div>
                        </div>
                      </div>

                      <div className="mt-4 flex items-center justify-between border-t border-green-200 dark:border-green-900/40 pt-4">
                        <Label className="text-sm font-semibold">Signing Time</Label>
                        <p className="font-mono text-xs">
                          {new Date(signResult.signingTime).toLocaleString()}
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
